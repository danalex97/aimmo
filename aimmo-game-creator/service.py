#!/usr/bin/env python
import logging
import os

from worker_manager import WORKER_MANAGERS


def main():
    logging.basicConfig(level=logging.DEBUG)

    if "aimmo-game-creator" in os.environ.get("HOSTNAME", ''):
        os.environ["GAME_API_URL"] = "https://staging-dot-decent-digit-629.appspot.com/aimmo/api/games/"
        os.environ["WORKER_MANAGER"] = "kubernetes"

    WorkerManagerClass = WORKER_MANAGERS[os.environ.get('WORKER_MANAGER', 'local')]
    worker_manager = WorkerManagerClass(os.environ.get('GAME_API_URL',
                                        'http://localhost:8000/players/api/games/'))
    worker_manager.run()

if __name__ == '__main__':
    main()
