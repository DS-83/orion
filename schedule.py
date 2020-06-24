import logging
import threading


#
# @with_logging
# def job():
#     print("I'm running on thread %s" % threading.current_thread())
#
#
# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()
#
# schedule.every(3).seconds.do(run_threaded, job)
#
# while 1:
#     schedule.run_continuously()
#     time.sleep(1)


# def worker():
#     w = threading.Timer(20.0, worker)
#     logging.info('LOG: Running job "%s"' % __name__)
#     print("Hello, World!")
#     w.start()
# worker()
#
# import sched, time
# s = sched.scheduler(time.time, time.sleep)
# def do_something(sc):
#     print("Doing stuff...")
#     # do your stuff
#     s.enter(60, 1, do_something, (sc,))
#
# s.enter(60, 1, do_something, (s,))
# s.run()
# w.Timer(15.0, worker).start() # called every minute
