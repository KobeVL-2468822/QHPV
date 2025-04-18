from dataclasses import dataclass
from typing import List


@dataclass
class Stream:
    ID: int 
    offset: int #
    length: int #total length/data transmitted in stream
    fin: bool  #transport:packet_send/packet_received
    packetCount: int    #total amount of packets that contained this stream
    httpFrameCount: int #total amount of http:frame_parsed/frame_created entries with this stream
    initPriority: int   # initial value of priority
    initIncrement: bool # initial value of increment
    resource: str       # requested resource
    fully_created: bool
    priorityHistory: List[int]

