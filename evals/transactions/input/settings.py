class Settings:
    def __init__(self, writer, listener):
        self.writer = writer
        self.listener = listener
        self._values = {"volume": 0.5, "bindings": {"jump": "Space", "fire": "J"}}

    @property
    def values(self):
        return self._values

    def apply(self, changes):
        self._values.update(changes)
        self.writer(self._values)
        self.listener(self._values)
        return True
