# Ensure bashrc forces colourful prompt
#sed -i 's/\#force_color_prompt=yes/force_color_prompt=yes/g' ~/.bashrc

# Add some shortcuts
export RCUTILS_CONSOLE_OUTPUT_FORMAT="{severity}: {message}"
function build () {
    cd /workspaces/limo_ros2/ ;
    colcon build --merge-install --symlink-install --packages-select $@ ;
    cd $OLDPWD ;
}
alias t='tmux'
function gs () { git status . ; }
function vm () { tmule -c /workspaces/limo_ros2/src/custom_packages/verbaliser/new_tmule/chat.tmule.yaml $1 ; }
function tm () { tmule -c /workspaces/limo_ros2/src/custom_packages/my_limo/tmule/talky.tmule.yaml $1 ; }
function mu () { tmule -c /workspaces/limo_ros2/src/custom_packages/my_limo/tmule/$1.tmule.yaml $2 ; }
function vr () { tmule -c /workspaces/limo_ros2/src/custom_packages/vrviz/tmule/example.tmule.yaml $1 ; }

echo "Included tmule file shorcuts:"
echo "  - [vm] communication through elevenlabs and gpt"
echo "  - [tm] dev space for chat + nav"
echo "  - [mu] \$1=[duckling,mapping,navigation,talky,tmapping]"
echo "  - [vr] for running with vrviz renderer"

function topogoal () { ros2 action send_goal /topological_navigation topological_navigation_msgs/action/GotoNode "{target: $1}" ; }

# Default some envvars
export OPENAI_PROMPT="You are a small robot which drives around office rooms to deliver mail, your name is LIMO."
export ELEVENLABS_VOICE="Paul"

export DOCKER_ESPEAK=true
export ALSA_OUTPUT='hw:2,0'
export ALSA_INPUT='hw:3,0'

export DISPLAY=:0

export DUCK="TAIL"

# Any configuration exports for this specific robot should be stored in the following:
source /workspaces/limo_ros2/src/custom_packages/my_limo/bash/robot_specific_config.sh

# Any usernames, passwords, API keys, ip addresses or ports should be stored in secrets.sh
source /workspaces/limo_ros2/src/custom_packages/my_limo/bash/secrets.sh
