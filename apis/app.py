from fastapi import FastAPI 

app = FastAPI()

@app.get("/goodbye") #http://example.com/goodbye 
def goodbye():
    return {"status": "bye"}

@app.get("/hello/{name}") #http://example.com/hello/ashwin -> hello ashwin
def greet(name: str):
    return {"message": f"hello {name}"}
