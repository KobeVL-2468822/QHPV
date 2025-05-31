from ObjectManager.StreamManager import *
from Parsers.Parser import parse_log_file, get_normalized_last_timestamp
from DataFunctions.Filters import *
from DataFunctions.AdditionalFunctions import *
from PlotFunctions.PlotFunctions import *
from operator import attrgetter


### TODO:

### CONFIGS
MODE = "CLIENT"                         # CLIENT || SERVER
PRIORITY_LOG_MODE = "ONLY_CHANGE"       # for servers that only return the urgency of a resource in the first packet
SHOW_DEBUG_HTTP_REQUESTS = False
SHOW_DEBUG_HTTP_REPLIES = False
SHOW_DEBUG_PACKETS_SEND = False
SHOW_DEBUG_PACKETS_RECEIVED = False
SHOW_DEBUG_STREAMS_SEND = False
SHOW_DEBUG_STREAMS_RECEIVED = False
DEBUG_DETECT_STREAM_PRIORITY_CHANGE = False

PLOT_TIME_UNIT_SIZE = 1000


# INPUT FILES
filepath = ".\\logfiles\\paper_demo_250mbit_throttle.qlog"
#filepath = ".\\logfiles\\paper_demo_250mbit_throttle.sqlog"
#filepath = ".\\logfiles\\paper_demo_250mbit_throttle-alt.qlog"



#filepath = ".\\logfiles\\paper_demo.qlog"
#filepath = ".\\logfiles\\paper_demo-alt.qlog"
#filepath = ".\\logfiles\\paper_demo2.qlog"

#filepath = ".\\logfiles\\facebook.qlog"
#filepath = ".\\logfiles\\facebook.sqlog"
#filepath = ".\\logfiles\\facebook_default_priority.qlog"
#filepath = ".\\logfiles\\facebook_default_priority.sqlog"


requests, replies, packets_received, packets_send, receive_streams, send_streams  = parse_log_file(filepath, PRIORITY_LOG_MODE)
endOfNormalizedCommTimeStamp = get_normalized_last_timestamp(filepath)

packets_received = filter_packets(packets_received)
packets_send = filter_packets(packets_send)


if SHOW_DEBUG_HTTP_REQUESTS:
    print("\nHTTP Requests:")
    requests.sort(key=attrgetter('time'))
    for req in requests:
        print(f"{req.stream_id} - type: {req.frame_type} - priority: {req.priority} - inc: {req.incremental} - resource: {req.path}")

if SHOW_DEBUG_HTTP_REPLIES:
    print("\nHTTP Replies:")
    replies.sort(key=attrgetter('time'))
    for rep in replies:
        print(f"{rep.stream_id} - type: {rep.frame_type} - priority: {rep.priority} - inc: {rep.incremental} - resource: {req.path}")

if SHOW_DEBUG_PACKETS_RECEIVED:
    print("\npacketsReceived:")
    packets_received.sort(key=attrgetter('time'))
    for rec in packets_received:
        print(f"Streams: {rec.streams}")

if SHOW_DEBUG_PACKETS_SEND:
    print("\npacketsSent:")
    for sen in packets_send:
        print(sen)

if SHOW_DEBUG_STREAMS_RECEIVED:
    print("\nReceiveStreams")
    for rs in receive_streams:
        print(rs)

if SHOW_DEBUG_STREAMS_SEND:
    print("\nSendStreams")
    for ss in send_streams:
        print(ss)

if DEBUG_DETECT_STREAM_PRIORITY_CHANGE:
    detect_priority_change(receive_streams, send_streams, MODE)


start_time = packets_received[0].time

# PLOTS -> matplotlib.pyplot
plot_stream_data_over_time(packets_received, start_time)
plot_stream_priority_over_time(receive_streams, start_time, endOfNormalizedCommTimeStamp)
plot_stream_aggregator(packets_received, start_time, endOfNormalizedCommTimeStamp)
plot_data_per_time_unit(packets_received, start_time, endOfNormalizedCommTimeStamp, PLOT_TIME_UNIT_SIZE)

# Extra plot made with plotly.graph_objects (web interface)
plot_data_per_time_unit_interactive(packets_received, start_time, endOfNormalizedCommTimeStamp, bin_size_ms=PLOT_TIME_UNIT_SIZE)

input("Press ENTER to close plots...")
