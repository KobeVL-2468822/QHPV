from Classes.Packet import Packet
from Classes.Stream import Stream
from typing import List
from ObjectManager.StreamManager import *


def create_packet(time: float, packet_type: str, packet_number: str, length: int, payload_length: int, total_frames: int, total_frames_length: int, direction: int, streams: List[Stream]) -> Packet:
    packet = Packet(
        time=time,
        packet_type=packet_type,
        packet_number=packet_number,
        length=length,
        payload_length=payload_length,
        total_frames=total_frames,
        total_frames_length=total_frames_length,
        direction=direction,
        streams=streams
    )
    return packet