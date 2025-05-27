from Classes.Stream import Stream
from typing import List, Optional
from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply 
from Classes.Packet import Packet


# Create a stream
def create_stream(id: int, offset: int, length: int, fin: bool, priority: int, increment: bool, resource: str, timestamp: float) -> Stream:
    stream = Stream(
        ID=id,
        offset=offset,
        length=length,
        fin=fin,
        packet_count=0,
        http_frame_count=0,
        init_priority=priority,
        init_incremental=increment,
        resource=resource,
        fully_created=True,
        priority_history=[],
        priority_history_timestamps=[]
    )
    stream.priority_history.append(priority)
    stream.priority_history_timestamps.append(timestamp)

    return stream

def create_stream_minimal_info(id: int, offset: int, increment_packet_count: bool, increment_frame_count: bool) -> Stream:
    stream = create_stream(id, offset, 0, False, 3, False, "", 0)
    # increment packet count
    if increment_packet_count:
        increment_packet_count_of_stream(stream)
    # increment frame count
    if increment_frame_count:
        increment_http_frame_count_of_stream(stream)
    # ensure stream is not labeled as fully created
    stream.fully_created=False
    return stream


# update a stream
def update_stream_by_id(id, length, fin, priority, increment, resource, timestamp, streams: List[Stream]) -> bool:
    stream = search_stream(id, streams)
    if stream != None:
        # If Stream was not fully created previously -> flush the priority_history List to prevent inconsistensies
        if stream.fully_created == False:
            stream.init_priority = priority
            stream.priority_history.clear()
            stream.priority_history_timestamps.clear()
        update_stream(length, fin, priority, increment, resource, timestamp, stream)
        return True
    return False  


def update_stream(length: int, fin: bool, priority: int, increment: bool, resource: str, timestamp: float, stream: Stream) -> Stream: 
    stream.length += length
    stream.fin = fin
    stream.init_incremental = increment
    stream.resource=resource
    stream.fully_created=True
    stream = update_priority(priority, timestamp, stream)
    return stream

# priority
def update_priority(priority: int, timestamp: float, stream: Stream) -> Stream:
    if len(stream.priority_history) > 0:
        last_priority_change = stream.priority_history[-1]
        if priority != last_priority_change:
            stream.priority_history.append(priority)
            stream.priority_history_timestamps.append(timestamp)
    else: 
        stream.priority_history.append(priority)
        stream.priority_history_timestamps.append(timestamp)

def update_priority_by_id(priority: int, timestamp: float, id: int, streams: List[Stream]) -> Stream:
    stream = search_stream(id, streams)
    if stream != None:
        stream = update_priority(priority, timestamp, stream)
        return stream
    return None

# search stream
def does_stream_exist(id: int, streams: List[Stream]) -> bool:
    return any(stream.ID == id for stream in streams)

def search_stream(id: int, streams: List[Stream]) -> Optional[Stream]:
    for stream in streams:
        if stream.ID == id:
            return stream
    return None

def is_stream_fully_created(id: int, streams: List[Stream]) -> bool:
    stream = search_stream(id, streams)
    if stream != None:
        return stream.fully_created
    return False


# packet count
def increment_packet_count_of_stream_by_id(id: int, streams: List[Stream]) -> bool:
    stream = search_stream(id, streams)
    if stream != None:
        increment_packet_count_of_stream(stream)
        return True
    return False
    
def increment_packet_count_of_stream(stream: Stream) -> Stream:
    stream.packet_count +=1
    return stream

# frame count
def increment_http_frame_count_of_stream_by_id(id: int, streams: List[Stream]) -> bool:
    stream = search_stream(id, streams)
    if stream != None:
        increment_http_frame_count_of_stream(stream)
        return True
    return False
    
def increment_http_frame_count_of_stream(stream: Stream) -> Stream:
    stream.http_frame_count +=1
    return stream

# length
def add_length_to_stream_by_id(id: int, streams: List[Stream], extra_length: int) -> bool:
    stream = search_stream(id, streams)
    if stream != None:
        add_length_to_stream(stream, extra_length)
        return True
    return False

def add_length_to_stream(stream: Stream, extra_length: int) -> Stream:
    stream.length += extra_length
    return stream

# get
def get_requests_of_stream(stream_id: int, requests: List[HTTP_request]) -> List[HTTP_request]:
    requests_of_stream: List[HTTP_request] = []
    for req in requests:
        if req.stream_id == stream_id:
            requests_of_stream.append(req)
    return requests_of_stream

def get_replies_of_stream(stream_id: int, replies: List[HTTP_reply]) -> List[HTTP_reply]:
    replies_of_stream: List[HTTP_reply] = []
    for rep in replies:
        if rep.stream_id == stream_id:
            replies_of_stream.append(rep)
    return replies_of_stream

def get_packets_of_stream(stream_id: int, packets: List[Packet]) -> List[Packet]:
    packets_of_stream: List[Packet] = []
    copy_of_packets = packets[:] #ensure packets itself wont be affected
    for packet in copy_of_packets:
        if len(packet.streams) > 0:
            streams_in_packet = [stream for stream in packet.streams if stream.ID == stream_id] 
            if streams_in_packet:
                packet.streams = streams_in_packet 
                packets_of_stream.append(packet)
    return packets_of_stream

