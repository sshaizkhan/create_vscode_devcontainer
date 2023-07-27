FROM osrf/ros:humble-desktop-full

# Setting up packages for devops
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
lsb-release \
net-tools \
iputils-ping \
apt-utils \
build-essential \
psmisc \
vim-gtk \
scons \
bison \
flex \
git \
wget \
sudo \
keyboard-configuration \
 && rm -rf /var/lib/apt/lists/*

ARG USERNAME=bot
ARG PASSWORD=""

ENV USER_NAME=$USERNAME
ENV PASSWORD=$PASSWORD

RUN adduser --ingroup sudo --disabled-password --gecos "" --shell /bin/bash --home /home/$USER_NAME $USER_NAME
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN if [ ! -z "$PASSWORD" ]; then echo $USER_NAME:$PASSWORD | chpasswd; fi
ENV HOME /home/$USER_NAME
USER $USER_NAME

RUN rosdep update
RUN sudo apt update

RUN sudo apt install python3-colcon-common-extensions
RUN sudo apt install python3-colcon-mixin
RUN sudo apt-get install -y mesa-utils

RUN sudo apt install python3-vcstool

CMD [ "bash" ]
