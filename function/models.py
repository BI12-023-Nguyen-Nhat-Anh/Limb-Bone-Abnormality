from .connect import db
from flask_login import UserMixin
from sqlalchemy.sql  import func

class User(db.Model, UserMixin):
    role = db.Column(db.Integer, default = 2)
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    token = db.Column(db.String(50))

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(50), nullable = False)
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship('User')
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    subfolders = db.relationship('Folder', backref=db.backref('parent_folder', remote_side=[id]))

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(50), nullable = False)
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    subfiles = db.relationship('Folder', backref=db.backref('files', lazy='dynamic'))
 