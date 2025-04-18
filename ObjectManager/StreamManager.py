from Classes.Stream import Stream
from typing import List, Optional
from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet


# Create a stream
def createStream(id: int, offset: int, length: int, fin: bool, priority: int, increment: bool, resource: str) -> Stream:
    stream = Stream(
        ID=id,
        offset=offset,
        length=length,
        fin=fin,
        packetCount=0,
        httpFrameCount=0,
        initPriority=priority,
        initIncrement=increment,
        resource=resource,
        fully_created=True,
        priorityHistory=[]
    )
    stream.priorityHistory.append(priority)

    return stream

def createStreamMinimalInfo(id: int, offset: int, incrementPacketCount: bool, incrementFrameCount: bool) -> Stream:
    stream = createStream(id, offset, 0, False, 3, False, "")
    # increment packet count
    if incrementPacketCount:
        incrementPacketCountOfStream(stream)
    # increment frame count
    if incrementFrameCount:
        incrementHttpFrameCountOfStream(stream)
    # ensure stream is not labeled as fully created
    stream.fully_created=False
    return stream


# update a stream
def updateStreamById(id, length, fin, priority, increment, resource, streams: List[Stream]) -> bool:
    stream = searchStream(id, streams)
    if stream != None:
        # If Stream was not fully created previously -> flush the priorityHistory List to prevent inconsistensies
        if stream.fully_created == False:
            stream.initPriority = priority
            stream.priorityHistory.clear()
        updateStream(length, fin, priority, increment, resource, stream)
        return True
    return False  


def updateStream(length: int, fin: bool, priority: int, increment: bool, resource: str, stream: Stream) -> Stream: 
    stream.length += length
    stream.fin = fin
    stream.initIncrement = increment
    stream.resource=resource
    stream.fully_created=True
    stream = updatePriority(priority, stream)
    return stream

# priority
def updatePriority(priority: int, stream: Stream) -> Stream:
    if len(stream.priorityHistory) > 0:
        lastPriorityChange = stream.priorityHistory[-1]
        if priority != lastPriorityChange:
            stream.priorityHistory.append(priority)
    else: 
        stream.priorityHistory.append(priority)

def updatePriorityById(priority: int, id: int, streams: List[Stream]) -> Stream:
    stream = searchStream(id, streams)
    if stream != None:
        stream = updatePriority(priority, stream)
        return stream
    return None

# search stream
def doesStreamExist(id: int, streams: List[Stream]) -> bool:
    return any(stream.ID == id for stream in streams)

def searchStream(id: int, streams: List[Stream]) -> Optional[Stream]:
    for stream in streams:
        if stream.ID == id:
            return stream
    return None

def isStreamFullyCreated(id: int, streams: List[Stream]) -> bool:
    stream = searchStream(id, streams)
    if stream != None:
        return stream.fully_created
    return False


# packet count
def incrementPacketCountOfStreamById(id: int, streams: List[Stream]) -> bool:
    stream = searchStream(id, streams)
    if stream != None:
        incrementPacketCountOfStream(stream)
        return True
    return False
    
def incrementPacketCountOfStream(stream: Stream) -> Stream:
    stream.packetCount +=1
    return stream

# frame count
def incrementHttpFrameCountOfStreamById(id: int, streams: List[Stream]) -> bool:
    stream = searchStream(id, streams)
    if stream != None:
        incrementHttpFrameCountOfStream(stream)
        return True
    return False
    
def incrementHttpFrameCountOfStream(stream: Stream) -> Stream:
    stream.httpFrameCount +=1
    return stream

# length
def addLengthToStreamById(id: int, streams: List[Stream], extraLength: int) -> bool:
    stream = searchStream(id, streams)
    if stream != None:
        addLengthToStream(stream, extraLength)
        return True
    return False

def addLengthToStream(stream: Stream, extraLength: int) -> Stream:
    stream.length += extraLength
    return stream

# get
def getRequestsOfStream(streamId: int, requests: List[HTTP_request]) -> List[HTTP_request]:
    requestsOfStream: List[HTTP_request] = []
    for req in requests:
        if req.streamId == streamId:
            requestsOfStream.append(req)
    return requestsOfStream

def getRepliesOfStream(streamId: int, replies: List[HTTP_reply]) -> List[HTTP_reply]:
    repliesOfStream: List[HTTP_reply] = []
    for rep in replies:
        if rep.streamId == streamId:
            repliesOfStream.append(rep)
    return repliesOfStream

def getPacketsOfStream(streamId: int, packets: List[Packet]) -> List[Packet]:
    packetsOfStream: List[Packet] = []
    copyOfPackets = packets[:] #ensure packets itself wont be affected
    for packet in copyOfPackets:
        if len(packet.streams) > 0:
            streamsInPacket = [stream for stream in packet.streams if stream.ID == streamId] 
            if streamsInPacket:
                packet.streams = streamsInPacket 
                packetsOfStream.append(packet)
    return packetsOfStream

