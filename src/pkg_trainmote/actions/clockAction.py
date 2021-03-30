import threading
from typing import Optional
from pkg_trainmote.models.Action import Action
from pkg_trainmote.actions.actionInterface import ActionInterface
import time
from datetime import datetime, timedelta, date

class ClockThread(threading.Thread):

    mDate = None

    def __init__(self, mDate: datetime, callback):
        threading.Thread.__init__(self)
        self.mDate = mDate
        self.kill = threading.Event()
        self.callback = callback

    def run(self):
        if self.mDate is not None:
            now = datetime.now()
            while now < self.mDate:
                diff = (self.mDate - now).total_seconds()
                if diff > 60:
                    time.sleep(60)
                elif diff > 0:
                    time.sleep(1)
                now = datetime.now()

            if self.callback is not None:
                self.callback()


class ClockAction(ActionInterface):

    __action: Optional[Action] = None
    timer: Optional[ClockThread] = None
    __date: datetime = datetime.now()

    def __init__(self, action: Action) -> None:
        self.__action = action

    def prepareAction(self):
        if self.__action is not None:
            hhValue = int(self.__action.inputs[0])
            hour = 0
            if hhValue <= 23 and hhValue >= 0:
                hour = hhValue

            mmValue = int(self.__action.inputs[1])
            minutes = 0
            if mmValue <= 59 and mmValue >= 0:
                minutes = mmValue

            ssValue = int(self.__action.inputs[1])
            seconds = 0
            if ssValue <= 59 and ssValue >= 0:
                seconds = ssValue

            now = datetime.now()
            self.__date = datetime(now.year, now.month, now.day, hour, minutes, seconds)
            if self.__date < datetime.now():
                tomorrow = date.today() + timedelta(days=1)
                self.__date = datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, minutes, seconds)

            print(self.__date)

    def runAction(self, _callback):
        self.timer = ClockThread(self.__date, _callback)
        self.timer.start()

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
