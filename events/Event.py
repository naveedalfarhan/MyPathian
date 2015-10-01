from abc import ABCMeta, abstractmethod

__author__ = 'brian'

class Event(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self):
        pass