FROM ros:humble

RUN apt-get update
RUN apt-get install -y --no-install-recommends curl gnupg ca-certificates
RUN curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2-testing/ubuntu $(lsb_release -cs) main" \
  | tee /etc/apt/sources.list.d/ros2-testing.list
RUN rm -rf /var/lib/apt/lists/*

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=ros
ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    git \
    curl \
    nano \
    bash-completion \
    build-essential \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-rosdep-modules \
    tmux \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y --no-install-recommends \
#    libudev1 \
#    && rm -rf /var/lib/apt/lists/*

RUN (addgroup --gid ${GID} ${USERNAME} || true) \
    && (id -u ${USERNAME} >/dev/null 2>&1 || adduser --uid ${UID} --gid ${GID} --disabled-password --gecos "" ${USERNAME}) \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && (addgroup dialout || true) \
    && usermod -a -G dialout ${USERNAME}

ENV WS=/home/${USERNAME}/ros2_ws
ENV ROS_WS=${WS}

RUN mkdir -p ${ROS_WS}/src/external ${ROS_WS}/src/local

COPY external/ ${ROS_WS}/src/external/
COPY local/ ${ROS_WS}/src/local/
COPY start.sh /home/${USERNAME}/start.sh
COPY bash_aliases.sh /home/${USERNAME}/.bash_aliases.sh

RUN chmod +x /home/${USERNAME}/start.sh \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

RUN mkdir -p /home/${USERNAME}/.colcon \
    && chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.colcon

RUN python3 -m pip install --no-cache-dir --upgrade pip wheel 'setuptools<75' \
    && python3 -m pip install --no-cache-dir tmule

RUN rosdep init || true

USER ${USERNAME}
WORKDIR ${ROS_WS}

RUN sed -i 's/^#\(force_color_prompt\)/\1/' /home/${USERNAME}/.bashrc

RUN grep -qxF 'source ~/.bash_aliases.sh' /home/${USERNAME}/.bashrc || echo 'source ~/.bash_aliases.sh' >> /home/${USERNAME}/.bashrc

CMD ["/bin/bash"]
