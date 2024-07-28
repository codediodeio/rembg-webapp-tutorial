import multiprocessing

max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = "0.0.0.0:5100"

workers = 4
# use the next line to dynamically set the number of workers based on the number of CPUs
# workers = (multiprocessing.cpu_count() * 2) + 1
threads = workers
timeout = 120
