#!/usr/bin/env bash

# Simple script for required packages such as Erlang/RabitMQ and et.

SETCOLOR_SUCCESS="echo -en \\033[1;32m"
SETCOLOR_FAILURE="echo -en \\033[1;31m"
SETCOLOR_NORMAL="echo -en \\033[0;39m"
BOLD=$(tput bold)
NORMAL_FONT=$(tput sgr0)


sudo ufw allow 27017
sudo ufw allow 15672
# Firstly, update all packages
echo "${BOLD}Update your system... to Windows 10. Thx)${NORMAL_FONT}"
wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
sudo dpkg -i erlang-solutions_1.0_all.deb
sudo apt-get update -y
sudo apt-get install -y erlang erlang-nox
if [ $? -eq 0 ]; then
    $SETCOLOR_SUCCESS
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[OK]"
    $SETCOLOR_NORMAL
    echo
else
    $SETCOLOR_FAILURE
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[fail]"
    $SETCOLOR_NORMAL
    echo
fi

# Secondly, Installing RabbitMQ
echo "${BOLD}Install RabbitMQ...${NORMAL_FONT}"
sudo apt-get install -y rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

if [ $? -eq 0 ]; then
    $SETCOLOR_SUCCESS
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[OK]"
    $SETCOLOR_NORMAL
    echo
else
    $SETCOLOR_FAILURE
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[fail]"
    $SETCOLOR_NORMAL
    echo
fi

echo "${BOLD}Enable RabbitMQ plugins...${NORMAL_FONT}"
sudo rabbitmqctl add_user radmin a
sudo rabbitmqctl set_user_tags radmin administrator
sudo rabbitmqctl set_permissions -p / radmin ".*" ".*" ".*"
sudo rabbitmq-plugins enable rabbitmq_management


# 5th
echo "${BOLD}Add Worker users...${NORMAL_FONT}"
# add new user
sudo rabbitmqctl add_user worker w
# add new virtual host
sudo rabbitmqctl add_vhost vhost
# set permissions for user on vhost
sudo rabbitmqctl set_permissions -p vhost worker ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p vhost radmin ".*" ".*" ".*"

if [ $? -eq 0 ]; then
    $SETCOLOR_SUCCESS
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[OK]"
    $SETCOLOR_NORMAL
    echo
else
    $SETCOLOR_FAILURE
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[fail]"
    $SETCOLOR_NORMAL
    echo
fi


# Return url for management console
echo "${BOLD}RabbitMQ web management console${NORMAL_FONT}"
$SETCOLOR_SUCCESS
ip route get 8.8.8.8 | awk '{a = $NF; print "URL: " a ":15672"; exit}'
$SETCOLOR_NORMAL
echo

if [ $? -eq 0 ]; then
    $SETCOLOR_SUCCESS
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[OK]"
    $SETCOLOR_NORMAL
    echo
else
    $SETCOLOR_FAILURE
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[fail]"
    $SETCOLOR_NORMAL
    echo
fi

# Return url for management console
echo "${BOLD}RabbitMQ amqp address${NORMAL_FONT}"
$SETCOLOR_SUCCESS
ip route get 8.8.8.8 | awk '{a = $NF; print "URL: " a ":5672"; exit}'
$SETCOLOR_NORMAL
echo

if [ $? -eq 0 ]; then
    $SETCOLOR_SUCCESS
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[OK]"
    $SETCOLOR_NORMAL
    echo
else
    $SETCOLOR_FAILURE
    echo -n "$(tput hpa $(tput cols))$(tput cub 6)[fail]"
    $SETCOLOR_NORMAL
    echo
fi
