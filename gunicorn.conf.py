# gunicorn.conf.py
workers = 3
bind = "0.0.0.0:8000"
module = "your_app:app"

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Worker options
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
