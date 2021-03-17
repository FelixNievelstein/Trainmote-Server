from pkg_trainmote.actions.actionInterface import ActionInterface
from pkg_trainmote.actions.clockAction import ClockAction, ClockThread
from pkg_trainmote.models.Action import Action, ActionType
from pkg_trainmote.actions.setSwitchAction import SetSwitchAction
from pkg_trainmote.actions.setStopAction import SetStopAction
from pkg_trainmote.actions.timerAction import TimerAction
from typing import Optional

def getProgramAction(action: Action) -> Optional[ActionInterface]:
    if action.type == ActionType.TM_SET_SWITCH.value:
        return SetSwitchAction(action)
    elif action.type == ActionType.TM_SET_STOP.value:
        return SetStopAction(action)
    elif action.type == ActionType.TM_PERFORM_TIMER.value:
        return TimerAction(action)
    elif action.type == ActionType.TM_PERFORM_ALARM.value:
        return ClockAction(action)
    return None
