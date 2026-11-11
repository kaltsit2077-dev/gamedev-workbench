from copy import deepcopy
from math import isfinite


class Settings:
    def __init__(self, writer, listener):
        self.writer = writer
        self.listener = listener
        self._values = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}
        self._applying = False

    @property
    def values(self):
        return deepcopy(self._values)

    def apply(self, changes):
        if self._applying:
            return False

        candidate = self._build_candidate(changes)
        if candidate is None:
            return False
        if candidate == self._values:
            return True

        self._applying = True
        try:
            try:
                persisted = self.writer(deepcopy(candidate))
            except BaseException:
                # The callback boundary must report failure through apply's bool result.
                return False
            if persisted is not True:
                return False

            self._values = candidate
            try:
                self.listener(deepcopy(candidate))
            except BaseException:
                # Persistence already succeeded; notification cannot undo it.
                pass
            return True
        finally:
            self._applying = False

    def _build_candidate(self, changes):
        if not isinstance(changes, dict) or not changes:
            return None
        if not set(changes) <= {"volume", "bindings"}:
            return None

        candidate = deepcopy(self._values)
        if "volume" in changes:
            volume = changes["volume"]
            if isinstance(volume, bool) or not isinstance(volume, (int, float)):
                return None
            # Check the range first so arbitrarily large ints need no float conversion.
            if not 0 <= volume <= 1 or not isfinite(volume):
                return None
            candidate["volume"] = volume

        if "bindings" in changes:
            bindings = changes["bindings"]
            if not isinstance(bindings, dict) or not bindings:
                return None
            if not set(bindings) <= {"jump", "fire"}:
                return None
            if any(not isinstance(key, str) or not key.strip() for key in bindings.values()):
                return None
            candidate["bindings"].update(bindings)
            if len(set(candidate["bindings"].values())) != len(candidate["bindings"]):
                return None

        return candidate
