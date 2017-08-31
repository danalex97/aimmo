#!/usr/bin/env python
import cPickle as pickle
import logging
import os
import sys

import eventlet

eventlet.sleep()
eventlet.monkey_patch()

import flask
from flask_socketio import SocketIO

from simulation.turn_manager import state_provider
from simulation import map_generator
from simulation.avatar.avatar_manager import AvatarManager
from simulation.turn_manager import ConcurrentTurnManager
from simulation.worker_manager import WORKER_MANAGERS
from simulation.world_state import WorldState

app = flask.Flask(__name__)
socketio = SocketIO()

worker_manager = None

# Every user has its own world state.
world_state_manager = {}

@socketio.on('connect')
def world_init():
    socketio.emit('world-init')

@socketio.on('disconnect')
def exit_game():
    del world_state_manager[flask.session['id']]

@socketio.on('client-ready')
def client_ready(client_id):
    flask.session['id'] = client_id
    world_state = WorldState(state_provider)
    world_state_manager[client_id] = world_state

def send_world_update():
    for world_state in world_state_manager.values():
        socketio.emit(
            'world-update',
            world_state.get_updates(),
            broadcast=True,
        )

@app.route('/')
def healthcheck():
    return 'HEALTHY'

@app.route('/player/<player_id>')
def player_data(player_id):
    player_id = int(player_id)
    return flask.jsonify({
        'code': worker_manager.get_code(player_id),
        'options': {},       # Game options
        'state': None,
    })

def run_game(port):
    global worker_manager

    print("Running game...")
    settings = pickle.loads(os.environ['settings'])

    api_url = os.environ.get('GAME_API_URL', 'http://localhost:8000/players/api/games/')
    generator = getattr(map_generator, settings['GENERATOR'])(settings)
    player_manager = AvatarManager()
    game_state = generator.get_game_state(player_manager)

    turn_manager = ConcurrentTurnManager(game_state=game_state, end_turn_callback=send_world_update, completion_url=api_url+'complete/')
    WorkerManagerClass = WORKER_MANAGERS[os.environ.get('WORKER_MANAGER', 'local')]
    worker_manager = WorkerManagerClass(game_state=game_state, users_url=api_url, port=port)

    worker_manager.start()
    turn_manager.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    socketio.init_app(app, resource=os.environ.get('SOCKETIO_RESOURCE', 'socket.io'))

    run_game(int(sys.argv[2]))

    socketio.run(
        app,
        debug=False,
        host=sys.argv[1],
        port=int(sys.argv[2]),
        use_reloader=False,
    )
