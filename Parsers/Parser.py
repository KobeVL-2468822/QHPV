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




def http_frame_parsed_parser(obj: Any, receive_streams: List[Stream], requests: List[HTTP_request], priority_log_mode: str) -> None:
    frame = obj.get("data", {}).get("frame", {})
    headers = {h["name"]: h["value"] for h in frame.get("headers", [])}
    path = next((h["value"] for h in frame.get("headers", []) if h["name"] == ":path"), None)
    timestamp = obj['time']

    _priority, _incremental, _explicitFlag = get_priority_and_incremental_values(headers)

    request = create_http_request(obj["time"], obj["data"]["stream_id"], frame.get("frame_type", 0), 
                                headers.get(":method", ""), headers.get(":path", ""), int(headers.get("content-length", 0)),
                                _priority, _incremental, path)

    if search_stream(request.stream_id, receive_streams):
        if(is_stream_fully_created(request.stream_id, receive_streams)):
            increment_http_frame_count_of_stream_by_id(request.stream_id, receive_streams)
            add_length_to_stream_by_id(request.stream_id, receive_streams, request.length)
            if (priority_log_mode=="ONLY_CHANGE" and _explicitFlag==False):
                None
            else: 
                update_priority_by_id(_priority, timestamp, request.stream_id, receive_streams )
        else:
            if(request_is_header_frame(request)):
                update_stream_by_id(request.stream_id, request.length, False, request.priority, request.incremental, request.resource, timestamp, receive_streams)
            increment_http_frame_count_of_stream_by_id(request.stream_id, receive_streams)
    else:
        if(request_is_header_frame(request)):
            stream = create_stream(request.stream_id, 0, request.length, False, request.priority, request.incremental, request.resource, timestamp)
            stream = increment_http_frame_count_of_stream(stream)
        else:
            stream = create_stream_minimal_info(request.stream_id, 0, False, True)     
        
        receive_streams.append(stream)

    requests.append(request)


def http_frame_created_parser(obj: Any, send_streams: List[Stream], replies: List[HTTP_reply], priority_log_mode: str) -> None:
    frame = obj.get("data", {}).get("frame", {})
    headers = {h["name"]: h["value"] for h in frame.get("headers", [])}
    path = next((h["value"] for h in frame.get("headers", []) if h["name"] == ":path"), None)
    timestamp = obj['time']

    _priority, _incremental, _explicitFlag = get_priority_and_incremental_values(headers)

    reply = create_http_reply(obj["time"], obj["data"]["stream_id"], frame.get("frame_type", 0), 
                                headers.get(":status", ""), int(headers.get("content-length", 0)),
                                _priority, _incremental, path)

    if search_stream(reply.stream_id, send_streams):
        if(is_stream_fully_created(reply.stream_id, send_streams)):
            increment_http_frame_count_of_stream_by_id(reply.stream_id, send_streams)
            add_length_to_stream_by_id(reply.stream_id, send_streams, reply.length)
            if (priority_log_mode=="ONLY_CHANGE" and _explicitFlag==False):
                None
            else: 
                update_priority_by_id(_priority, timestamp, reply.stream_id, send_streams )

        else:
            if(reply_is_header_frame(reply)):
                update_stream_by_id(reply.stream_id, reply.length, False, reply.priority, reply.incremental, reply.resource, timestamp, send_streams)
            increment_http_frame_count_of_stream_by_id(reply.stream_id, send_streams)
    else:
        if(reply_is_header_frame(reply)):
            stream = create_stream(reply.stream_id, 0, reply.length, False, reply.priority, reply.incremental, reply.resource, timestamp)
            stream = increment_http_frame_count_of_stream(stream)

        else:
            stream = create_stream_minimal_info(reply.stream_id, 0, False, True)    
        send_streams.append(stream)

    replies.append(reply)


def transport_packet_parser(obj: Any, packets_received: List[Packet], packets_send: List[Packet], receive_streams: List[Stream], send_streams: List[Stream]) -> None:
    data = obj.get("data", {})
    header = data.get("header", {})
    raw = data.get("raw", {})
    frames = data.get("frames", [])

    total_frames_length = sum(frame.get("length", 0) for frame in frames if "length" in frame)

    streams = [
        Stream(
            ID=frame["stream_id"], offset=frame.get("offset", 0), length=frame.get("length", 0),
            fin=frame.get("fin", False), packet_count=0, http_frame_count=0, init_priority=0,
            init_incremental=False, resource="", fully_created=True, priority_history=[], priority_history_timestamps=[])
        for frame in frames if frame.get("frame_type") == "stream"
    ]
    
    packet = create_packet(obj["time"], header.get("packet_type", ""), header.get("packet_number", 0),
                          raw.get("length", 0), raw.get("payload_length", 0), len(frames),
                          total_frames_length, "received" if obj.get("name") == "transport:packet_received" else "sent", streams)


    if obj.get("name") == "transport:packet_received":
        transport_packet_received_parser(packet, receive_streams, packets_received)

    else:
        transport_packet_send_parser(packet, send_streams, packets_send)


def transport_packet_received_parser(packet: Packet, receive_streams: List[Stream], packets_received: List[Packet]):
    for stream in packet.streams:
            if(increment_packet_count_of_stream_by_id(stream.ID, receive_streams)==False):
                stream = create_stream_minimal_info(stream.ID, stream.offset, True, False)
                receive_streams.append(stream)
    packets_received.append(packet)


def transport_packet_send_parser(packet: Packet, send_streams: List[Stream], packets_send: List[Packet]):
    for stream in packet.streams:
            if(increment_packet_count_of_stream_by_id(stream.ID, send_streams)==False):
                stream = create_stream_minimal_info(stream.ID, stream.offset, True, False)
                send_streams.append(stream)
    packets_send.append(packet)









def parse_sqlog_json_seq_file(file_path: Any, priority_log_mode: str) -> tuple[List[HTTP_request], List[HTTP_reply], List[Packet], List[Packet], List[Stream], List[Stream]]:
    requests: List[HTTP_request] = []
    replies: List[HTTP_reply] = []
    packets_received: List[Packet] = []
    packets_send: List[Packet] = []
    receive_streams: List[Stream] = []
    send_streams: List[Stream] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("\x1E"):  # JSON-SEQ header
                line = line[1:]

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # Invalid JSON

            # Ignore object without "name"
            if "name" not in obj:
                continue

            event_name = obj["name"]

            if event_name == "http:frame_parsed":
                http_frame_parsed_parser(obj, receive_streams, requests, priority_log_mode)

            elif event_name == "http:frame_created":
                http_frame_created_parser(obj, send_streams, replies, priority_log_mode)

            elif event_name in ["transport:packet_received", "transport:packet_sent"]:
                transport_packet_parser(obj, packets_received, packets_send, receive_streams, send_streams)

    return requests, replies, packets_received, packets_send, receive_streams, send_streams


def get_normalized_last_timestamps_sqlog(file_path: Any) -> float:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    first_time = None
    last_time = None

    for line in lines:
        line = line.strip()
        if line.startswith("\x1E"):      # JSON-SEQ header
            line = line[1:]

        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        if "time" in obj:
            time_value = obj["time"]
            if first_time is None:
                first_time = time_value
            last_time = time_value

    if first_time is None or last_time is None:
        raise ValueError("No valid timestamps could be found.")

    return last_time - first_time


import json
from typing import Any, List


def parse_qlog_file(file_path: Any, priority_log_mode: str) -> tuple[List[HTTP_request], List[HTTP_reply], List[Packet], List[Packet], List[Stream], List[Stream]]:
    requests: List[HTTP_request] = []
    replies: List[HTTP_reply] = []
    packets_received: List[Packet] = []
    packets_send: List[Packet] = []
    receive_streams: List[Stream] = []
    send_streams: List[Stream] = []

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Invalid .qlog file.")

    traces = data.get("traces", [])
    for trace in traces:
        events = trace.get("events", [])
        for obj in events:
            if "name" not in obj:
                continue

            event_name = obj["name"]

            if event_name == "http:frame_parsed":
                http_frame_parsed_parser(obj, receive_streams, requests, priority_log_mode)

            elif event_name == "http:frame_created":
                http_frame_created_parser(obj, send_streams, replies, priority_log_mode)

            elif event_name in ["transport:packet_received", "transport:packet_sent"]:
                transport_packet_parser(obj, packets_received, packets_send, receive_streams, send_streams)

    return requests, replies, packets_received, packets_send, receive_streams, send_streams


def get_normalized_last_timestamp_qlog(file_path: Any) -> float:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Invalid .qlog file.")

    traces = data.get("traces", [])
    first_time = None
    last_time = None

    for trace in traces:
        events = trace.get("events", [])
        for event in events:
            if "time" in event:
                time_value = event["time"]
                if first_time is None:
                    first_time = time_value
                last_time = time_value

    if first_time is None or last_time is None:
        raise ValueError("No valid timestamps could be found.")

    return last_time - first_time



def is_qlog_file(file_path: str) -> bool:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            obj = json.load(f)
            return obj.get("qlog_format") == "JSON"
        except Exception:
            return False

def parse_log_file(file_path: str, priority_log_mode: str) -> tuple[List[HTTP_request], List[HTTP_reply], List[Packet], List[Packet], List[Stream], List[Stream]]:
    if (is_qlog_file(file_path)):
        return parse_qlog_file(file_path, priority_log_mode)
    else:
        return parse_sqlog_json_seq_file(file_path, priority_log_mode)
    

def get_normalized_last_timestamp(file_path: str) -> float:
    if (is_qlog_file(file_path)):
        return get_normalized_last_timestamp_qlog(file_path)
    else:
        return get_normalized_last_timestamps_sqlog(file_path)