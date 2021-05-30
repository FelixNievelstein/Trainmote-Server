from typing import Optional
from pkg_trainmote.models.Program import Program
from .programMachine import ProgramMachine

programMachine = ProgramMachine()

##
# Method to get current running program. If no program running method returns None.
##
def getRunningProgramm() -> Optional[Program]:
    if programMachine.isRunning:
        return programMachine.program
    else:
        return None
