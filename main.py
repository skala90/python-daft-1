from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method/")
def method(request: Request):
    return {"method": f"{request.method}"}

@app.put("/method/")
def method(request: Request):
    return {"method": f"{request.method}"}

@app.post("/method/")
def method(request: Request):
    return {"method": f"{request.method}"}

@app.delete("/method/")
def method(request: Request):
    return {"method": f"{request.method}"}

class PatientInput(BaseModel):
    name: str
    surename: str

class PatientOutput(BaseModel):
    id: int
    patient: dict

def update_counter():
    with open("counter.txt",mode="r") as f:
        counter = f.read()

    counter = int(counter)

    with open("counter.txt",mode="w") as f:
        f.write(str(counter+1))

    return counter


@app.post("/patient/", response_model=PatientOutput)
def receive_patient(rq: PatientInput):
    return PatientOutput(patient=rq.dict(), id=update_counter())