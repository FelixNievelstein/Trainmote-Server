from typing import Optional, Dict, Any, List
import enum

class Action():

    def __init__(
        self,
        uid: Optional[str],
        type: str,
        position: int,
        values: List[str],
        name: Optional[str]
    ):
        self.uid = uid
        self.type = type
        self.position = position
        self.name = name
        self.values = values

    def to_dict(self):
        return {
            "uid": self.uid,
            "type": self.type,
            "position": self.position,
            "values": self.values,
            "name": self.name
        }    

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        values: List[str] = []
        for value in data.get("values"):
            values.append(value)
        action = cls(
            str(data.get("uid")),
            str(data.get("type")),
            int(str(data.get("position"))),
            values,
            data.get("name")
        )
        return action


class ActionType(enum.Enum):
    TM_SET_SWITCH = "SetSwitch"
    TM_SET_STOP = "SetStop"
    TM_PERFORM_TIMER = "WaitFor"
    TM_PERFORM_ALARM = "StartAtClock"
