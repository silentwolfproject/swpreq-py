import signal
from typing import Callable, Dict


class SignalHandler:
    def __init__(self):
        self._handlers: Dict[int, Callable] = {}
        self._installed = False

    def on(self, sig: int, callback: Callable) -> "SignalHandler":
        self._handlers[sig] = callback
        return self

    def install(self):
        if self._installed:
            return

        for sig, cb in self._handlers.items():
            signal.signal(sig, lambda s, f: cb())

        self._installed = True

    def uninstall(self):
        for sig in self._handlers:
            signal.signal(sig, signal.SIG_DFL)

        self._installed = False