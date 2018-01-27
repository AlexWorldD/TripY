#!/usr/bin/env bash

# Simple script for required packages such as Erlang/RabitMQ and et.
sudo ufw allow 27017
sudo ufw allow 15672
sudo ufw allow 5672
sudo sudo apt-get update && sudo apt-get -y upgrade
sudo cd ~/TripY
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt




