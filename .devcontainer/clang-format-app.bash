#!/bin/bash
source /home/bot/.bashrc

find /home/bot/src/ -iname *.hh -o -iname *.cc | xargs /usr/bin/clang-format -style=file
