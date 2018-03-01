#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/Desktop/carnivora
sudo route add default gw 192.168.178.1
sudo git pull
sudo python3 manage.py runserver 192.168.178.30:8000 --noreload
cd /
