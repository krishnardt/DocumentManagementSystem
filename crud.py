from sqlalchemy.orm import Session
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
import os, datetime as dt, time, shutil
import models, schemas
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import load_only
from models import Users, Files, Collaborators
import CONSTANTS

from lockfile import LockFile, LockTimeout


# filename = 'crud.log'
# logging = qrl.create_or_get_logger(filename)


file_dir = CONSTANTS.FILE_DIR#"/home/spyder/Documents/Document_Management/BLOBS"


def get_users(db: Session):
    return db.query(models.Users).all()


def get_email_id(email: str, db: Session):
	#we willl get the email object of a given user
	return db.query(models.Users).filter(models.Users.email == email).first()

def add_email_id(email: str, db: Session):
	#adds email-id to the database
	user_det = Users(name = '', email = email)
	db.add(user_det)
	db.commit()
	db.refresh(user_det)
	return user_det


def get_file_id_by_filename(filename, db):
	#gets file_id from file based on file name
	try:
		file_id = db.query(Files).filter(Files.name==filename).with_entities(Files.id).first()
		print(file_id[0])
		return file_id[0]
	except:
		return None

def get_filepath_by_file_id(file_id, db):
	#gets path of the uploaded file in the server based on file_id
	file_id = db.query(Files).filter(Files.id==file_id).with_entities(Files.filepath).first()
	print(file_id[0])
	return file_id[0]

def update_file_status(file_id, db):
	#updates the file related record in table, basically modified date
	file_status = db.query(Files).filter(Files.id==file_id).update({'modified_on': dt.datetime.now()})
	db.commit()

	return file_status



def create_document(destination, filename, email, db: Session):
	#inserts a document in the given location of a server
	#Adds record to the File table and Collaborator's table.
	
	try:

		email_id = get_email_id(email, db)
		if email_id is None:
			email_id = add_email_id(email, db).id
			print(email_id)
		else:
			email_id = email_id.id
		print(email_id)

		doc_det = Files(name=filename, filepath = destination, created_on = str(dt.datetime.now()),
			owner = email_id, modified_on = dt.datetime.now(),file_status='saved')

		print(doc_det)
		db.add(doc_det)
		db.commit()
		#db.refresh(doc_det)
		db.flush()

		print(doc_det.id)
		shared_status = Collaborators(collaborator_id=email_id,
				file_id = doc_det.id, access_level = "owner",
				access_date = dt.datetime.now(), downloaded_on = dt.datetime.now())
		db.add(shared_status)
		db.commit()
		db.refresh(shared_status)
		return True
	except Exception as e:
	 	return False


def is_owner_collaborator(filename, email, db):
	"""
	Description:
	checks the relationship between user and file
	inputs:
	-------
	filename: the name of the file
	email: user's email id
	db: database conenction

	returns:
	--------
	False: if email-id or file is wrong
	False: if there is no relation between file and user
	True: if there is a relationship between user and file.
	"""
	email_id = get_email_id(email, db)
	file_id = get_file_id_by_filename(filename, db)
	print(email_id, file_id)

	if email_id is None or file_id is None:
		return False
	#collab status to check if there is any realtion
	#between user and file
	collab_status = db.query(Collaborators).filter(
		and_(Collaborators.collaborator_id == email_id.id,
		Collaborators.file_id == file_id)).first()
	print("the onwer and collab status is ", collab_status)
	if collab_status is None:
		return False

	
	return True


def version_check(email_id, file_id, db: Session):
	"""
	Description:
	to check if the modified file and server file
	both are of same version based upon then user's recent
	downloaded time and file's recent modified time.

	inputs:
	-------
	email_id: users;s email-id
	file_id: the id of a given file
	db: Database object

	returns:
	--------
	True: if the file can be uploaded
	False: if there is any change in version/modified.

	"""

	#gets the recent modified time from File model
	recent_uploaded_time = db.query(Files).filter(Files.id == file_id). with_entities(
		Files.modified_on).first()
	print(recent_uploaded_time)
	recent_uploaded_time= recent_uploaded_time[0]

	#gets the user's downloaded time of a file
	user_downloaded_time = db.query(Collaborators).filter(
		and_(Collaborators.collaborator_id == email_id.id,
		Collaborators.file_id == file_id)).with_entities(Collaborators.downloaded_on).first()
	print(user_downloaded_time)
	user_downloaded_time = user_downloaded_time[0]

	#if the modified time is greater thant the user downlaoded time,
	#then the record is outdated
	if user_downloaded_time < recent_uploaded_time:
		return False

	return True


def is_owner(email_id, file_id, db):
	#to check the user is owner or not
	file_owner = db.query(Files).filter(Files.id == file_id).with_entities(Files.owner).first()
	if file_owner[0] == file_id:
		return True
	return False



def update_document(destinaton, file, email, db:Session):

	email_id = get_email_id(email, db)
	file_id = get_file_id_by_filename(file.filename, db)
	print(email)

	#to include version check based on modified time and idownoaded time


	version_status = version_check(email_id, file_id, db)
	print("version check is ",version_status)

	if version_status == False:
		return None

		#this part creates a lock object with the given file path
	file_lock_check = LockFile(destinaton+'/'+file.filename)
	#checks if the file is locked or not
	if file_lock_check.is_locked():
		if is_owner(email_id, file_id, db) == True:
			#if the user is owner the lock is released
			lock.release()
		else:
			#returns None if locked and the user is not owner
			print("file is locked for ", email)
			return "locked"

	#locks the file object
	file_lock_check.acquire()

	while file_lock_check.i_am_locking():

		#lock has been implemented on a record.
		#No one can do modification through database, until current transaction is completed.
		#in the file_status, the lock has been implemented on a given file record
		#then the updated file has been uploaded
		#and then the modified time is updated and record will be releasaed.
		#this is row-level locking.
		#Even though the operations can be done on physical file level
		#through the database no one can do modifications on it until the lock is released.
		try:
			file_status = db.query(Files).filter(Files.id==file_id).with_for_update().first()
			#
			#time.sleep(20)
			#.update({'modified_on': dt.datetime.now()})
			
			file_path = destinaton+"/"+file.filename

			with open(file_path, "wb+") as file_object:
				shutil.copyfileobj(file.file, file_object)
			
			file_status.modified_on = dt.datetime.now()
			db.commit()
			#file_update = update_file_status(file_id, db)
			update_status = db.query(Collaborators).filter(and_(
				Collaborators.collaborator_id == email_id.id,Collaborators.file_id == file_id))
			update_status = update_status.update({'downloaded_on': dt.datetime.now()})
			db.commit()
			#releases the lock if anything goes wrong
			file_lock_check.release()
		except LockTimeout:
		    print("enterd into exception")
		    #brute method to break the lock
		    file_lock_check.break_lock()
		    file_lock_check.acquire()
		    return False

	if file_lock_check.is_locked():
		file_lock_check.release()


	return True


def download_document(filename, email, db):
	#After ownloading the file to a local server
	# we will be updating the downloded_on field of
	#Collaborators table. For version check purpose
	email_id = get_email_id(email, db).id
	file_id = get_file_id_by_filename(filename, db)
	print(email_id, file_id)


	#this part creates a lock opject with the given file path
	file_lock_check = LockFile(file_dir+'/'+filename)
	#using is_locked, we will get to know, it the file is locked or not
	print("the file status   ", file_lock_check.is_locked())
	if file_lock_check.is_locked():
		if is_owner(email_id, file_id, db) == True:
			#if the current user is owner we, will release the lock
			lock.release()
			print("owner file status  ", file_lock_check.is_locked())
		else:
			#otherwise i returns none as the fileis alreay locked
			print("tje file status   ", file_lock_check.is_locked())
			return None


	try:
		print("downloading from here")
		update_status = db.query(Collaborators).filter(and_(
			Collaborators.collaborator_id == email_id,Collaborators.file_id == file_id))
		update_status = update_status.update({'downloaded_on': dt.datetime.now()})
		db.commit()
		print(update_status)
		return True
	except:
		return False
	





def share_post(sharing, db: Session):

	#sharing the file to the user as collaborator
	#is nothing but adding the user as collaborator
	#once the user is added as collaborator, the collaborator
	#can download it, edit and upload it.
	user_email = sharing.collaborator_id
	filename = sharing.filename
	access_level = sharing.access_level
	try:
		file_id =get_file_id_by_filename(filename, db)
		collaborator_id = get_email_id(user_email, db).id

		file_lock_check = LockFile(file_dir+'/'+filename)

		if file_lock_check.is_locked():
			if is_owner(collaborator_id, file_id, db) == True:
				lock.release()
			else:
				return None

		shared_status = Collaborators(collaborator_id=collaborator_id,
			file_id = file_id, access_level = access_level,
			access_date = dt.datetime.now())
		db.add(shared_status)
		db.commit()
		db.refresh(shared_status)
		return True
	except :
		return False



def get_user_post(email: str, db: Session):
	#gets the posts which are shared to the given user and 
	#which are owned by the given user.
	user_id = get_email_id(email, db).id
	my_posts = db.query(Files).filter(Files.owner == user_id).with_entities(Files.id, Files.name, Files.filepath).all()

	shared_posts = db.query(Collaborators, Files).filter(and_(Collaborators.file_id == Files.id, Collaborators.collaborator_id == user_id)).with_entities(
		Files.id, Files.name, Files.filepath, Collaborators.access_level).all()

	#shared_posts= db.query(Files).filter(Files.owner == user_id).with_entities(Files.name, Files.filepath).all()
	print(my_posts, shared_posts)

	return {'owner': my_posts, 'collaborator': shared_posts}