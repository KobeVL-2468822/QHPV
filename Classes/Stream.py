from dataclasses import dataclass
from typing import List


@dataclass
class Stream:
    ID: int 
    offset: int #
    length: int #total length/data transmitted in stream
    fin: bool  #transport:packet_send/packet_received
    packet_count: int    #total amount of packets that contained this stream
    http_frame_count: int #total amount of http:frame_parsed/frame_created entries with this stream
    init_priority: int   # initial value of priority
    init_incremental: bool # initial value of increment
    resource: str       # requested resource
    fully_created: bool
    priority_history: List[int]
    priority_history_timestamps: List[float]

