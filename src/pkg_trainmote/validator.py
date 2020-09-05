from typing import List


class Validator:

    def validateDict(self, dictionary: dict, keys: List[str]):
        for key in keys:
            if key not in dictionary:
                return False

        return True
