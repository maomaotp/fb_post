#!/bin/bash
export PATH=/usr/local/bin:$PATH
path=$(dirname $0)
path=${path/\./$(pwd)}

cd $path
python fb_auto_commenter.py $1

