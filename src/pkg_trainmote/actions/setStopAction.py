from typing import Optional
from pkg_trainmote.models.Action import Action
from pkg_trainmote.actions.actionInterface import ActionInterface
from pkg_trainmote import gpioservice

class SetStopAction(ActionInterface):

    __action: Optional[Action] = None

    def __init__(self, action: Action) -> None:
        self.__action = action

    def prepareAction(self):
        if self.__action is not None:
            print(self.__action.inputs[0])

    def runAction(self, _callback):
        try:
            intValue = int(self.__action.inputs[1])
            gpioservice.setStop(self.__action.inputs[0], bool(intValue))
        except Exception as err:
            print(err)
        _callback()

    def cancelAction(self):
        pass
