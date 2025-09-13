from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from datetime import datetime, date
from bson import SON
from pymongo import DESCENDING

from models import EmployeeCreate, EmployeeOut, EmployeeUpdate
from mongo_db import employees_collection
from JWT_authentication import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])

def doc_to_employee_out(doc) -> EmployeeOut:
    jd = doc.get("joining_date")
    if isinstance(jd, datetime):
        jd = jd.date()
    return EmployeeOut(
        employee_id=doc["employee_id"],
        name=doc["name"],
        department=doc["department"],
        salary=doc["salary"],
        joining_date=jd,
        skills=doc.get("skills", [])
    )

@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, user: dict = Depends(get_current_user)):
    doc = payload.dict()
    jd = doc.pop("joining_date")
    doc["joining_date"] = datetime(jd.year, jd.month, jd.day)
    try:
        res = await employees_collection.insert_one(doc)
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="employee_id must be unique")
        raise
    new_doc = await employees_collection.find_one({"_id": res.inserted_id})
    return doc_to_employee_out(new_doc)

@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str):
    doc = await employees_collection.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return doc_to_employee_out(doc)

@router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeUpdate, user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if "joining_date" in update_data and isinstance(update_data["joining_date"], date):
        jd = update_data["joining_date"]
        update_data["joining_date"] = datetime(jd.year, jd.month, jd.day)
    result = await employees_collection.update_one(
        {"employee_id": employee_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    doc = await employees_collection.find_one({"employee_id": employee_id})
    return doc_to_employee_out(doc)

@router.delete("/{employee_id}")
async def delete_employee(employee_id: str, user: dict = Depends(get_current_user)):
    result = await employees_collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

@router.get("/", response_model=List[EmployeeOut])
async def list_employees(
    department: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    query = {}
    if department:
        query["department"] = department
    cursor = employees_collection.find(query).sort("joining_date", DESCENDING).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [doc_to_employee_out(d) for d in docs]


@router.get("/employees/avg-salary")
async def avg_salary_by_department():
    pipeline = [
        {
            "$group": {
                "_id": "$department",                 
                "avg_salary": {"$avg": "$salary"}     
            }
        },
        {
            "$project": {                           
                "_id": 0,
                "department": "$_id",
                "avg_salary": 1,
                
            }
        }
    ]

    result = await employees_collection.aggregate(pipeline).to_list(None)

    if not result:
        raise HTTPException(status_code=404, detail="No employees found")

    return result



@router.get("/employees/search")
async def search_employees(skill: str, limit: int = 10):
    cursor = employees_collection.find(
        {"skills": {"$regex": f"^{skill}$", "$options": "i"}}
    ).limit(limit)

    results = await cursor.to_list(length=limit)

    # Convert ObjectId to string
    for r in results:
        r["_id"] = str(r["_id"])

    if not results:
        return {"message": f"No employees found with skill {skill}"}
    return results
