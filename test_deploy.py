from __future__ import print_function

import os
import docker

# open the connection to the cloud application
os.system("gcloud container clusters get-credentials dev --zone europe-west1-b --project decent-digit-629")

# creting docker images
env = {
    'DOCKER_HOST': 'tcp://192.168.42.29:2376',
    'DOCKER_TLS_VERIFY': '1',
    'DOCKER_CERT_PATH': '/home/alexandrudan1/.minikube/certs',
    'DOCKER_API_VERSION': '1.23'
}
client = docker.from_env(
    environment=env,
    version='auto',
)

def build_docker_image(client, path):
    status = client.build(
        decode=True,
        path=path
    )
    for line in status:
        if 'stream' in line:
            print(line['stream'], end='')

print("Building docker images.")
build_docker_image(client, "./aimmo-game-creator")
build_docker_image(client, "./aimmo-game")
build_docker_image(client, "./aimmo-game-worker")

print("Removing old pods and replication contrllers.")
os.system("kubectl delete rc --all")
os.system("kubectl delete pods --all")
# os.system("kubectl delete service --all")

print("Creating a new replication controller for game creator...")
os.system("kubectl create -f ./aimmo-game-creator/rc-aimmo-game-creator.yaml")

print("Done.")
