import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "unix:/tmp/gunicorn.sock"
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stdout
timeout = 120
