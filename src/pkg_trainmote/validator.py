from typing import List, Dict


class Validator:

    def validateDict(self, dictionary: Dict[str, str], keys: List[str]):
        for key in keys:
            if dictionary.get(key) is None:
                return False

        return True
