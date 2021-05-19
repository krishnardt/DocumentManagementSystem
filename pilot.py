from fastapi import FastAPI
from main import document_router
#from security import security_router
import uvicorn
import crud, models, schemas
import uvicorn, time
from database import SessionLocal, engine
from fastapi import Request, Depends
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware#, SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware
import psycopg2
from psycopg2 import sql
import CONSTANTS

from models import Users, Files, Collaborators




app = FastAPI(title='DMS',
        description='Document Management System',
        version='1.0.0', redoc_url = None,)


def init_routers(app: FastAPI) -> None:
    app.include_router(document_router, prefix='', tags=['documents'])
    #app.include_router(security_router, prefix='', tags=['Security'])



def check_or_create_db():
    con = psycopg2.connect(
       database="postgres", user=CONSTANTS.USERNAME, password=CONSTANTS.PASSWORD, host=CONSTANTS.IP_ADDRESS, port= CONSTANTS.DB_PORT
    )
    con.autocommit = True
    print('Database connected.')


    cur = con.cursor()

    cur.execute("SELECT datname FROM pg_database;")

    list_database = cur.fetchall()

    database_name = "doc_service2"#CONSTANTS.DB_NAME

    if (database_name,) in list_database:
        print("'{}' Database already exist".format(database_name))
    else:
        print("'{}' Database not exist.".format(database_name))
        sql = '''CREATE database doc_service''';
        cur.execute(sql)
        print("Database created successfully........")
    con.close()
    print('Done')

    Users.__table__.create(bind=engine, checkfirst=True)
    Files.__table__.create(bind=engine, checkfirst=True)
    Collaborators.__table__.create(bind=engine, checkfirst=True)





def create_app() -> FastAPI:
    
    init_routers(app=app)
    #please uncomment if you want to create database and its tables automaticallly.
    #this may workwith privilige details or maynot work as it is not tested due to time constraint
    #but small tweakings would automate all the database related part.

    
    #check_or_create_db()

    return app


app = create_app()



origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.debug = True


if __name__ == "__main__":
    uvicorn.run("pilot:app", host="127.0.0.1", port=8000, reload=True)
    #app.run(debug=True)