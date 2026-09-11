from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from infrastructure.database import Base

# --- CONTEXTO CATÁLOGO ---
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False) # Ej: "Tortas", "Postres", "Cóctel Salado"
    is_active = Column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=True) # Para detallar rellenos y bizcochos
    base_price = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)
    
    category = relationship("Category")

# --- CONTEXTO VENTAS (PEDIDOS AGENDADOS) ---
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), unique=True)
    
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String(50), default="PENDING")
    delivery_date = Column(Date, nullable=False) # CRÍTICO: Fecha agendada de entrega
    total_amount = Column(Integer, nullable=False, default=0)
    notes = Column(String, nullable=True)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    
    # Nuevos campos de personalización
    size_option = Column(String(50), nullable=True) # Ej: "15 personas", "30 personas"
    dedication_text = Column(String(100), nullable=True) # Ej: "Feliz Cumpleaños Juan"
    
    unit_price = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")