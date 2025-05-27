from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet
from Classes.Stream import Stream
from typing import List
from ObjectManager.StreamManager import *
from ObjectManager.HttpFrameManager import *
from ObjectManager.PacketManager import *
from .Filters import *



def follow_stream(stream_id: int, requests: List[HTTP_request], replies: List[HTTP_reply], packets_received: List[Packet], packets_send: List[Packet], receive_streams: List[Stream], send_streams: List[Stream]) -> None:
    requests = get_requests_of_stream(stream_id, requests)
    replies = get_replies_of_stream(stream_id, replies)
    packets_received = get_packets_of_stream(stream_id, packets_received)
    packets_send = get_packets_of_stream(stream_id, packets_send)
    receive_stream = search_stream(stream_id, receive_streams)
    send_stream = search_stream(stream_id, send_streams)

    print(f"Following stream {stream_id}")
    print(receive_stream)
    for req in requests:
        print(req)
    for packet in packets_received:
        print(packet)
    print(send_stream)
    for rep in replies:
        print(rep)
    for packet in packets_send:
        print(packet)


# Compares the received requests with the send replies priories
def detect_priority_change(receive_streams: List[Stream], send_streams: List[Stream], mode: str) -> None:
    if mode == "SERVER":
        detect_priority_change_server(receive_streams, send_streams)
    elif mode == "CLIENT":
        detect_priority_change_client(receive_streams, send_streams)
    else:
        print(f"Mode not detected: {mode}")


def detect_priority_change_server(receive_streams: List[Stream], send_streams: List[Stream]):
    lone_streams: List[Stream] = []
    for rs in receive_streams:
        ss_found = False
        for ss in send_streams:
            if rs.ID == ss.ID:
                ss_found = True
                if (len(rs.priority_history) > 0 and len(ss.priority_history) > 0):
                    if rs.priority_history[0] == ss.priority_history[-1]:
                        print(f"Server kept priority for stream {rs.ID} - {rs.priority_history[0]}")
                    else:
                        print(f"Server changed priority for Stream {rs.ID} - from {rs.priority_history[0]} to {ss.priority_history[-1]}")
                        print(f"PriorityHistory: Receive - {rs.priority_history}, Send - {ss.priority_history}")
                else:
                    print(f"Not enough stream information found for Stream {rs.ID}")
            if ss_found:
                break
        if ss_found == False:
            lone_streams.append(rs)

def detect_priority_change_client(receive_streams: List[Stream], send_streams: List[Stream]):
    lone_streams: List[Stream] = []
    for rs in receive_streams:
        ss_found = False
        for ss in send_streams:
            if rs.ID == ss.ID:
                ss_found = True
                if (len(rs.priority_history) > 0 and len(ss.priority_history) > 0):
                    if ss.priority_history[0] == rs.priority_history[-1]:
                        print(f"Server kept priority for stream {rs.ID} - {ss.priority_history[0]}")
                    else:
                        print(f"Server changed priority for Stream {rs.ID} - from {ss.priority_history[0]} to {rs.priority_history[-1]}")
                        print(f"PriorityHistory: Send - {ss.priority_history}, Receive - {rs.priority_history}")
                else:
                    print(f"Not enough stream information found for Stream {rs.ID}")
            if ss_found:
                break
        if ss_found == False:
            lone_streams.append(rs)