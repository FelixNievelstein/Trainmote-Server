from sqlite3.dbapi2 import DatabaseError, Error
from statemachine import StateMachine, State

from pkg_trainmote.actions.actionInterface import ActionInterface
from .models.Program import Program
from .models.Action import Action
from typing import Optional, List
from .actions import actionHelper

class ProgramMachine(StateMachine):

    program: Optional[Program] = None
    __action_index: int = 0
    __actionInterface: Optional[ActionInterface] = None
    __currentAction: Optional[Action] = None

    isRunning: bool = False

    readyForAction = State('readyForAction', initial=True)
    runningAction = State('RunningAction')
    actionFinished = State('ActionFinished')
    preparingAction = State('preparingAction')

    startProgram = readyForAction.to(preparingAction)
    cancelProgram = runningAction.to(readyForAction)
    endAction = runningAction.to(actionFinished)
    prepareForAction = actionFinished.to(preparingAction)
    startAction = preparingAction.to(runningAction)
    endProgram = preparingAction.to(readyForAction)

    def start(self, program: Program):
        if program.name is not None:
            print("Start " + program.name)

        if self.is_readyForAction:
            self.program = program
            self.startProgram()
        else:
            raise Error("A program is already running.")

    def on_startProgram(self):
        self.isRunning = True
        self.__currentAction = self.loadAction()

    def on_enter_runningAction(self):
        def actionCallback():
            self.endAction()

        self.__actionInterface.runAction(actionCallback)

    def on_cancelProgram(self):
        self.isRunning = False
        self.program = None
        if self.__actionInterface is not None:
            self.__actionInterface.cancelAction()
        self.__action_index = 0

    def on_endAction(self):
        self.__action_index = self.__action_index + 1
        self.__currentAction = self.loadAction()

    def on_enter_actionFinished(self):
        self.prepareForAction()

    def on_enter_preparingAction(self):
        self.prepare()

    def prepare(self):
        if self.__currentAction is not None:
            self.__actionInterface = actionHelper.getProgramAction(self.__currentAction)
            if self.__actionInterface is not None:
                self.__actionInterface.prepareAction()
                self.startAction()
                return
        self.endProgram()

    def on_endProgram(self):
        print('Program End')
        self.isRunning = False
        self.program = None
        self.__action_index = 0

##
#
##
    def getCurrentAction(self) -> Optional[Action]:
        return self.__currentAction

##
#   Load the action for the current __action_index.
##
    def loadAction(self) -> Optional[Action]:
        if self.program is not None and self.__action_index < len(self.program.actions):
            return self.program.actions[self.__action_index]
        return None

##
# Returns the following actions of the program
##
    def followingActions(self) -> List[Action]:
        if self.program is not None and self.__action_index < len(self.program.actions):
            return self.program.actions[self.__action_index + 1:]
        return []
