from dataclasses import dataclass
from typing import List
from Classes.Stream import Stream

@dataclass
class Packet:
    time: float
    packet_type: str
    packet_number: int
    length: int
    payload_length: int
    total_frames: int
    total_frames_length: int
    direction: str  # "sent" of "received"
    streams: List[Stream]  # list of streams in packet