#!/bin/bash

# Variables
PROJECT_DIR="/home/symon/Projects/BookNest-Server"
VENV_DIR="$PROJECT_DIR/venv"
FLASK_APP="app.py"
NGINX_CONF="/etc/nginx/sites-available/booknest"
NGINX_LINK="/etc/nginx/sites-enabled/booknest"

# Update and install necessary packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx

# Set up virtual environment
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install Flask
pip install Flask gunicorn

# Create Gunicorn systemd service file
sudo bash -c 'cat > /etc/systemd/system/booknest.service <<EOF
[Unit]
Description=Gunicorn instance to serve BookNest
After=network.target

[Service]
User='$USER'
Group=www-data
WorkingDirectory='$PROJECT_DIR'
Environment="PATH='$VENV_DIR'/bin"
ExecStart='$VENV_DIR'/bin/gunicorn --workers 3 --bind unix:booknest.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF'

# Start and enable the Gunicorn service
sudo systemctl start booknest
sudo systemctl enable booknest

# Configure Nginx
sudo bash -c 'cat > '$NGINX_CONF' <<EOF
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:'$PROJECT_DIR'/booknest.sock;
    }
}
EOF'

# Enable the Nginx configuration
sudo ln -s $NGINX_CONF $NGINX_LINK

# Test Nginx configuration and restart
sudo nginx -t
sudo systemctl restart nginx
