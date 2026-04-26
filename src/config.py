"""Application configuration — loads/saves config.json with sensible defaults."""

import json
import os
from typing import Any


DEFAULTS = {
    "debug": False,
    "camera_index": 0,
    "auto_detect": True,
    "scan_interval": 350,
    "scan_cooldown": 1.5,
    "flash": True,
    "sound": False,
}


class Config:
    def __init__(self):
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config.json",
        )
        self.debug_mode: bool = DEFAULTS["debug"]
        self.camera_index: int = DEFAULTS["camera_index"]
        self.auto_detect: bool = DEFAULTS["auto_detect"]
        self.scan_interval: int = DEFAULTS["scan_interval"]
        self.scan_cooldown: float = DEFAULTS["scan_cooldown"]
        self.flash: bool = DEFAULTS["flash"]
        self.sound: bool = DEFAULTS["sound"]
        self.load_config()

    def load_config(self):
        """Load config from disk; bootstrap defaults if file missing/invalid."""
        data: dict = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
            except (json.JSONDecodeError, OSError) as exc:
                print(f"[config] could not parse {self.config_path}: {exc}")
                data = {}

        self.debug_mode = bool(data.get("debug", DEFAULTS["debug"]))
        self.camera_index = int(data.get("camera_index", DEFAULTS["camera_index"]))
        self.auto_detect = bool(data.get("auto_detect", DEFAULTS["auto_detect"]))
        self.scan_interval = int(data.get("scan_interval", DEFAULTS["scan_interval"]))
        self.scan_cooldown = float(data.get("scan_cooldown", DEFAULTS["scan_cooldown"]))
        self.flash = bool(data.get("flash", DEFAULTS["flash"]))
        self.sound = bool(data.get("sound", DEFAULTS["sound"]))

        # Always re-write so a missing/empty/corrupt file is healed on first run.
        self.save_config()

    def update_setting(self, key: str, value: Any) -> bool:
        if key == "camera_index":
            self.camera_index = int(value)
        elif key == "debug_mode":
            self.debug_mode = bool(value)
        elif key == "auto_detect":
            self.auto_detect = bool(value)
        elif key == "scan_interval":
            self.scan_interval = int(value)
        elif key == "scan_cooldown":
            self.scan_cooldown = float(value)
        elif key == "flash":
            self.flash = bool(value)
        elif key == "sound":
            self.sound = bool(value)
        else:
            return False
        self.save_config()
        return True

    def save_config(self):
        data = {
            "debug": self.debug_mode,
            "camera_index": self.camera_index,
            "auto_detect": self.auto_detect,
            "scan_interval": self.scan_interval,
            "scan_cooldown": self.scan_cooldown,
            "flash": self.flash,
            "sound": self.sound,
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as exc:
            print(f"[config] could not write {self.config_path}: {exc}")
