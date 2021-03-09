from statemachine import StateMachine, State
from .models.Program import Program

class ProgramMachine(StateMachine):

    m_program: Program

    def start(self, program: Program):
        if self.is_readyForAction:
            self.m_program = program
            self.startProgram()

    readyForAction = State('readyForAction', initial=True)
    runningAction = State('RunningAction')
    actionFinished = State('ActionFinished')
    preparingAction = State('preparingAction')

    startProgram = readyForAction.to(preparingAction)
    cancelProgram = runningAction.to(readyForAction)
    endAction = runningAction.to(actionFinished)
    prepareForAction = actionFinished.to(preparingAction)
    startAction = preparingAction.to(runningAction)

    def on_startProgram(self):
        print('startProgram')
    
    def on_startAction(self):
        print('startAction')

    def on_cancelProgram(self):
        print('startAction')

    def on_endAction(self):
        print('startAction')

    def on_prepareForAction(self):
        print('on_prepareForAction')
