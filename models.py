# -*- coding: utf-8 -*-
"""
Created on Friday May 14 21:00:01 2021

@author: KrishNa
"""
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
# from database import Base, engine

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy


from database import engine, SessionLocal, Base

# SQLALCHEMY_DATABASE_URL = "postgresql://root:root@localhost:5432/document_management1"


# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()



class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)



    file_data = relationship("Files", back_populates="owned")
    collaborator = relationship("Collaborators", back_populates="owned")



class FileStatusEnum(Enum):
    editing = 1
    saved = 2


class Files(Base):
    __tablename__= "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    filepath = Column(String, unique=True, index=True)
    created_on = Column(DateTime)
    owner = Column(Integer, ForeignKey("users.id"))
    modified_on = Column(DateTime)
    #file_status = Column(Enum(FileStatusEnum, name = "file_status"))
    file_status = Column(String)

    owned = relationship("Users", back_populates="file_data")
    files_data = relationship("Collaborators", back_populates="access")



class AccessLevelEnum(Enum):
    edit = 1
    read = 2

class Collaborators(Base):
    __tablename__ = "collaborators"

    #id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    collaborator_id = Column(Integer, ForeignKey("users.id"))
    file_id = Column(Integer, ForeignKey("files.id"))
    #access_level = Column(Enum(AccessLevelEnum))
    access_level = Column(String)
    access_date= Column(DateTime)
    expiry_on = Column(DateTime)
    downloaded_on = Column(DateTime)
    active_yn = Column(Boolean, default=True)

    access = relationship("Files", back_populates="files_data")
    owned = relationship("Users", back_populates="collaborator")

    __table_args__ = (
    sqlalchemy.PrimaryKeyConstraint(
        collaborator_id, file_id,
        ),
    )











# Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)
#Base.metadata.create_all(engine)

