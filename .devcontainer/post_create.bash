#!/bin/bash

#update and upgrade any installed packages
sudo apt update
sudo apt -y upgrade

# Install terminator
sudo apt-get install -y terminator

#install nano
sudo apt-get -y install nano


colcon --log-base "./colcon-log" mixin add default "file://`pwd`//workspace_name/src/application_name/.devcontainer/colcon_mixins/index.yaml"

sudo chown -R bot:bot /home/bot

ln -s /home/bot/workspace_name/src/application_name/.devcontainer/.vscode/ /home/bot/.vscode

# link the container settings
mkdir -p /home/bot/.vscode-server/data/Machine
ln -s /home/bot/workspace_name/src/application_name/.devcontainer/settings.json /home/bot/.vscode-server/data/Machine/settings.json

# install Terminator config
mkdir -p /home/bot/.config/terminator
ln -s /home/bot/workspace_name/src/application_name/.devcontainer/terminator.config /home/bot/.config/terminator/config

# link .bashrc
rm /home/bot/.bashrc
ln -s /home/bot/workspace_name/src/application_name/.devcontainer/.bashrc /home/bot/.bashrc

# link .bash_aliases
# rm /home/bot/.bash_aliases
ln -s /home/bot/workspace_name/src/application_name/.devcontainer/.bash_aliases /home/bot/.bash_aliases