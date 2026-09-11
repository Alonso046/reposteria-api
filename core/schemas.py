from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- ESQUEMAS DE CATEGORÍA ---
class CategoryBase(BaseModel):
    name: str
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- ESQUEMAS DE PRODUCTO (CATÁLOGO) ---
class ProductBase(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    base_price: int
    is_available: bool = True
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

# Para cuando actualicemos precio o stock desde el panel de tu mamá
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[int] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# --- ESQUEMAS DE VENTAS (CARRITO Y CHECKOUT) ---
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    size_option: Optional[str] = None # Ej: "15 personas"
    dedication_text: Optional[str] = None # Ej: "Feliz Cumpleaños"

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_date: date # Fecha para agendar la entrega
    notes: Optional[str] = None
    items: List[OrderItemCreate]