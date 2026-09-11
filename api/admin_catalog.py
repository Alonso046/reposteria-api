from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import requests

from core import models, schemas
from infrastructure.database import get_db

router = APIRouter(prefix="/admin", tags=["Administración de Catálogo"])

# --- AQUÍ VA TU LLAVE DE IMGBB ---
IMGBB_API_KEY = "a6b39b81f0070f4e65af3ec37983b37c"

# --- ENDPOINTS PARA CATEGORÍAS ---

@router.post("/categories/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    new_category = models.Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# --- ENDPOINTS PARA PRODUCTOS ---

@router.post("/products/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products/", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualiza solo los campos que vengan en la petición (exclude_unset=True)
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
        
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Producto eliminado exitosamente"}


# --- ENDPOINT PARA SUBIR IMÁGENES A IMGBB ---
@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 1. Leer el archivo que viene desde el frontend
        contents = await file.read()
        
        # 2. Enviar la imagen a la API de ImgBB
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": (file.filename, contents, file.content_type)}
        )
        
        # 3. Procesar la respuesta
        if response.status_code == 200:
            data = response.json()
            return {"image_url": data["data"]["url"]}
        else:
            raise HTTPException(status_code=400, detail="Error al subir la imagen a ImgBB")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))