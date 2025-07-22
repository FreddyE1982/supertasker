from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_cat = models.Category(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@app.get("/categories", response_model=list[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.post('/appointments', response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    if appointment.category_id is not None:
        cat = db.query(models.Category).filter(models.Category.id == appointment.category_id).first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
    db_app = models.Appointment(**appointment.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get('/appointments', response_model=list[schemas.Appointment])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(models.Appointment).all()

@app.put('/appointments/{appointment_id}', response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail='Appointment not found')
    if appointment.category_id is not None:
        cat = db.query(models.Category).filter(models.Category.id == appointment.category_id).first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
    for field, value in appointment.dict().items():
        setattr(db_app, field, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete('/appointments/{appointment_id}')
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail='Appointment not found')
    db.delete(db_app)
    db.commit()
    return {'detail': 'Deleted'}
