"""
Middleware de Rate Limiting
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time
from core.config import settings

class RateLimiter:
    def __init__(self):
        # Diccionario para almacenar requests por IP
        self.requests: Dict[str, list] = {}
        # Limpiar datos antiguos cada 5 minutos
        self.last_cleanup = time.time()
    
    def is_allowed(self, ip: str, limit: int = None, window: int = 60) -> Tuple[bool, int, int]:
        """
        Verifica si una IP puede hacer más requests
        
        Args:
            ip: IP del cliente
            limit: Número máximo de requests (por defecto desde settings)
            window: Ventana de tiempo en segundos (por defecto 60)
        
        Returns:
            Tuple[is_allowed, remaining_requests, reset_time]
        """
        if limit is None:
            limit = settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        
        current_time = time.time()
        
        # Limpiar datos antiguos periódicamente
        if current_time - self.last_cleanup > 300:  # 5 minutos
            self._cleanup_old_requests(current_time, window)
            self.last_cleanup = current_time
        
        # Obtener requests de esta IP
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Filtrar requests dentro de la ventana de tiempo
        cutoff_time = current_time - window
        self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > cutoff_time]
        
        # Verificar si puede hacer más requests
        if len(self.requests[ip]) >= limit:
            # Calcular cuándo se puede hacer el siguiente request
            oldest_request = min(self.requests[ip])
            reset_time = int(oldest_request + window)
            remaining = 0
            return False, remaining, reset_time
        
        # Agregar este request
        self.requests[ip].append(current_time)
        remaining = limit - len(self.requests[ip])
        reset_time = int(current_time + window)
        
        return True, remaining, reset_time
    
    def _cleanup_old_requests(self, current_time: float, window: int):
        """Limpia requests antiguos de todas las IPs"""
        cutoff_time = current_time - window
        for ip in list(self.requests.keys()):
            self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > cutoff_time]
            if not self.requests[ip]:
                del self.requests[ip]

# Instancia global del rate limiter
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting
    """
    # Obtener IP del cliente
    client_ip = request.client.host if request.client else "unknown"
    
    # Verificar rate limit
    is_allowed, remaining, reset_time = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        # Calcular segundos hasta reset
        seconds_until_reset = reset_time - int(time.time())
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Rate limit exceeded. Try again in {seconds_until_reset} seconds.",
                "limit": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
                "remaining": remaining,
                "reset_time": reset_time,
                "retry_after": seconds_until_reset
            },
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(seconds_until_reset)
            }
        )
    
    # Agregar headers de rate limit a la respuesta
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    return response

def check_rate_limit(ip: str, limit: int = None, window: int = 60):
    """
    Función para verificar rate limit en endpoints específicos
    """
    is_allowed, remaining, reset_time = rate_limiter.is_allowed(ip, limit, window)
    
    if not is_allowed:
        seconds_until_reset = reset_time - int(time.time())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {seconds_until_reset} seconds.",
            headers={
                "X-RateLimit-Limit": str(limit or settings.RATE_LIMIT_REQUESTS_PER_MINUTE),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(seconds_until_reset)
            }
        )
    
    return remaining, reset_time
