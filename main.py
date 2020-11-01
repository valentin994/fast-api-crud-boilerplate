from fastapi import FastAPI
import uvicorn
from models import User

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users")
def register_user(user: User):
    return {'data': user,
            'msg': f'Successfully registered {user.name}'}

if __name__ == "__main__":
     uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")

 