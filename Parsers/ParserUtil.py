from typing import Any
from ObjectManager.StreamManager import *


def getPriorityAndIncrementalValues(headers: dict[Any, Any]) -> tuple[int, bool]:
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
            # Probeer het nummer te extraheren en om te zetten naar een integer
            priority = int(priority_str.split("=")[-1].split(",")[0])
            priority_explicit = True
        except ValueError:
            # Als de conversie faalt, stel dan een standaard prioriteit in (bijv. 3)
            priority = 3
            incremental = "i" in priority_str  # 'i' geeft aan dat het incrementeel is
    return priority, incremental, priority_explicit



