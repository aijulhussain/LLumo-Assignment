from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., example="E123")
    name: str = Field(..., example="John Doe")
    department: str = Field(..., example="Engineering")
    salary: float = Field(..., example=75000)
    joining_date: date = Field(..., example="2023-01-15")
    skills: List[str] = Field(..., example=["Python", "MongoDB", "APIs"])

    @field_validator("skills", mode="before")
    def ensure_list_of_strings(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None

    @field_validator("skills", mode="before")
    def ensure_list_of_strings(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

class EmployeeOut(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: float
    joining_date: date
    skills: List[str]

    model_config = {"from_attributes": True}
