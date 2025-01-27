from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException

from app import models, schema
from app.database import engine, session
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = session()
    try : 
        yield db
    finally:
        db.close()

@app.get("/")
def get_app():
    return {"message": "Hello World"}

#get product list
@app.get("/product/list")
def get_product_list(pageNo:int=1, db: Session = Depends(get_db)):
    skip = 0
    limit = 10
    if pageNo > 1:
        skip = (pageNo - 1) * limit
    total_products = db.query(models.Product).count()
    products = db.query(models.Product).offset(skip).limit(limit).all()
    total_pages = (total_products + limit - 1) // limit
    return {"products": products, "total_products": total_products, "total_pages": total_pages}

# add new product
@app.post("/product/add", response_model=schema.ProductResponse)
def add_product(product: schema.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.model_dump())
    new_product.created_date = datetime.now()
    new_product.updated_date = datetime.now()
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return  new_product


@app.get("/product/{pid}/info")
def get_product_info(pid: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == pid).first()
    return {"product": product}


@app.put("/product/{pid}/update", response_model=schema.ProductResponse)
def update_product(pid: int, product: schema.ProductUpdate, db: Session = Depends(get_db)):
    product_exist = db.query(models.Product).filter(models.Product.id == pid).first()
    
    if not product_exist:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.model_dump().items():
        setattr(product_exist, key, value)
    
    product_exist.updated_date = datetime.now()
    db.commit()
    db.refresh(product_exist)
    
    return product_exist