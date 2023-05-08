import time
import schedule
import threading


class Scheduler(object):
    registered_tasks = []

    def add(self, job, *args, **kwargs):
        def decorator(func):
            if not kwargs.get("name"):
                name = func.__name__
            else:
                name = kwargs.pop("name")

            self.registered_tasks.append(
                {"name": name, "func": func, "job": job.do(func, *args, **kwargs)}
            )

        return decorator

    def remove(self, task):
        schedule.cancel_job(task["job"])

    def _run(self):
        while not self.shutdown_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.shutdown_event = threading.Event()
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.shutdown_event.set()
        self.thread.join()
        for task in self.registered_tasks:
            schedule.cancel_job(task["job"])


scheduler = Scheduler()