#!/bin/bash
cd /home/ubuntu/BookNest-Server
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flaskapp
