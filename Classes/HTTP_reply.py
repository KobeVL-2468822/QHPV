from dataclasses import dataclass

@dataclass
class HTTP_reply:
    time: float
    stream_id: int
    frame_type: int
    code: str
    length: int
    priority: int
    incremental: bool
    resource: str