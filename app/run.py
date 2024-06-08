import json
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_required
from . import db
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort

from .models import Client, MettaAttack, Attack, Run, RunTasks

run = Blueprint('run', __name__)

@run.route('/runs')
@login_required
def runs():
    runs = Run.query.all()
    return render_template('runs.html', runs=runs)


@run.route('/new_run')
@login_required
def new_run():
    clients = Client.query.all()
    attacks = Attack.query.all()
    return render_template('new_run.html', clients=clients, attacks=attacks)


@run.route('/new_run', methods=['POST'])
@login_required
def run_attack():
    client_ids = request.form.getlist('clients')
    attack_id = request.form.get('attack')

    # Convert client_ids from list of strings to list of integers
    client_ids = [int(id) for id in client_ids]

    # Fetch the selected attack and clients from the database
    attack = Attack.query.get(int(attack_id))
    clients = Client.query.filter(Client.id.in_(client_ids)).all()

    run_db = Run(status='Running', attack_id=attack.id, attack=attack, clients=clients, created_date=datetime.now())
    db.session.add(run_db)
    db.session.commit()

    attack_list = json.loads(attack.attacks)

    for attack_id in attack_list:
        metta_attack = MettaAttack.query.get(attack_id)
        if metta_attack is not None:
            actions = metta_attack.actions

            for client in clients:
                run_task = RunTasks(client_id=client.id, run_id=run_db.id, actions=actions)  # Use action as command
                db.session.add(run_task)
        else:
            print(f'MettaAttack with ID {attack_id} not found')

    db.session.commit()

    for client in clients:
        print(f'Running attack {attack.name} on client {client.hostname}')

    return redirect(url_for('run.runs'))


@run.route('/status/<int:client_id>', methods=['GET'])
@jwt_required()
def get_status(client_id):
    # Update the client's heartbeat
    #print(get_jwt_identity())
    client = Client.query.get(client_id)
    if client:
        client.heartbeat = datetime.now()
        db.session.commit()

    run_tasks = RunTasks.query.filter_by(client_id=client_id, status='Pending').all()

    run_tasks_json = [run_task.serialize() for run_task in run_tasks]

    return jsonify(run_tasks_json)


@run.route('/result/<int:task_id>', methods=['POST'])
@jwt_required()
def post_result(task_id):
    result_data = request.get_json()
    run_task = RunTasks.query.get(task_id)
    if run_task is None:
        abort(404, description="Task not found")

    run_task.output = json.dumps(result_data.get('results'), ensure_ascii=False)
    run_task.status = 'Done'

    run_tasks = RunTasks.query.filter_by(run_id=run_task.run_id).all()
    if all(task.status == 'Done' for task in run_tasks):
        run_main = Run.query.get(run_task.run_id)
        run_main.status = 'Done'

    db.session.commit()
    return jsonify(message="Results updated successfully"), 200


@run.route('/view_run/<int:run_id>', methods=['GET'])
@login_required
def view_run(run_id):
    run_tasks = RunTasks.query.filter_by(run_id=run_id).all()
    run = Run.query.get(run_id)
    attack_name = run.attack.name

    for run_task in run_tasks:
        actions = json.loads(run_task.actions)
        # output may be empty
        if run_task.output:
            output = json.loads(run_task.output)
        else:
            output = {}
        run_task.action_output = {k: (actions.get(k), output.get(k, "")) for k in actions}

    return render_template('view_run.html', run_tasks=run_tasks, attack_name=attack_name)


@run.route('/delete_run/<int:run_id>', methods=['POST'])
@login_required
def delete_run(run_id):
    run = Run.query.get(run_id)
    if run is None:
        abort(404, description="Run not found")
    run_tasks = RunTasks.query.filter_by(run_id=run_id).all()
    for run_task in run_tasks:
        db.session.delete(run_task)
    db.session.delete(run)
    db.session.commit()
    return redirect(url_for('run.runs'))