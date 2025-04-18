from dataclasses import dataclass
from typing import List
from Classes.Stream import Stream

@dataclass
class Packet:
    time: float
    packetType: str
    packetNumber: int
    length: int
    payloadLength: int
    totalFrames: int
    totalFramesLength: int
    direction: str  # "sent" of "received"
    streams: List[Stream]  # Lijst van streams in het pakket