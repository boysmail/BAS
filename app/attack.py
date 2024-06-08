import json
import os
import subprocess
from datetime import datetime

import yaml
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required

from . import db
from .models import MettaAttack, Attack

attack = Blueprint('attack', __name__)


# Patch yaml to force keys to be strings https://stackoverflow.com/questions/50045617/yaml-load-force-dict-keys-to-strings
def my_construct_mapping(self, node, deep=False):
    data = self.construct_mapping_org(node, deep)
    return {(str(key) if isinstance(key, int) else key): data[key] for key in data}


yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
yaml.SafeLoader.construct_mapping = my_construct_mapping


@attack.route('/attacks')
@login_required
def attacks():
    attacks_list = Attack.query.all()
    return render_template('attacks.html', attacks=attacks_list)


@attack.route('/delete_attack/<int:id>', methods=['POST'])
@login_required
def delete_attack(id):
    try:
        attack = Attack.query.get(id)
        db.session.delete(attack)
        db.session.commit()
    except Exception as e:
        # attack probably used in a run
        flash("Attack is in use")
    return redirect(url_for('attack.attacks'))


@attack.route('/new_attack')
@login_required
def new_attack():
    return render_template('new_attack.html')


@attack.route('/new_attack', methods=['POST'])
@login_required
def create_new_attack():
    data = request.get_json()
    attack_name = data.get('attackName')
    table_data = data.get('tableData')
    steps = len(table_data)

    attack = Attack(name=attack_name, steps=steps, created_date=datetime.now(), attacks=json.dumps(table_data))
    db.session.add(attack)
    db.session.commit()

    return redirect(url_for('attack.attacks'))


@attack.route('/refresh_attacks')
@login_required
def refresh_attacks():

    # metta
    folder_path = 'app\metta\MITRE'
    paths = []
    # clear the database
    db.session.query(MettaAttack).delete()
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                text = yaml.safe_load(open(file_path))
                paths.append(file_path)
                text = yaml.safe_load(open(file_path))
                # get group from file path
                group = file_path.split('\\')[-2]
                db.session.add(MettaAttack(name=text["name"], filename=file_path, group=group,
                                           description=text["meta"]["description"], os=text["os"],
                                           actions=json.dumps(text["meta"]["purple_actions"])))
            except Exception as e:
                # Not a valid YAML file
                pass
    db.session.commit()
    return paths


@attack.route('/get_attacks')
@login_required
def get_attacks():
    attacks_list = MettaAttack.query.all()
    attacks_ser = [attack.serialize() for attack in attacks_list]
    # attacks_list = [{"name": "Attack 1", "description": "This is attack 1", "value": "attack1"},
    #         {"name": "Attack 2", "description": "This is attack 2", "value": "attack2"},
    #         {"name": "Attack 3", "description": "This is attack 3", "value": "attack3"},
    #         {"name": "Attack 4", "description": "This is attack 4", "value": "attack4"},
    #         {"name": "Attack 5", "description": "This is attack 5", "value": "attack5"}]
    return jsonify(attacks_ser)
