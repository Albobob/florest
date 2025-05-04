import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # 2*кол-во ядер + 1
worker_class = "sync"
timeout = 60
loglevel = "info"
accesslog = "/var/www/florest/logs/gunicorn_access.log"
errorlog = "/var/www/florest/logs/gunicorn_error.log"