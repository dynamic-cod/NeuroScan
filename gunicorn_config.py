import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'neuroscan'

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Hook application code
def on_starting(server):
    """Log that Gunicorn is starting."""
    server.log.info("Starting NeuroScan application server")

def on_reload(server):
    """Log that Gunicorn is reloading."""
    server.log.info("Reloading NeuroScan application server")

def post_fork(server, worker):
    """Clean up after forking worker process."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Pre-fork initialization."""
    pass

def pre_exec(server):
    """Pre-exec initialization."""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Log when server is ready."""
    server.log.info("Server is ready. Spawning workers")