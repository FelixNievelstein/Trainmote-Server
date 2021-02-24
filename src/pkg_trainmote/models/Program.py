from typing import Optional, List, Dict, Any
from .Action import Action

class Program():

    def __init__(
        self,
        uid: str,
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
