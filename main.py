from ObjectManager.StreamManager import *
from Parsers.Parser import parse_json_seq_file
from DataFunctions.Filters import *
from DataFunctions.AdditionalFunctions import *

MODE = "SERVER"
PRIORITY_LOG_MODE = "ONLY_CHANGE"

"""
"frame_type":"stream","stream_id":12,
,"name":"http:frame_parsed","data":{"stream_id":4,
"""


#requests, replies, packetsReceived, packetsSent, receiveStreams, sendStreams  = parse_json_seq_file(".\qlogs\server-5ba009964413f00b574cd4d4fbea93a4d54b4719.sqlog")

MODE = "CLIENT"
requests, replies, packetsReceived, packetsSent, receiveStreams, sendStreams  = parse_json_seq_file(".\\qlogs\\aioquic.sqlog", PRIORITY_LOG_MODE)

requests, replies = filter_lists(requests, replies)
packetsReceived = filter_packets(packetsReceived)
packetsSent = filter_packets(packetsSent)

#follow_stream(288, requests, replies, packetsReceived, packetsSent, receiveStreams, sendStreams)

"""
# Debug output
print("HTTP Requests:")
for req in requests:
    print(req)

print("\nHTTP Replies:")
for rep in replies:
    print(rep)

print("\npacketsReceived:")
for rec in packetsReceived:
    print(rec)

print("\npacketsSent:")
for sen in packetsSent:
    print(sen)

"""

print("\nReceiveStreams")
for rs in receiveStreams:
    print(rs)

print("\nSendStreams")
for ss in sendStreams:
    print(ss)


detect_priority_change(receiveStreams, sendStreams, MODE)
#detect_priority_change(sendStreams, receiveStreams)

#"""