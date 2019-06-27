#!/usr/bin/env python3
from worker import workerh
from apscheduler.schedulers.blocking import BlockingScheduler
print('reloj')
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every 1 minutes.')
    workerh()


sched.start()