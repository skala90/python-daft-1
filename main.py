from fastapi import Depends, FastAPI, Request, HTTPException, Cookie, status, Response
from pydantic import BaseModel
from hashlib import sha256
import json
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse

app = FastAPI()
app.session_tokens = []
app.secret_key = "very constant and random secret, best 64 characters, here it is."


security = HTTPBasic()


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
    with open("counter.txt", mode="r") as f:
        counter = f.read()

    counter = int(counter)

    with open("counter.txt", mode="w") as f:
        f.write(str(counter + 1))

    return counter


def load_patient_db():
    with open("patient_data.jsonl", "r", encoding="utf") as infile:
        jsonl_content = infile.readlines()
    return [json.loads(item) for item in jsonl_content]


def save_patient(PatientOutput):
    with open("patient_data.jsonl", "a", encoding="utf") as outfile:
        res_dict = PatientOutput.patient
        res_dict["id"] = PatientOutput.id
        json.dump(res_dict, outfile, ensure_ascii=False)
        outfile.write("\n")


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
        return {"name": res[0]["name"], "surename": res[0]["surename"]}
    else:
        raise HTTPException(status_code=204, detail="Item not found")


from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@app.get("/welcome")
def welcome(request: Request, session_token: str = Cookie(None)):
    if session_token in app.session_tokens:
        return templates.TemplateResponse("welcome.html", {"request": request, "user": "trudnY"})
    else:
        raise HTTPException(status_code=401, detail="Unathorised")

@app.post("/login")
def get_current_user(
    response: Response, credentials: HTTPBasicCredentials = Depends(security)
):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    session_token = sha256(
        bytes(
            f"{credentials.username}{credentials.password}{app.secret_key}",
            encoding="utf8",
        )
    ).hexdigest()
    app.session_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    response.headers["Location"] = "/welcome"
    response.status_code = status.HTTP_302_FOUND

@app.post("/logout")
def logout(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=401, detail="Unathorised")
    app.session_tokens.remove(session_token)
    return RedirectResponse("/")
