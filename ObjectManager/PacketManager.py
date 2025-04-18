from Classes.Packet import Packet
from Classes.Stream import Stream
from typing import List
from ObjectManager.StreamManager import *


def createPacket(time: float, packetType: str, packetNumber: str, length: int, payloadLength: int, totalFrames: int, totalFramesLength: int, direction: int, streams: List[Stream]) -> Packet:
    packet = Packet(
        time=time,
        packetType=packetType,
        packetNumber=packetNumber,
        length=length,
        payloadLength=payloadLength,
        totalFrames=totalFrames,
        totalFramesLength=totalFramesLength,
        direction=direction,
        streams=streams
    )
    return packet