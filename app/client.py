import json
import subprocess
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, send_from_directory, jsonify
from flask_jwt_extended import create_access_token
from flask_login import login_required

from . import db
from .models import Client

client = Blueprint('client', __name__)

@client.route('/clients')
@login_required
def clients():
    clients_list = Client.query.all()
    return render_template('clients.html', clients=clients_list)


@client.route('/delete_client/<int:id>', methods=['POST'])
@login_required
def delete_client(id):
    client = Client.query.get(id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('client.clients'))


@client.route('/new_client')
@login_required
def contact():
    try:
        ip, port = request.host.split(':')
    except ValueError:
        ip = request.host
        port = 80
    return render_template('new_client.html', ip=ip, port=port)


@client.route('/register_client', methods=['POST'])
def register_client():
    hostname = request.json.get('name')
    ip = request.json.get('ip')
    date = request.json.get('date')

    client = Client(hostname=hostname, ip=ip, date=datetime.fromisoformat(date))
    db.session.add(client)
    db.session.commit()
    # JWT
    access_token = create_access_token(identity=client.id)
    # return id
    return jsonify(access_token=access_token, client_id=client.id)


@client.route('/new_client', methods=['POST'])
def new_client():
    ip = request.form.get('ip')
    port = request.form.get('port')
    name = request.form.get('name')
    config = {
        "ip": ip,
        "port": port,
        "name": name
    }

    # Write config to a file
    with open(f'app/client/config.json', 'w') as f:
        json.dump(config, f)
    subprocess.run(
        ['pyinstaller',
         '--onefile', 'client/main.py',
         '--add-data', 'client/config.json;.',
         '--distpath', 'downloads',
         '--noconsole',
         '-n', name,
         '--upx-dir', 'upx'], cwd='app')

    filename = f'{name}.exe'
    return send_from_directory('downloads', filename, as_attachment=True)


@client.route('/client.exe')
def download_client():
    return send_from_directory('downloads', 'client.exe', as_attachment=True)


