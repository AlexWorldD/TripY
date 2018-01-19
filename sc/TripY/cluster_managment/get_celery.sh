#!/usr/bin/env bash

# Simple script for required packages such as Erlang/RabitMQ and et.
sudo ufw allow 27017
sudo ufw allow 15672
sudo ufw allow 5672
sudo pip install -r requirements.txt




