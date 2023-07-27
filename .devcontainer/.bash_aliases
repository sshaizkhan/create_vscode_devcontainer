#!/bin/bash

function clean_processes() {
  sudo pkill -9 gzclient
  sudo pkill -9 gzserver
  sudo pkill -9 _ros2_daemon
  sudo pkill -9 rviz
}

function set_new_log_dir() {
  export ROS_LOG_DIR=~/src/logs/log_dir_$(date '+%Y_%m_%d_%H_%M_%S')
  mkdir -p $ROS_LOG_DIR
  rm ~/src/logs/latest
  ln -s $ROS_LOG_DIR ~/src/logs/latest
}

function set_log_to_latest() {
  export ROS_LOG_DIR=~/src/logs/latest
}
