from typing import Optional, List, Dict, Any
from .Action import Action
from types import SimpleNamespace
import json
from pkg_trainmote.validators.validator import Validator

class Program():

    def __init__(
        self,
        uid: Optional[str],
        actions: List[Action],
        name: Optional[str]
    ):
        self.uid = uid
        self.actions = actions
        self.name = name

    def to_dict(self):
        return {
            "uid": self.uid,
            "actions": [action.to_dict() for action in self.actions],
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], id: str):
        actions: List[Action] = []
        for action in data.get("actions"):
            actions.append(Action.from_dict(action))

        program = cls(
            id,
            actions,
            str(data.get("name"))
        )
        return program

    @classmethod
    def from_Json(cls, data: Any):
        if Validator().validateDict(data, "program_scheme") is True:
            mProgram = json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))
            if hasattr(mProgram, 'uid'): 
                return cls(mProgram.uid, mProgram.actions, mProgram.name)
            else:
                return cls(None, mProgram.actions, mProgram.name)
        else:
            raise ValueError("Invalid json")

class UpdateProgramRequest():

    def __init__(
        self,
        program: Program,
        actionsToDelete: List[str]
    ):
        self.program = program
        self.actionsToDelete = actionsToDelete

    @classmethod
    def from_Json(cls, data: Any, uid: str):
        if Validator().validateDict(data, "program_update_scheme") is True:
            mRequest = json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))
            mProgram = Program.from_dict(data["program"], uid)
            return cls(mProgram, mRequest.actionsToDelete)
        else:
            raise ValueError("Invalid json")
