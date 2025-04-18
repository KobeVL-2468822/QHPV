import json
from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet
from Classes.Stream import Stream
from typing import Any, List
from ObjectManager.StreamManager import *
from ObjectManager.HttpFrameManager import *
from ObjectManager.PacketManager import *
from .ParserUtil import *




def httpFrameParsedParser(obj: Any, receiveStreams: List[Stream], requests: List[HTTP_request], priority_log_mode: str) -> None:
    frame = obj.get("data", {}).get("frame", {})
    headers = {h["name"]: h["value"] for h in frame.get("headers", [])}
    path = next((h["value"] for h in frame.get("headers", []) if h["name"] == ":path"), None)

    _priority, _incremental, _explicitFlag = getPriorityAndIncrementalValues(headers)

    request = createHttpRequest(obj["time"], obj["data"]["stream_id"], frame.get("frame_type", 0), 
                                headers.get(":method", ""), headers.get(":path", ""), int(headers.get("content-length", 0)),
                                _priority, _incremental, path)

    if searchStream(request.streamId, receiveStreams):
        if(isStreamFullyCreated(request.streamId, receiveStreams)):
            incrementHttpFrameCountOfStreamById(request.streamId, receiveStreams)
            addLengthToStreamById(request.streamId, receiveStreams, request.length)
            if (priority_log_mode=="ONLY_CHANGE" and _explicitFlag==False):
                None
            else: 
                updatePriorityById(_priority, request.streamId, receiveStreams )
        else:
            if(requestIsHeaderFrame(request)):
                updateStreamById(request.streamId, request.length, False, request.priority, request.incremental, request.resource, receiveStreams)
            incrementHttpFrameCountOfStreamById(request.streamId, receiveStreams)
    else:
        if(requestIsHeaderFrame(request)):
            stream = createStream(request.streamId, 0, request.length, False, request.priority, request.incremental, request.resource)
            stream = incrementHttpFrameCountOfStream(stream)
        else:
            stream = createStreamMinimalInfo(request.streamId, 0, False, True)     
        
        receiveStreams.append(stream)

    requests.append(request)


def httpFrameCreatedParser(obj: Any, sendStreams: List[Stream], replies: List[HTTP_reply], priority_log_mode: str) -> None:
    frame = obj.get("data", {}).get("frame", {})
    headers = {h["name"]: h["value"] for h in frame.get("headers", [])}
    path = next((h["value"] for h in frame.get("headers", []) if h["name"] == ":path"), None)

    _priority, _incremental, _explicitFlag = getPriorityAndIncrementalValues(headers)

    reply = createHttpReply(obj["time"], obj["data"]["stream_id"], frame.get("frame_type", 0), 
                                headers.get(":status", ""), int(headers.get("content-length", 0)),
                                _priority, _incremental, path)

    if searchStream(reply.streamId, sendStreams):
        if(isStreamFullyCreated(reply.streamId, sendStreams)):
            incrementHttpFrameCountOfStreamById(reply.streamId, sendStreams)
            addLengthToStreamById(reply.streamId, sendStreams, reply.length)
            if (priority_log_mode=="ONLY_CHANGE" and _explicitFlag==False):
                None
            else: 
                updatePriorityById(_priority, reply.streamId, sendStreams )

        else:
            if(replyIsHeaderFrame(reply)):
                updateStreamById(reply.streamId, reply.length, False, reply.priority, reply.incremental, reply.resource, sendStreams)
            incrementHttpFrameCountOfStreamById(reply.streamId, sendStreams)
    else:
        if(replyIsHeaderFrame(reply)):
            stream = createStream(reply.streamId, 0, reply.length, False, reply.priority, reply.incremental, reply.resource)
            stream = incrementHttpFrameCountOfStream(stream)

        else:
            stream = createStreamMinimalInfo(reply.streamId, 0, False, True)    
        sendStreams.append(stream)

    replies.append(reply)


def transportPacketParser(obj: Any, packetsReceived: List[Packet], packetsSend: List[Packet], receiveStreams: List[Stream], sendStreams: List[Stream]) -> None:
    data = obj.get("data", {})
    header = data.get("header", {})
    raw = data.get("raw", {})
    frames = data.get("frames", [])

    totalFramesLength = sum(frame.get("length", 0) for frame in frames if "length" in frame)

    # Maak een lijst van Stream objecten voor dit pakket
    streams = [
        Stream(
            ID=frame["stream_id"], offset=frame.get("offset", 0), length=frame.get("length", 0),
            fin=frame.get("fin", False), packetCount=0, httpFrameCount=0, initPriority=0,
            initIncrement=False, resource="", fully_created=True, priorityHistory=[])
        for frame in frames if frame.get("frame_type") == "stream"
    ]
    
    packet = createPacket(obj["time"], header.get("packet_type", ""), header.get("packet_number", 0),
                          raw.get("length", 0), raw.get("payload_length", 0), len(frames),
                          totalFramesLength, "received" if obj.get("name") == "transport:packet_received" else "sent", streams)


    if obj.get("name") == "transport:packet_received":
        transportPacketReceivedParser(packet, receiveStreams, packetsReceived)

    else:
        transportPacketSendParser(packet, sendStreams, packetsSend)



def transportPacketReceivedParser(packet: Packet, receiveStreams: List[Stream], packetsReceived: List[Packet]):
    for stream in packet.streams:
            if(incrementPacketCountOfStreamById(stream.ID, receiveStreams)==False):
                stream = createStreamMinimalInfo(stream.ID, stream.offset, True, False)
                receiveStreams.append(stream)
    packetsReceived.append(packet)


def transportPacketSendParser(packet: Packet, sendStreams: List[Stream], packetsSend: List[Packet]):
    for stream in packet.streams:
            if(incrementPacketCountOfStreamById(stream.ID, sendStreams)==False):
                stream = createStreamMinimalInfo(stream.ID, stream.offset, True, False)
                sendStreams.append(stream)
    packetsSend.append(packet)







def parse_json_seq_file(file_path: Any, priority_log_mode: str) -> tuple[List[HTTP_request], List[HTTP_reply], List[Packet], List[Packet], List[Stream], List[Stream]]:
    requests: List[HTTP_request] = []
    replies: List[HTTP_reply] = []
    packetsReceived: List[Packet] = []
    packetsSent: List[Packet] = []
    receiveStreams: List[Stream] = []
    sendStreams: List[Stream] = []


    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("\x1E"):  # Verwijder JSON-SEQ scheidingsteken
                line = line[1:]

            try:
                obj = json.loads(line)
                if obj.get("name") == "http:frame_parsed":
                    httpFrameParsedParser(obj, receiveStreams, requests, priority_log_mode)
                    
                elif obj.get("name") == "http:frame_created":
                    httpFrameCreatedParser(obj, sendStreams, replies, priority_log_mode)

                elif obj.get("name") in ["transport:packet_received", "transport:packet_sent"]:
                    transportPacketParser(obj, packetsReceived, packetsSent, receiveStreams, sendStreams)
                   
            except json.JSONDecodeError:
                continue  # Sla ongeldige JSON-regels over

    return requests, replies, packetsReceived, packetsSent, receiveStreams, sendStreams
