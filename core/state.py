import json
from pathlib import Path

from .config import STATE_FILE


class StateManager:
    """
    Manages the persistence of the proxy application state.
    """

    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file

    def get_state(self):
        """
        Read the current proxy state from the JSON file.

        Returns:
            dict: A dictionary containing the state of all running proxies.
        """
        if Path(self.state_file).exists():
            try:
                with Path(self.state_file).open() as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_state(self, state):
        """
        Save the current proxy state to the JSON file.

        Args:
            state (dict): The state dictionary to save.
        """
        with Path(self.state_file).open("w") as f:
            json.dump(state, f, indent=4)
