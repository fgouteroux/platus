# -*- coding: utf-8 -*-
import os
from multiprocessing import cpu_count

bind = '0.0.0.0:5001'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'

max_requests = 1000

workers = cpu_count()
timeout = os.getenv("WORKER_TIMEOUT", 30)
