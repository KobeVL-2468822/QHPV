from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet
from Classes.Stream import Stream
from typing import List
from ObjectManager.StreamManager import *
from ObjectManager.HttpFrameManager import *
from ObjectManager.PacketManager import *
from .Filters import *



def follow_stream(streamId: int, requests: List[HTTP_request], replies: List[HTTP_reply], packetsReceived: List[Packet], packetsSent: List[Packet], receiveStreams: List[Stream], sendStreams: List[Stream]) -> None:
    requests = getRequestsOfStream(streamId, requests)
    replies = getRepliesOfStream(streamId, replies)
    packetsReceived = getPacketsOfStream(streamId, packetsReceived)
    packetsSent = getPacketsOfStream(streamId, packetsSent)
    receiveStream = searchStream(streamId, receiveStreams)
    sendStream = searchStream(streamId, sendStreams)

    print(f"Following stream {streamId}")
    print(receiveStream)
    for req in requests:
        print(req)
    for packet in packetsReceived:
        print(packet)
    print(sendStream)
    for rep in replies:
        print(rep)
    for packet in packetsSent:
        print(packet)


# Compares the received requests with the send replies priories
def detect_priority_change(receiveStreams: List[Stream], sendStreams: List[Stream], mode: str) -> None:
    if mode == "SERVER":
        detect_priority_change_server(receiveStreams, sendStreams)
    elif mode == "CLIENT":
        detect_priority_change_client(receiveStreams, sendStreams)
    else:
        print(f"Mode not detected: {mode}")


def detect_priority_change_server(receiveStreams: List[Stream], sendStreams: List[Stream]):
    loneStreams: List[Stream] = []
    for rs in receiveStreams:
        ssFound = False
        for ss in sendStreams:
            if rs.ID == ss.ID:
                ssFound = True
                if (len(rs.priorityHistory) > 0 and len(ss.priorityHistory) > 0):
                    if rs.priorityHistory[0] == ss.priorityHistory[-1]:
                        print(f"Server kept priority for stream {rs.ID} - {rs.priorityHistory[0]}")
                    else:
                        print(f"Server changed priority for Stream {rs.ID} - from {rs.priorityHistory[0]} to {ss.priorityHistory[-1]}")
                        print(f"PriorityHistory: Receive - {rs.priorityHistory}, Send - {ss.priorityHistory}")
                else:
                    print(f"Not enough stream information found for Stream {rs.ID}")
            if ssFound:
                break
        if ssFound == False:
            loneStreams.append(rs)

def detect_priority_change_client(receiveStreams: List[Stream], sendStreams: List[Stream]):
    loneStreams: List[Stream] = []
    for rs in receiveStreams:
        ssFound = False
        for ss in sendStreams:
            if rs.ID == ss.ID:
                ssFound = True
                if (len(rs.priorityHistory) > 0 and len(ss.priorityHistory) > 0):
                    if ss.priorityHistory[0] == rs.priorityHistory[-1]:
                        print(f"Server kept priority for stream {rs.ID} - {ss.priorityHistory[0]}")
                    else:
                        print(f"Server changed priority for Stream {rs.ID} - from {ss.priorityHistory[0]} to {rs.priorityHistory[-1]}")
                        print(f"PriorityHistory: Send - {ss.priorityHistory}, Receive - {rs.priorityHistory}")
                else:
                    print(f"Not enough stream information found for Stream {rs.ID}")
            if ssFound:
                break
        if ssFound == False:
            loneStreams.append(rs)