import threading
from typing import Optional
from pkg_trainmote.models.Action import Action
from pkg_trainmote.actions.actionInterface import ActionInterface
import time

class TimerThread(threading.Thread):

    seconds = 0

    def __init__(self, interval: int, callback):
        threading.Thread.__init__(self)
        self.seconds = interval
        self.kill = threading.Event()
        self.callback = callback

    def run(self):
        time.sleep(self.seconds)
        if self.callback is not None:
            self.callback()

class TimerAction(ActionInterface):

    __action: Optional[Action] = None
    timer: Optional[TimerThread] = None
    __seconds: int = 0

    def __init__(self, action: Action) -> None:
        self.__action = action

    def prepareAction(self):
        if self.__action is not None:
            hhSeconds = int(self.__action.values[0]) * 3600
            mmSeconds = int(self.__action.values[1]) * 60
            self.__seconds = + hhSeconds + mmSeconds + int(self.__action.values[2])
            print(self.__seconds)

    def runAction(self, _callback):
        TimerThread(self.__seconds, _callback)

    def cancelAction(self):
        self.timer.join()
        self.timer.kill.set()
        pass


# class BaseThread(threading.Thread):
#     def __init__(self, callback=None, callback_args=None, *args, **kwargs):
#         target = kwargs.pop('target')
#         super(BaseThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
#         self.callback = callback
#         self.method = target
#         self.callback_args = callback_args

#     def target_with_callback(self):
#         self.method()
#         if self.callback is not None:
#             self.callback(*self.callback_args)
