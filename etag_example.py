from fastapi import FastAPI
from starlette.requests import Request
from fastapi_etag import Etag, add_exception_handler

app = FastAPI()
add_exception_handler(app)


async def get_hello_etag(request: Request):
    return "etagfor" + request.path_params["name"]


@app.get("/hello/{name}", dependencies=[Depends(Etag(get_hello_etag))])
async def hello(name: str):
    return {"hello": name}