from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import urllib.parse

from core import models, schemas
from infrastructure.database import get_db

router = APIRouter(prefix="/sales", tags=["Ventas y Pedidos"])

# REEMPLAZA ESTE NÚMERO POR EL DE TU MAMÁ
# Debe incluir el código de país (56 para Chile) pero sin el signo +
WHATSAPP_NUMBER = "56957009769" 

@router.post("/orders/", status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    total_amount = 0
    
    # 1. Iniciar el texto formateado para WhatsApp
    wa_text = "NUEVO ENCARGO WEB 🧁\n\n"
    wa_text += f"👤 Cliente: {order_data.customer_name}\n"
    # Formatear la fecha para que se vea legible (DD/MM/YYYY)
    wa_text += f"📅 Fecha de Entrega: {order_data.delivery_date.strftime('%d/%m/%Y')}\n\n"
    wa_text += "🛍️ DETALLE DEL PEDIDO:\n"

    # 2. Buscar si el cliente ya existe, o crearlo
    db_customer = db.query(models.Customer).filter(models.Customer.phone == order_data.customer_phone).first()
    if not db_customer:
        db_customer = models.Customer(name=order_data.customer_name, phone=order_data.customer_phone)
        db.add(db_customer)
        db.flush() # Asigna un ID al cliente sin cerrar la transacción
        
    # 3. Crear la orden principal
    new_order = models.Order(
        customer_id=db_customer.id,
        delivery_date=order_data.delivery_date,
        notes=order_data.notes,
        status="PENDING",
        total_amount=0 # Lo calcularemos en el siguiente paso
    )
    db.add(new_order)
    db.flush()

    # 4. Procesar cada producto del carrito
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto con ID {item.product_id} no existe")
        
        # Calcular precio base x cantidad
        subtotal = product.base_price * item.quantity
        total_amount += subtotal
        
        # Guardar en base de datos
        new_item = models.OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            size_option=item.size_option,
            dedication_text=item.dedication_text,
            unit_price=product.base_price,
            subtotal=subtotal
        )
        db.add(new_item)
        
        # Agregar al mensaje de WhatsApp
        wa_text += f"- {item.quantity}x {product.name}"
        if item.size_option:
            wa_text += f" ({item.size_option})"
        wa_text += f" [${subtotal}]\n"
        
        if item.dedication_text:
            wa_text += f"  📝 Dedicatoria: \"{item.dedication_text}\"\n"
            
    # 5. Finalizar cálculos y guardar todo
    new_order.total_amount = total_amount
    db.commit()
    
    # 6. Completar el mensaje
    wa_text += f"\n💵 Total a pagar: ${total_amount}\n"
    if order_data.notes:
        wa_text += f"\n📌 Notas del cliente: {order_data.notes}\n"

    # 7. Codificar el mensaje para que funcione en una URL (cambia espacios por %20, etc.)
    encoded_msg = urllib.parse.quote(wa_text)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"

    # Retornamos la URL al frontend para que haga la redirección automática
    return {
        "message": "Pedido registrado exitosamente",
        "order_id": new_order.id,
        "whatsapp_redirect_url": whatsapp_url
    }


@router.get("/orders/")
def get_all_orders(db: Session = Depends(get_db)):
    # Traemos todos los pedidos ordenados del más nuevo al más antiguo
    orders = db.query(models.Order).order_by(models.Order.id.desc()).all()
    
    result = []
    for order in orders:
        # Buscamos los datos del cliente que hizo este pedido
        customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
        
        result.append({
            "id": order.id,
            "customer_name": customer.name if customer else "Desconocido",
            "customer_phone": customer.phone if customer else "Sin teléfono",
            "delivery_date": order.delivery_date.strftime("%d/%m/%Y"),
            "total_amount": order.total_amount,
            "notes": order.notes
        })
        
    return result