from typing import Optional, Dict, Any, List
import enum

class Action():

    def __init__(
        self,
        uid: Optional[str],
        type: Optional[str],
        position: Optional[int],
        inputs: Optional[List[str]],
        name: Optional[str]
    ):
        self.uid = uid
        self.type = type
        self.position = position
        self.name = name
        self.inputs = inputs

    def to_dict(self):
        return {
            "uid": self.uid,
            "type": self.type,
            "position": self.position,
            "inputs": self.inputs,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if "inputs" in data.keys():
            inputs: List[str] = []
            for value in data.get("inputs"):
                inputs.append(value)
            return cls(
                None if data.get("uid") is None else str(data.get("uid")),
                None if data.get("type") is None else str(data.get("type")),
                None if data.get("position") is None else int(str(data.get("position"))),
                inputs,
                data.get("name")
            )
        else:
            return cls(
                None if data.get("uid") is None else str(data.get("uid")),
                None if data.get("type") is None else str(data.get("type")),
                None if data.get("position") is None else int(str(data.get("position"))),
                None,
                data.get("name")
            )


class ActionType(enum.Enum):
    TM_SET_SWITCH = "SetSwitch"
    TM_SET_STOP = "SetStop"
    TM_PERFORM_TIMER = "WaitFor"
    TM_PERFORM_ALARM = "StartAtClock"
