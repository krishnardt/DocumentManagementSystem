# -*- coding: utf-8 -*-
"""
Created on Friday May 15 10:00:01 2021

@author: KrishNa
@contributor: KrishNa
"""


from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status, File, UploadFile, Depends, Response

from sqlalchemy.orm import Session
import crud, models, schemas
import uvicorn
from database import SessionLocal, engine
from fastapi import Request, APIRouter
import time
import io, tempfile
from starlette.responses import StreamingResponse, JSONResponse
from fastapi.responses import FileResponse
import os, time, shutil
import CONSTANTS
#import threading


#app = FastAPI()
document_router = APIRouter()

models.Base.metadata.create_all(bind=engine)

#we can modify file_dir from CONSTANTS.py file
file_dir = CONSTANTS.FILE_DIR



#DB session initiator that can be used 
#as dependency for APIs
#Instead of sending it s dependency,
#we can use context managers to connect and
#disconnect the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        
        db.close()
  

#dummy class for threading to
#get the return values.
class Increment:
    def __init__(self):
        self.status = False

    def update(self, val):
        self.status = val



def upload_function(destination, file, email, db):
    """
    Description:
    ------------
    function that handles both upload and update document api logics

    input:
    ------
    destination: the target directory where the file is stored
    file: the file object that is uploaded to get the filename and content
    email: email-id of the person that uploaded/updated
    db: database dependency, we can resolve it using context managers too
    upload_mode: to identify if the file is being uploaded/updated

    returns:
    True: if upload is successfull,
    False: if any of the requirements failed
    --------
    """

    #logic to copy the file from source to desination
    #file path is the path of the file in target directory
    file_path = file_dir+"/"+file.filename
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    #db_user = crud.get_user_by_email(db, email=user.email)
    #insert_status = crud.create_user(db=db, user=user)
    
    try:
        
        #crud function to upload file
        upload_status = crud.create_document(file_path, file.filename, email, db)
        
        print("the upload_status is ", upload_status)
        
        return upload_status
    except:
        
        return False


def update_function(destination, file, email, db):
    """
    Description:
    ------------
    function that handles both upload and update document api logics

    input:
    ------
    destination: the target directory where the file is stored
    file: the file object that is uploaded to get the filename and content
    email: email-id of the person that uploaded/updated
    db: database dependency, we can resolve it using context managers too
    upload_mode: to identify if the file is being uploaded/updated

    returns:
    True: if upload is successfull,
    False: if any of the requirements failed
    --------
    """

    #logic to copy the file from source to desination
    #file path is the path of the file in target directory
    
    
    
    #threading.Lock().acquire()
    #print(threading.Lock().locked())
    try:
        #crud function to update file
        upload_status = crud.update_document(destination, file, email, db)
        print(upload_status)
        #incr.update(upload_status)
        return upload_status
    except:
        #incr.update(False)
        return False
    # print(threading.Lock().locked())
    # if threading.Lock().locked():
    #     threading.Lock().release()
    # incr.update(False)
    # return False



@document_router.get("/users", response_model=List[schemas.Users])
def read_users(limit: int = 100, db: Session = Depends(get_db)):
    """
    returns:
    all the users in the application
    """
    users = crud.get_users(db)

    return users





@document_router.post('/upload-doc')
async def upload_file(user:schemas.User = Depends(), in_file: UploadFile=File(...), db: Session = Depends(get_db)):
    """
    Description:
    ------------
    As authentication not applied here....
    lets take input as email-id, the person who is uploading the doc
    for the first time as owner and another input as the file being uploaded

    input:
    ------
    @user : schema that contains user_email
    in_file: the file object that an user uploads

    output:
    -------
    returns
    409: duplicate, if the file is already uploaded
    201: if the new file is created

    """
    
    upload_status = upload_function(file_dir, in_file, user.email, db)
    print(upload_status)
    if upload_status == False:
        return {
        'status': status.HTTP_409_CONFLICT,
        'detail':"trying to uploading the same content again. If modified, try update api"
        } 
        #"duplicate status"
    return {
    'status':status.HTTP_201_CREATED,
    'detail': f"file '{in_file.filename}' saved at '{file_dir}'"
    }
    


@document_router.get("/download_file/")
def download_file(filenames: schemas.Download=Depends(), db: Session = Depends(get_db)):
    """
    End-point to download files.

    Parameters
    ----------
    filename : str
        This is the filename which is sent in form from templates.
        Filename should be a valid of the files present in the 
        'All Files' folder.

    Returns
    -------
        A FileReponse of the selected filename.
        400: if there is any issue in upload docuemnt function.
        423: if the file is busy or locked.
    """

    access_status = crud.is_owner_collaborator(filenames.filename, filenames.email_id, db)
    print("the access status is ....... ",access_status)
    if access_status == False:
        return {
        'status': status.HTTP_406_NOT_ACCEPTABLE,
        'details': "must be filename/user is wrong/missing"
        }
    print(access_status)
    



    collab_update = crud.download_document(filenames.filename, filenames.email_id, db)
    print(collab_update)

    if collab_update == None:
        print("the value is ", access_status)
        return {
        'status': status.HTTP_423_LOCKED,
        'details': "file is busy"
        }

    if collab_update == False:
        return {
            'status':status.HTTP_400_BAD_REQUEST,
            'detail':"issue in updating document function"
        }
    return FileResponse(file_dir+"/"+filenames.filename, media_type="text/mp4", filename=filenames.filename)
    
    






@document_router.post('/share')
async def share_post(sharing_post : schemas.SharePost, db: Session = Depends(get_db)):
    """
    Description:
    ------------
    Owner can share the document to any user who is
    already in the database.

    input:
    ------
    input is a pydantic schema that is present in schemas.
    @sharing_post: that schema contains following inputs.
    collaborator_id: id to whom we want to share
    filename: name of the file that wanted to share
    access_level: the level of access to be given to user

    returns:
    200: if the sharing was success
    409: if the file is already shared.
    423: if the file is locked or busy
    """
    collaborator_id = sharing_post.collaborator_id
    file_name =  sharing_post.filename

    print(sharing_post)

    #curd function that takes care of sharing the post
    shared_status = crud.share_post(sharing_post, db)

    if shared_status == True:
        return {
        'status': status.HTTP_200_OK,
        'details': "post shared successfully"
        }
    elif shared_status == False:
        return {
        'status': status.HTTP_409_CONFLICT,
        'detail':"ALREADY SHARED"
        }

    else:
        return {
        'status': status.HTTP_423_LOCKED,
        'details': "file is busy"
        }




@document_router.get('/posts/{email}')
def get_my_posts(email: str, db: Session = Depends(get_db)):
    """
    here you get all posted the user is created and
    shared to user

    input params:
    @user_id: the id of the user

    @returns:
    200: if the data is fetched properly
    """
    my_posts = crud.get_user_post(email, db)

    return {
    'status':status.HTTP_200_OK,
    'data':my_posts,
    'details': 'consists of both owner and access and collaborator posts'
    }


@document_router.put('/update')
async def update_post(request: Request, user:schemas.User = Depends(), 
    in_file: UploadFile=File(...), db: Session = Depends(get_db)):
    """
    Description:
    ------------
    After the document is modified/edited, it can be uploaded here by
    owner/collaborator.
    Version check is based on the columns in these tables:
    a. modified_on in Files model/table(most recent file modified time)
    b. downloaded_on in Collaborators model/table(for a given user)

    if modified_on is less than the downloaded_on, then the conecerned user
    can update the file, otherwise, they have to pull it and do it again.

    inputs:
    -------
    @user: the schema that contains the field email-id who is updating
    in_file: the file object that an user uploads

    output:
    -------
    @returns
    202: if the modified data is accepted
    412: if content modified or working on old content
    406: if filename/user is wrong/missing or some issue in code
    423: if the file is locked

    """
    #crud function to check if there is any relation between 
    #file and the updater

    check_user_status = crud.is_owner_collaborator(in_file.filename, 
        user.email, db)
    
    if check_user_status == True:

        #function that handles both upload and update document logic
        #incr = Increment()
        saving_status = update_function(file_dir, in_file, user.email,
        db)
        # incr = Increment()
        # t1 = threading.Thread(target=update_function, args = (file_dir, in_file, user.email,
        #  db, incr, "update"))
        # t1.start()
        # t1.join()
        # saving_status = incr.status 
        print("------------------------------------")
        print("saving status is ", saving_status)
        if saving_status == None:
            return {
            'status':status.HTTP_412_PRECONDITION_FAILED,
            'detail':'content modified, please download the latest content and try again'
            }
        elif saving_status == "locked":
            return {
            'status':status.HTTP_423_LOCKED,
            'detail':'file is busy'
            }
        elif saving_status == False:
            return {
            'status': status.HTTP_406_NOT_ACCEPTABLE,
            'details': "some issue in the code"
            }


    else:
        return {
        'status': status.HTTP_406_NOT_ACCEPTABLE,
        'details': "must be filename/user is wrong/missing"
        } 

    return {
    'status': status.HTTP_202_ACCEPTED,
    "detail": f"file '{in_file.filename}' saved at '{file_dir}'"
    }
