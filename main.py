import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from routes import router as employee_router
from mongo_db import ensure_indexes_and_schema, client
from JWT_authentication import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="LLUMO Assessment API", version="2.0")
app.include_router(employee_router)

@app.on_event("startup")
async def startup_event():
    await ensure_indexes_and_schema()

@app.on_event("shutdown")
async def shutdown_event():
    client.close()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
