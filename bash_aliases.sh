#!/usr/bin/env bash

if [ -f /opt/ros/humble/setup.bash ]; then
  source /opt/ros/humble/setup.bash
fi

if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
  source "$HOME/ros2_ws/install/setup.bash"
fi

export ROS_WS="$HOME/ros2_ws"

export RCUTILS_CONSOLE_OUTPUT_FORMAT="{severity}: {message}"
export RCUTILS_COLORIZED_OUTPUT=1

alias nano='nano -BEPOUWx -T 4'
alias t='tmux'

export JOY_CONFIG=/home/ros/ros2_ws/src/local/my_limo/config/logitech.yaml 
export JOY_DEV='/dev/input/js0'
export JOY_DEV_ID=0


# export ROBOT_NAME=$(hostname | sed 's|-|_|g')

# export MQTT_BROKER_IP=''
# export MQTT_BROKER_PORT=''
# export MQTT_ENCODING='json'

# export ALSA_INPUT="hw:3,0"
# export ALSA_OUTPUT="hw:2,0"
# export DOCKER_ESPEAK=True

# export ENVIRONMENT_TEMPLATE='/home/ros/ros2_ws/src/custom_packages/environment_template'
# source $ENVIRONMENT_TEMPLATE/config/environment.sh
# export TMAP_FILE_WRITE=$ENVIRONMENT_TEMPLATE/config/topological/network.tmap2.yaml

# export RVIZ_CONFIG="/home/ros/ros2_ws/src/custom_packages/my_limo/config/display.rviz2.yaml"

# export VRVIZ_TABLE_CONFIG=$RVIZ_CONFIG
# export VRVIZ_MQTT_BROKER_IP=""
# export VRVIZ_MQTT_BROKER_PORT="8883"
# export VRVIZ_MQTT_CLIENT_NAME="vrviz_limo_server"
# export VRVIZ_MQTT_BROKER_NAMESPACE="vrviz"

# # Any configuration exports for this specific robot should be stored in the following:
# source $MY_LIMO/bash/robot_specific_config.sh

# # Any usernames, passwords, API keys, ip addresses or ports should be stored in secrets.sh
# source $MY_LIMO/bash/secrets.sh