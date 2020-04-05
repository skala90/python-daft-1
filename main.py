from fastapi import FastAPI, Request

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