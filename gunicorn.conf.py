
"""
Production Gunicorn Configuration for NVC Banking Platform
Optimized for performance, reliability, and security
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5
graceful_timeout = 30

# Restart workers after this many seconds to prevent memory leaks
max_worker_age = 3600

# Logging configuration
loglevel = "info"
# Use standard output for logs (can be overridden by environment variables)
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "nvc_banking_platform"

# Server mechanics
preload_app = True
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in production)
# keyfile = None
# certfile = None

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("NVC Banking Platform server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called just after a worker has been forked."""
    worker.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    pass

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    pass

def pre_exec(server):
    """Called just before a new master process is forked."""
    pass
