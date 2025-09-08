import 'package:flutter/foundation.dart';
import '../models/user.dart';
import '../models/login_request.dart';
import '../models/register_request.dart';
import '../models/register_response.dart';
import '../services/auth_service.dart';

enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

class AuthProvider with ChangeNotifier {
  AuthStatus _status = AuthStatus.initial;
  User? _user;
  String? _errorMessage;

  AuthStatus get status => _status;
  User? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _status == AuthStatus.authenticated && _user != null;
  bool get isLoading => _status == AuthStatus.loading;

  AuthProvider() {
    _initializeAuth();
  }

  // Inicializar estado de autenticación
  Future<void> _initializeAuth() async {
    _setStatus(AuthStatus.loading);
    
    try {
      final isAuth = await AuthService.isAuthenticated();
      if (isAuth) {
        final user = await AuthService.getStoredUser();
        if (user != null) {
          _user = user;
          _setStatus(AuthStatus.authenticated);
        } else {
          _setStatus(AuthStatus.unauthenticated);
        }
      } else {
        _setStatus(AuthStatus.unauthenticated);
      }
    } catch (e) {
      _setError('Error al inicializar autenticación: $e');
    }
  }

  // Login
  Future<bool> login(String email, String password) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final request = LoginRequest(email: email, password: password);
      await AuthService.login(request);
      
      // Obtener información del usuario desde el backend
      final user = await AuthService.getCurrentUserFromBackend();
      if (user != null) {
        _user = user;
        _setStatus(AuthStatus.authenticated);
        return true;
      } else {
        _setError('No se pudo obtener información del usuario');
        return false;
      }
    } catch (e) {
      _setError('Error en el login: $e');
      return false;
    }
  }

  // Registro
  Future<RegisterResponse?> register(String fullName, String email, String password, {String? phone}) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final request = RegisterRequest(
        fullName: fullName,
        email: email,
        password: password,
        phone: phone ?? '',
      );
      final registerResponse = await AuthService.register(request);
      
      // El registro no devuelve token, solo éxito
      _setStatus(AuthStatus.unauthenticated);
      return registerResponse;
    } catch (e) {
      _setError('Error en el registro: $e');
      return null;
    }
  }

  // Logout
  Future<void> logout() async {
    _setStatus(AuthStatus.loading);
    
    try {
      await AuthService.logout();
    } catch (e) {
      // Ignorar errores de logout
      print('Error en logout: $e');
    } finally {
      _user = null;
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  // Verificar salud del backend
  Future<Map<String, dynamic>?> healthCheck() async {
    try {
      return await AuthService.healthCheck();
    } catch (e) {
      print('Error en health check: $e');
      return null;
    }
  }

  // Actualizar información del usuario
  Future<void> updateUser() async {
    try {
      final user = await AuthService.getCurrentUser();
      if (user != null) {
        _user = user;
        notifyListeners();
      }
    } catch (e) {
      print('Error al actualizar usuario: $e');
    }
  }

  // Solicitar restablecimiento de contraseña
  Future<Map<String, dynamic>?> forgotPassword(String email) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final response = await AuthService.forgotPassword(email);
      _setStatus(AuthStatus.unauthenticated);
      return response;
    } catch (e) {
      _setError('Error al solicitar restablecimiento: $e');
      return null;
    }
  }

  // Restablecer contraseña
  Future<Map<String, dynamic>?> resetPassword({
    required String email,
    required String resetCode,
    required String newPassword,
  }) async {
    _setStatus(AuthStatus.loading);
    _clearError();

    try {
      final response = await AuthService.resetPassword(
        email: email,
        resetCode: resetCode,
        newPassword: newPassword,
      );
      _setStatus(AuthStatus.unauthenticated);
      return response;
    } catch (e) {
      _setError('Error al restablecer contraseña: $e');
      return null;
    }
  }

  // Limpiar error
  void clearError() {
    _clearError();
  }

  // Métodos privados
  void _setStatus(AuthStatus status) {
    _status = status;
    notifyListeners();
  }

  void _setError(String error) {
    _errorMessage = error;
    _status = AuthStatus.error;
    notifyListeners();
  }

  void _clearError() {
    _errorMessage = null;
    if (_status == AuthStatus.error) {
      _status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }
}
