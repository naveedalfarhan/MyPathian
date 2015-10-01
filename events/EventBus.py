from collections import deque
import thread

__author__ = 'brian'

class EventBus:
    event_queue = None
    th = None
    lock = None

    @classmethod
    def publish(cls, event):
        if cls.lock is None:
            cls.lock = thread.allocate_lock()

        if cls.event_queue is None:
            cls.event_queue = deque()

        cls.lock.acquire()
        cls.event_queue.append(event)
        cls.lock.release()

        if cls.th is None:
            th = thread.start_new_thread(cls.run_tasks,())

    @classmethod
    def run_tasks(cls):
        while cls.event_queue:
            cls.lock.acquire()
            event = cls.event_queue.popleft()
            cls.lock.release()
            event.handle()
