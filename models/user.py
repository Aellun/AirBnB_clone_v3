#!/usr/bin/python3
""" Module docstring: contain the User class representing users in the system.
attributes:email, password, and personal information.
"""
import hashlib
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(BaseModel, Base):
    """Representation of a class user
    Attributes:
        email (str): The user's email address.
        password (str): The user's encrypted password.
        first_name (str, optional): The user's first name.
        last_name (str, optional): The user's last name.
        places (relationship): A collection of places associated with the user.
        reviews (relationship): A collection of reviews authored by the user.
    """
    if models.storage_t == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship(
            "Place",
            cascade="all, delete, delete-orphan",
            backref="user"
        )
        reviews = relationship(
            "Review",
            cascade="all, delete, delete-orphan",
            backref="user"
        )
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""

    def __init__(self, *args, **kwargs):
        """initializes user
         Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments."""
        super().__init__(*args, **kwargs)

    def __setattr__(self, __name: str, __value) -> None:
        """
        Sets an attribute of this class to a given value.
         Args:
            __name (str): The name of the attribute to set.
            __value: The value to assign to the attribute.
            Note:
            If the attribute being set is 'password',
            the value is hashed using MD5 before assignment.
        """
        if __name == 'password':
            if type(__value) is str:
                m = hashlib.md5(bytes(__value, 'utf-8'))
                super().__setattr__(__name, m.hexdigest())
        else:
            super().__setattr__(__name, __value)
