from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database import engine
from core import models
from api import admin_catalog, sales # <-- 1. Agregamos 'sales' aquí

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Repostería Artesanal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos ambas rutas
app.include_router(admin_catalog.router)
app.include_router(sales.router) # <-- 2. Registramos el router de ventas

@app.get("/")
def root():
    return {"message": "API de Repostería Funcionando 🍰"}