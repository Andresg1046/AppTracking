#!/usr/bin/env python3
"""
Script para crear datos de prueba para el WebSocket
"""
from core.database import SessionLocal
from features.ecommerce.models import Order
from features.tracking.models import Driver, DeliveryTracking
from features.users.models import User
from features.vehicles.models import Vehicle
from features.roles.models import Role
from features.auth.models import UserSession
from datetime import datetime

def create_test_data():
    db = SessionLocal()
    try:
        # Crear orden de prueba
        test_order = Order(
            woocommerce_order_id=12345,
            customer_email='test@example.com',
            customer_name='Juan Pérez',
            customer_phone='555-1234',
            shipping_address={
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'address_1': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'postcode': '10001'
            },
            subtotal=50.00,
            tax_total=5.00,
            shipping_total=10.00,
            total=65.00,
            status='processing',
            payment_status='paid'
        )
        db.add(test_order)
        db.commit()
        print(f'✅ Orden creada: ID {test_order.id}')
        
        # Buscar conductor existente
        driver = db.query(Driver).first()
        if driver:
            # Crear tracking de entrega
            delivery = DeliveryTracking(
                order_id=test_order.id,
                driver_id=driver.id,
                status='assigned',
                priority='normal',
                delivery_address=test_order.shipping_address,
                delivery_coordinates={'lat': 40.7128, 'lng': -74.0060},
                estimated_arrival=datetime.utcnow(),
                customer_name=test_order.customer_name,
                customer_phone=test_order.customer_phone
            )
            db.add(delivery)
            db.commit()
            print(f'✅ Entrega asignada: ID {delivery.id}')
            print(f'✅ Conductor asignado: ID {driver.id}')
        else:
            print('❌ No hay conductores disponibles')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
