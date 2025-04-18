from dataclasses import dataclass

@dataclass
class HTTP_request:
    time: float
    streamId: int
    frameType: int
    method: str
    path: str
    length: int
    priority: int
    incremental: bool
    resource: str
    
