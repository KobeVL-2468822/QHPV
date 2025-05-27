from typing import Any
from ObjectManager.StreamManager import *


def get_priority_and_incremental_values(headers: dict[Any, Any]) -> tuple[int, bool]:
    priority_str = headers.get("priority", None)
    if(priority_str == None):
        priority_str = headers.get("Priority", None)
    elif(priority_str == None):
        priority_str = headers.get("PRIORITY", None)

    # Default values
    priority=3
    incremental = False
    priority_explicit = False

    if priority_str is not None:
        try:
            priority = int(priority_str.split("=")[-1].split(",")[0])
            priority_explicit = True
        except ValueError:
            priority = 3 # No info -> default value
            incremental = "i" in priority_str
    return priority, incremental, priority_explicit



