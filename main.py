from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json

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

def load_patient_db():
    with open('patient_data.jsonl', 'r', encoding='utf') as infile:
        jsonl_content = infile.readlines()
    return [json.loads(item) for item in jsonl_content]


def save_patient(PatientOutput):
    with open('patient_data.jsonl', 'a', encoding='utf') as outfile:
        res_dict = PatientOutput.patient
        res_dict["id"] = PatientOutput.id
        json.dump(res_dict, outfile, ensure_ascii=False)
        outfile.write('\n')


@app.post("/patient/", response_model=PatientOutput)
def receive_patient(rq: PatientInput):
    result = PatientOutput(patient=rq.dict(), id=update_counter())
    save_patient(result)
    return result

@app.get("/patient/{id}")
def find_patient(id):
    list_of_patients = load_patient_db()
    print(list_of_patients)
    res = [item for item in list_of_patients if item["id"] == int(id)]
    print(res)
    if len(res) == 1:
        return {"name":res[0]["name"], "surename":res[0]["surename"]}
    else:
        raise HTTPException(status_code=204, detail="Item not found")

@app.get("/welcome")
def welcome():
	return {"message": "Hello World during the coronavirus pandemic!"}