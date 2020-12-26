from app.main import db
import datetime
from sqlalchemy.sql import func

from app.main import db
import datetime
from sqlalchemy.sql import func


class Provider(db.Model):
    __tablename__ = "PROVIDER"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    credentials = db.relationship("Credentials", back_populates="provider")


class Credentials(db.Model):
    __tablename__ = "CREDENTIALS"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True, unique=True)

    provider_id = db.Column(db.Integer, db.ForeignKey("PROVIDER.id"))
    provider = db.relationship("Provider", back_populates="credentials")
