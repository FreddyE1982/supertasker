from datetime import datetime
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    color: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    category_id: int | None = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

    class Config:
        orm_mode = True
