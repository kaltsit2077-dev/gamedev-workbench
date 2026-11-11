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
        if not isinstance(changes, dict) or not changes:
            return False
        if any(key not in ("volume", "bindings") for key in changes):
            return False

        candidate = deepcopy(self._values)
        if "volume" in changes:
            volume = changes["volume"]
            if (
                isinstance(volume, bool)
                or not isinstance(volume, (int, float))
                or not 0 <= volume <= 1
                or not isfinite(volume)
            ):
                return False
            candidate["volume"] = volume

        if "bindings" in changes:
            patch = changes["bindings"]
            if not isinstance(patch, dict) or not patch:
                return False
            for action, binding in patch.items():
                if action not in ("jump", "fire"):
                    return False
                if not isinstance(binding, str) or not binding.strip():
                    return False
                candidate["bindings"][action] = binding
            if candidate["bindings"]["jump"] == candidate["bindings"]["fire"]:
                return False

        if candidate == self._values:
            return True

        self._applying = True
        try:
            try:
                persisted = self.writer(deepcopy(candidate))
            except Exception:
                return False
            if persisted is not True:
                return False

            # This is the only commit point; observers see the persisted state.
            self._values = candidate
            try:
                self.listener(deepcopy(candidate))
            except Exception:
                # Notification failure cannot undo a completed persistence.
                pass
            return True
        finally:
            self._applying = False
