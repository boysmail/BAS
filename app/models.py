from datetime import datetime

from . import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(80), nullable=False)
    ip = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    heartbeat = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Client %r>' % self.hostname


class MettaAttack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(180), nullable=False)
    group = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    os = db.Column(db.String(80), nullable=False)
    actions = db.Column(db.String(2000), nullable=False)

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'filename': self.filename, 'group': self.group}


class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    attacks = db.Column(db.String(2000), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def serialize(self):
        return {'id': self.id, 'name': self.name, 'steps': self.steps, 'created_date': self.created_date}


# TODO: TEST Run model
# Association table
clients_runs = db.Table('clients_runs',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('run_id', db.Integer, db.ForeignKey('run.id'), primary_key=True)
)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    attack_id = db.Column(db.Integer, db.ForeignKey('attack.id'), nullable=False)
    attack = db.relationship('Attack', backref=db.backref('runs', lazy=True))
    clients = db.relationship('Client', secondary=clients_runs, lazy='subquery',
        backref=db.backref('runs', lazy=True))
    tasks = db.relationship('RunTasks', backref='run', lazy=True)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'status': self.status,
            'attack_name': self.attack.name,
            'client_hostnames': [client.hostname for client in self.clients],
            'tasks': [task.serialize() for task in self.tasks],
            'created_date': self.created_date
        }


class RunTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    run_id = db.Column(db.Integer, db.ForeignKey('run.id'), nullable=False)  # New foreign key
    actions = db.Column(db.String(2000), nullable=False)
    output = db.Column(db.String(2000), nullable=True)
    status = db.Column(db.String(80), nullable=False, default='Pending')


    def serialize(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'run_id': self.run_id,
            'actions': self.actions,
            'output': self.output,
            'status': self.status
        }

