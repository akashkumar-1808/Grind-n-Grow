from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import User, Subject, Session

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        exclude = ("password",)

class SubjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Subject
        include_fk = True
        load_instance = True

class SessionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Session
        include_fk = True
        load_instance = True
