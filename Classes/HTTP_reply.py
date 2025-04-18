from dataclasses import dataclass

@dataclass
class HTTP_reply:
    time: float
    streamId: int
    frameType: int
    code: str
    length: int
    priority: int
    incremental: bool
    resource: str