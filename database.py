# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 18:43:52 2020

@author: Ravi Varma Injeti
@contributor: KrishNa
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import CONSTANTS



username = CONSTANTS.USERNAME
password = CONSTANTS.PASSWORD
ip_address = CONSTANTS.IP_ADDRESS
port = CONSTANTS.DB_PORT
db = CONSTANTS.DB_NAME

#SQLALCHEMY_DATABASE_URL = "postgresql://root:root@localhost:5432/document_management"

SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{ip_address}:{port}/{db}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()