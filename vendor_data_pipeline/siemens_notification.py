__author__ = 'gopikrishnan'


import sys
import time
from siemens_post_handler  import  *

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sc=SiemensGrouper()
'''
Extend FileSystemEventHandler to be able to write custom on_any_event method
'''
class MyHandler(FileSystemEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''


    def on_created(self, event):
        filename=event.src_path[len(watch_directory)+1:len(event.src_path)]
        sc.run([filename])

    #def on_deleted(self, event):
        #print("deleted: " + event.src_path)

    #def on_modified(self, event):
        #print("modified: " + event.src_path)

    #def on_moved(self, event):
        #print("moved/renamed: " + event.src_path)


#watch_directory = "/pathian/site/db"      # Get watch_directory parameter
watch_directory= sc.siemens_xml_folder


def start_service():
    event_handler = MyHandler()
    #print("\n\n----------\n\ninside start_service")
    #print watch_directory

    observer = Observer()
    observer.schedule(event_handler, watch_directory, True)
    observer.setDaemon(True)
    observer.start()

    '''
    Keep the script running or else python closes without stopping the observer
    thread and this causes an error.
    '''

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



