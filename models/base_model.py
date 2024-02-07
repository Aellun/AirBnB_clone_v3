#!/usr/bin/python3
"""
BaseModel Module Docstring:
Defines the BaseModel class,which serves as the foundation
for other model classes in the application.
This class encapsulates common attributes and behaviors such as initialization,
serialization, and interaction with the storage layer.
"""
import inspect
from datetime import datetime
import models
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import uuid

time = "%Y-%m-%dT%H:%M:%S.%f"

if models.storage_t == "db":
    Base = declarative_base()
else:
    Base = object


class BaseModel:
    """BaseModel Class Definition:
    The base class for all models in the application,
    providing common functionality.
    Inherits from SQLAlchemy's declarative_base
    if using a database storage system, otherwise inherits from object.
    """
    if models.storage_t == "db":
        id = Column(String(60), primary_key=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the BaseModel class.
        Accepts keyword arguments to set initial attribute values.
        Generates unique IDs and sets timestamps accordingly."""
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    setattr(self, key, value)
            if kwargs.get("created_at", None) and type(self.created_at) is str:
                self.created_at = datetime.strptime(kwargs["created_at"], time)
            else:
                self.created_at = datetime.utcnow()
            if kwargs.get("updated_at", None) and type(self.updated_at) is str:
                self.updated_at = datetime.strptime(kwargs["updated_at"], time)
            else:
                self.updated_at = datetime.utcnow()
            if kwargs.get("id", None) is None:
                self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at

    def __str__(self):
        """String rep of the BaseModel class"""
        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, self.id,
                                         self.__dict__)

    def save(self):
        """updates the attribute 'updated_at' with the current datetime"""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """ Converts the instance to a dictionary rep.
        Formats datetime objects to a string rep for compatibility.
        Omits certain internal attributes and sensitive information
        unless explicitly needed.
        """
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        frame = inspect.currentframe().f_back
        func_name = frame.f_code.co_name
        class_name = ''
        if 'self' in frame.f_locals:
            class_name = frame.f_locals["self"].__class__.__name__
        is_fs_writing = func_name == 'save' and class_name == 'FileStorage'
        if 'password' in new_dict and not is_fs_writing:
            del new_dict['password']
        return new_dict

    def delete(self):
        """remove the current instance from the storage"""
        models.storage.delete(self)
