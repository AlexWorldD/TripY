#!/usr/bin/env bash

# Simple script for required packages such as Erlang/RabitMQ and et.
sudo ufw allow 27017
sudo ufw allow 15672
sudo ufw allow 5672
sudo apt-get install pip3
sudo pip3 install -r requirements.txt




