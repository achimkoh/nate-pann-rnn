#!/bin/bash

cd www && python3 -m http.server && cd .. &
python3 sample-body.py
python3 sample-title.py
python3 bot.py
pkill python3 -m http.server
