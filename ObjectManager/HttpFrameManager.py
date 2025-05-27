from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply
from ObjectManager.StreamManager import *

def create_http_request(time: float, stream_id: int, frame_type: str, method: str, path: str, length: int, priority: int, incremental: bool, resource: str) -> HTTP_request:
    request = HTTP_request(
        time=time,
        stream_id=stream_id,
        frame_type=frame_type,
        method=method,
        path=path,
        length=length,
        priority=priority,
        incremental=incremental,
        resource=resource
        )
    return request 


def create_http_reply(time: float, stream_id: int, frame_type: str, code: str, length: int, priority: int, incremental: bool, resource: str) -> HTTP_reply:
    reply = HTTP_reply(
        time=time,
        stream_id=stream_id,
        frame_type=frame_type,
        code=code,
        length=length,
        priority=priority,
        incremental=incremental,
        resource=resource
        )
    return reply 

def request_is_header_frame(request: HTTP_request)-> bool:
    return request.frame_type == "headers"

def reply_is_header_frame(reply: HTTP_reply)-> bool:
    return reply.frame_type == "headers"

