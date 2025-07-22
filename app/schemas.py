from datetime import datetime
from pydantic import BaseModel

class AppointmentBase(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

    class Config:
        orm_mode = True
