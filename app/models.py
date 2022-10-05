from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

connectionRequests = db.Table('connectionRequests',
    db.Column('requesting_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('requested_id', db.Integer, db.ForeignKey('users.id'))
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_connected = db.Column(db.Integer, default=0)
    connected_with = db.Column(db.Integer)

    task_lists = db.relationship('TaskList', backref='owner', lazy='dynamic')
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')
    # connections = db.relationship('ConnectionRequest', backref='owner', lazy='dynamic')

    requested = db.relationship(
        'User', secondary=connectionRequests,
        primaryjoin=(connectionRequests.c.requesting_id == id),
        secondaryjoin=(connectionRequests.c.requested_id == id),
        backref=db.backref('connectionRequests', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TaskList(db.Model):
    __tablename__ = 'tasklists_table'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_shared = db.Column(db.Integer, default=0)

    task_lists = db.relationship('Task', backref='tasks_tasklist', lazy='dynamic')
    
    def __repr__(self):
        return '<TaskList: {}, user: {}>'.format(self.text, self.user_id)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tasklist_id = db.Column(db.Integer, db.ForeignKey('tasklists_table.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Task: {}, tasklist_id: {}>'.format(self.text, self.tasklist_id)

# --helper table to keep track about pending request to connect--
# if user wants to connect with somebody, he makes a request and
# another user have to decline or accept the request
# class ConnectionRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     id_requesting = db.Column(db.Integer, db.ForeignKey('users.id'))
#     id_requested = db.Column(db.Integer, db.ForeignKey('users.id'))

#     def __repr__(self):
#         return '<ConnectionRequest - id_requesting: {}, id_requested: {}>'.format(self.id_requesting, self.id_requested)

