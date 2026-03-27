#!/usr/bin/env bash
set -eo pipefail

TOTAL_SLEEP_TIME="${SLEEP_TIME:-${1:-infinity}}"

echo "Sourcing /opt/ros/humble/setup.bash"
source /opt/ros/humble/setup.bash

cd "$HOME/ros2_ws"

if [ ! -f "$MARKER_FILE" ]; then
    echo -e "\n\n\nRunning apt update\n"
    sudo apt-get update -q

    echo -e "\n\n\nRunning ROSDep Update\n"
    rosdep update

    echo -e "\n\n\nRunning ROSDep Install\n"
    rosdep install --from-paths src --ignore-src -r -y --skip-keys "gazebo_ros gazebo_plugins"

    echo -e "\n\n\nBuilding Colcon Workspace at /home/ros/ros2_ws\n"
    colcon build --symlink-install --packages-skip ydlidar_ros2_driver limo_gazebosim limo_speaker voice_control astra_camera astra_camera_msgs limo_msgs

    echo -e "\n\n\nMarking first run complete\n"
    touch "$MARKER_FILE"
else
    echo -e "\n\n\nFirst run already completed — skipping setup steps\n"
fi


echo -e "\n\n\nSourcing built workspace\n"
[ -f "$HOME/ros2_ws/install/setup.bash" ] && source "$HOME/ros2_ws/install/setup.bash"

if [ -f "$HOME/ros2_ws/install/setup.bash" ]; then
  echo "Sourcing workspace overlay"
  source "$HOME/ros2_ws/install/setup.bash"
fi

if [ -n "${TMULE_FILE:-}" ]; then
  echo "Launching tmule with TMULE_FILE=${TMULE_FILE}"
  tmule -c "$TMULE_FILE" launch
else
  echo "TMULE_FILE is not set, skipping tmule launch"
fi

echo "Sleeping for ${TOTAL_SLEEP_TIME}"
sleep "${TOTAL_SLEEP_TIME}"

if [ -n "${TMULE_FILE:-}" ]; then
  echo "Terminating tmule with TMULE_FILE=${TMULE_FILE}"
  tmule -c "$TMULE_FILE" terminate
else
  echo "TMULE_FILE is not set, skipping tmule terminate"
fi
