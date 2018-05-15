y#!/bin/bash
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/carnivora
sudo git pull
source /home/pi/tensorflow/bin/activate
sudo /home/pi/tensorflow/bin/python3 manage.py runserver 192.168.178.30:8000
cd /
