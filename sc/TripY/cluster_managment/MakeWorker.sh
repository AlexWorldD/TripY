#!/usr/bin/env bash
#!/usr/bin/env bash

# Simple script for required packages such as Erlang/RabitMQ and et.

SETCOLOR_SUCCESS="echo -en \\033[1;32m"
SETCOLOR_FAILURE="echo -en \\033[1;31m"
SETCOLOR_NORMAL="echo -en \\033[0;39m"
BOLD=$(tput bold)
NORMAL_FONT=$(tput sgr0)
sudo pip install -r requirements.txt


# Firstly, update all packages
sudo apt-get install fortune cowsay
$SETCOLOR_SUCCESS
cowsay -f stegosaurus "${BOLD}Update your system... to Windows!                  ${NORMAL_FONT}"
$SETCOLOR_NORMAL
# 4th Flask
cowsay -f stegosaurus "${BOLD}Install pip...${NORMAL_FONT}"
sudo apt-get update -y
sudo apt install -y python-pip
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



# Installing Celery
cowsay -f stegosaurus "${BOLD}Install Celery...${NORMAL_FONT}"
# apt list --installed
pip install celery
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


cowsay -f stegosaurus "${BOLD}Add Celery user...${NORMAL_FONT}"

sudo adduser celery
sudo mkdir /var/log/celery/
sudo mkdir /var/run/celery/
chown -R celery:celery /var/log/celery/
chown -R celery:celery /var/run/celery/

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
cowsay -f stegosaurus "${BOLD}Build configuration files...${NORMAL_FONT}"

cd /etc/init.d/
wget https://raw.githubusercontent.com/celery/celery/3.1/extra/generic-init.d/celeryd
chmod +x celeryd
cd /home/PersonalReminderBotWorker
cp -i celeryd /etc/default/
#sudo chown celery: /root/PersonalReminderBotWorker
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

# Configure Worker
cowsay -f stegosaurus "${BOLD}Let's configure this worker! ${NORMAL_FONT}"

read -p 'Bot token: ' token
read -p 'Gateway URL: ' gt
echo  >> default_config.py
echo 'BOT_TOKEN = "'$token'"' >> default_config.py
echo  >> default_config.py
echo 'GATEWAY_URL = "'$gt'"' >> default_config.py
echo  >> default_config.py
echo 'RETRANSMISSION_URL = "'$gt'/retransmit/'$token'"' >> default_config.py
echo  >> default_config.py

read -p 'Select queue: ' mode
t_t='CELERYD_OPTS="--time-limit=300 -Q '$mode' --statedb=/var/run/celery/%n.state --autoscale=10,3"'
echo  >> /etc/default/celeryd
echo $t_t >> /etc/default/celeryd

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

echo "${BOLD}Configure RabbitMQ...${NORMAL_FONT}"
read -p 'RabbitMQ Server IP: ' ip
sed -i "s/\(\@.*\/\)/@$ip\//g" default_config.py

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


cowsay -f stegosaurus "${BOLD}Start Celery Worker...${NORMAL_FONT}"

/etc/init.d/celeryd start
#celery worker -l info -A main.celery -Q nlp,reminders --statedb=/var/run/celery/%n.state --autoscale=10,3
#celery worker -l info -A main.celery -Q nlp,reminders --autoscale=10,3

