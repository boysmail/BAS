from sqlalchemy import func
from . import db
from flask import Blueprint, render_template

from .models import Client, Attack, Run, RunTasks

main = Blueprint('main', __name__)


@main.route('/')
def index():
    num_clients = Client.query.count()
    num_attacks = Attack.query.count()
    num_runs = Run.query.count()
    runs_per_day = db.session.query(func.date(Run.created_date), func.count(Run.id)).group_by(
        func.date(Run.created_date)).all()
    runs_per_day = {str(date): count for date, count in runs_per_day}
    tasks_per_client = db.session.query(Client.hostname, func.count(RunTasks.id)).join(RunTasks).group_by(
        Client.hostname).all()
    tasks_per_client = {str(hostname): count for hostname, count in tasks_per_client}
    steps_per_attack = db.session.query(Attack.name, Attack.steps).all()
    steps_per_attack = {str(name): steps for name, steps in steps_per_attack}

    return render_template('dashboard.html',
                           num_clients=num_clients,
                           num_attacks=num_attacks,
                           num_runs=num_runs,
                           runs_per_day=runs_per_day,
                           tasks_per_client=tasks_per_client,
                           steps_per_attack=steps_per_attack)
