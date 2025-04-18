from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet
from typing import List


# returns only requests that have a method and replies that have a length !=0
def filter_lists(requests: List[HTTP_request], replies: List[HTTP_reply]) -> tuple[List[HTTP_request], List[HTTP_reply]]:
    filteredRequests: List[HTTP_request] = []
    filteredReplies: List[HTTP_reply] = []
    for req in requests:
        if(req.method!=""):
            filteredRequests.append(req)

    for rep in replies:
        if(rep.length!=0):
            filteredReplies.append(rep)

    return filteredRequests, filteredReplies


# return only packets with a length that has a value of >0
def filter_packets(packets: List[Packet]) -> List[Packet]:
    packetList: List[Packet] = []
    for packet in packets:
        if len(packet.streams) >0:
            packetList.append(packet)
    return packetList

