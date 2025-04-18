from Classes.HTTP_request import HTTP_request
from Classes.HTTP_reply import HTTP_reply
from ObjectManager.StreamManager import *

def createHttpRequest(time: float, streamId: int, frameType: str, method: str, path: str, length: int, priority: int, incremental: bool, resource: str) -> HTTP_request:
    request = HTTP_request(
        time=time,
        streamId=streamId,
        frameType=frameType,
        method=method,
        path=path,
        length=length,
        priority=priority,
        incremental=incremental,
        resource=resource
        )
    return request 


def createHttpReply(time: float, streamId: int, frameType: str, code: str, length: int, priority: int, incremental: bool, resource: str) -> HTTP_reply:
    reply = HTTP_reply(
        time=time,
        streamId=streamId,
        frameType=frameType,
        code=code,
        length=length,
        priority=priority,
        incremental=incremental,
        resource=resource
        )
    return reply 

def requestIsHeaderFrame(request: HTTP_request)-> bool:
    return request.frameType == "headers"

def replyIsHeaderFrame(reply: HTTP_reply)-> bool:
    return reply.frameType == "headers"

