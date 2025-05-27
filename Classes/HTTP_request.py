from dataclasses import dataclass

@dataclass
class HTTP_request:
    time: float
    stream_id: int
    frame_type: int
    method: str
    path: str
    length: int
    priority: int
    incremental: bool
    resource: str
    
