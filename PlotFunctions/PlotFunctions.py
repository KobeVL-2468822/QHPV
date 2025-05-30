from ObjectManager.StreamManager import *
from DataFunctions.Filters import *
from DataFunctions.AdditionalFunctions import *
from operator import attrgetter
from typing import List
from collections import defaultdict
import math

import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Plot a graph of all cumulated data received over the different streams. X-> Time, Y-> Data received (cumulative)
def plot_stream_data_over_time(packets_received: List[Packet], start_time: float):

    stream_data = {}
    packets_received.sort(key=attrgetter('time'))

    for packet in packets_received:
        time = packet.time - start_time  # Normalized time
    
        for stream in packet.streams:
            if stream.ID not in stream_data:
                stream_data[stream.ID] = {'times': [], 'data': []}
        
            # Cumulative data for current stream
            if len(stream_data[stream.ID]['data']) == 0:
                stream_data[stream.ID]['times'].append(time)
                stream_data[stream.ID]['data'].append(0)

            cumulative_data = stream_data[stream.ID]['data'][-1] + stream.length 
            stream_data[stream.ID]['times'].append(time)
            stream_data[stream.ID]['data'].append(cumulative_data)

    # Creata a plot
    plt.figure(figsize=(10, 6))

    # Plot every stream and add the stream-ID at the end of the line
    for stream_id, data in stream_data.items():
        line, = plt.plot(data['times'], data['data'], label=f"Stream {stream_id}")
        line_color = line.get_color()
        plt.text(data['times'][-1], data['data'][-1], f" {stream_id}", color=line_color, verticalalignment='center', horizontalalignment='left', fontsize=9)

    # Add labels and title
    plt.xlabel('Time (milliseconds)', fontsize=12)
    plt.ylabel('Cumulative Data Received (bytes)', fontsize=12)
    plt.title('Cumulative Data Received / Stream Over Time', fontsize=14)

    # Hide legend - clutters screen too much
    plt.legend().set_visible(False)
    plt.tight_layout()

    plt.grid(True)
    plt.show(block=False)


# Plot a graph of the priority history of all streams throughout the connection. X -> Time, Y-> Priority
def plot_stream_priority_over_time(receive_streams: List[Stream], start_time: float, normalized_end_time: float):
    # Group streams per initial priority
    priority_buckets = {prio: [] for prio in range(8)}

    for stream in receive_streams:
        if stream.priority_history:
            initial_priority = stream.priority_history[0]
            priority_buckets[initial_priority].append(stream)

    # Create a plot
    plt.figure(figsize=(14, 8))

    # Offset tracking per priority level
    offset_trackers = {prio: {} for prio in range(8)}

    for prio, bucket in priority_buckets.items():
        if not bucket:
            continue

        for stream in bucket:
            if not stream.priority_history or not stream.priority_history_timestamps:
                continue

            normalized_times = [t - start_time for t in stream.priority_history_timestamps]
            priorities = stream.priority_history

            times = []
            prios = []


            
            # Use an offset to prevent streams of the same urgency value to overlap each other, making the graph unreadable
            buffer = 0.2

            for i in range(len(priorities)):
                prio_at_i = priorities[i]
                base = prio_at_i + (buffer * prio_at_i)

                # Calc or get offset for the stream
                tracker = offset_trackers[prio_at_i]
                if stream.ID not in tracker:
                    # Give each stream in an urgency bucket a different offset value
                    tracker[stream.ID] = (len(tracker) + 1) / (len(bucket) + 1)
                offset = tracker[stream.ID]

                start_time_segment = normalized_times[i]
                end_time_segment = (
                    normalized_times[i + 1] if i < len(priorities) - 1 else normalized_end_time
                )

                times += [start_time_segment, end_time_segment]
                prios += [base + offset, base + offset]

            line, = plt.plot(times, prios, drawstyle='steps-post', label=f"Stream {stream.ID}")

            plt.text(times[-1], prios[-1], f" {stream.ID}", color=line.get_color(), verticalalignment='center', horizontalalignment='left', fontsize=7)


    plt.gca().invert_yaxis()
    plt.yticks([i + (buffer * i) for i in range(9)], [str(i) for i in range(9)]) 

    plt.xlim(0, normalized_end_time)

    # Add labels and title
    plt.xlabel('Time (milliseconds)', fontsize=12)
    plt.ylabel('Urgency (0 = Highest)', fontsize=12)
    plt.title('Priority/Urgency History Of Streams', fontsize=14)

    plt.grid(True)
    plt.legend().set_visible(False)
    plt.tight_layout()
    plt.show(block=False)


def plot_stream_aggregator(packets_received: List[Packet], start_time: float, normalized_end_time: float):
    # Create segments
    segments = []
    for idx, packet in enumerate(packets_received):
        normalized_time = packet.time - start_time

        next_packet_time = normalized_end_time
        if idx + 1 < len(packets_received):
            next_packet_time = packets_received[idx + 1].time - start_time

        streams_in_packet = defaultdict(int)
        for stream in packet.streams:
            streams_in_packet[stream.ID] += stream.length

        segments.append({
            "start": normalized_time,
            "end": next_packet_time,
            "streams": dict(streams_in_packet)
        })

    fig, ax = plt.subplots(figsize=(15, 7))
    cmap = plt.colormaps.get_cmap('tab20')
    available_colors = [cmap(i) for i in range(cmap.N)]
    stream_colors = {}
    stream_color_idx = 0


    # Group segments together based on streams
    grouped_segments = []
    if segments:
        current_group = {
            "start": segments[0]["start"],
            "end": segments[0]["end"],
            "streams": segments[0]["streams"].copy()
        }

        for seg in segments[1:]:
            if set(seg["streams"].keys()) == set(current_group["streams"].keys()):
                # Same stream(s) -> don't close group yet
                current_group["end"] = seg["end"]
                for sid, bytes_amount in seg["streams"].items():
                    current_group["streams"][sid] += bytes_amount
            else:
                # Close group and start a new group
                grouped_segments.append(current_group)
                current_group = {
                    "start": seg["start"],
                    "end": seg["end"],
                    "streams": seg["streams"].copy()
                }

        grouped_segments.append(current_group)  # Add last group to list of groups

    # Draw the grouped segments
    for group in grouped_segments:
        start = group["start"]
        end = group["end"]
        duration = end - start

        if duration <= 0:
            continue

        streams = group["streams"]

        bottom = 0
        for stream_id, total_bytes in streams.items():
            data_rate = total_bytes / duration  # bytes/ms

            if stream_id not in stream_colors:
                stream_colors[stream_id] = available_colors[stream_color_idx % len(available_colors)]
                stream_color_idx += 1

            color = stream_colors[stream_id]

            # Plot bar
            ax.broken_barh(
                [(start, duration)],
                (bottom, data_rate),
                facecolors=color,
                edgecolors=color,
            )

            # Only write the stream id one time above a group so the screen doesnt get cluttered with stream ids
            if data_rate > 0:
                ax.text(
                    start + duration / 2,
                    bottom + data_rate / 2,
                    str(stream_id),
                    ha='center',
                    va='center',
                    fontsize=6,
                    color='black'
                )

            bottom += data_rate

    # Add labels and title
    ax.set_xlim(0, normalized_end_time)
    ax.set_xlabel("Time (milliseconds)", fontsize=12)
    ax.set_ylabel("Data Rate (Bytes/ms)", fontsize=12)
    ax.set_title("Stream Aggregator", fontsize=14)

    ax.grid(True, axis='both')
    #ax.set_yticks([])

    plt.tight_layout()
    plt.show(block=False)




def plot_data_per_time_unit(packets_received: List[Packet], start_time: float, normalized_end_time: float, bin_size_ms: float = 100.0):
    # Create bins (time units)
    num_bins = int(math.ceil(normalized_end_time / bin_size_ms))
    bins = [defaultdict(int) for _ in range(num_bins)]

    for packet in packets_received:
        bin_index = int((packet.time - start_time) // bin_size_ms)
        for stream in packet.streams:
            bins[bin_index][stream.ID] += stream.length

    fig, ax = plt.subplots(figsize=(15, 7))
    cmap = plt.colormaps.get_cmap('tab20')
    available_colors = [cmap(i) for i in range(cmap.N)]
    stream_colors = {}
    stream_color_idx = 0

    for i, bin_data in enumerate(bins):
        if not bin_data:
            continue

        # Sort streams on byte quantity, bigger streams at the bottom
        sorted_streams = sorted(bin_data.items(), key=lambda x: -x[1])
        bottom = 0
        bin_start = i * bin_size_ms
        bin_width = bin_size_ms

        total_bin_bytes = sum(size for _, size in sorted_streams)

        for stream_id, size in sorted_streams:
            if stream_id not in stream_colors:
                stream_colors[stream_id] = available_colors[stream_color_idx % len(available_colors)]
                stream_color_idx += 1
            color = stream_colors[stream_id]

            height = size  

            ax.broken_barh(
                [(bin_start, bin_width)],
                (bottom, height),
                facecolors=color,
                edgecolors='black'
            )

            ax.text(
                bin_start + bin_width / 2,
                bottom + height / 2,
                f"{stream_id} ({size})",
                ha='center',
                va='center',
                fontsize=6,
                color='black'
            )

            bottom += height

        ax.text(
            bin_start + bin_width / 2,
            bottom + 5,
            f"Total: {total_bin_bytes}",
            ha='center',
            va='bottom',
            fontsize=7,
            fontweight='bold'
        )

    ax.set_xticks([i * bin_size_ms for i in range(num_bins)])

    ax.set_xlim(0, normalized_end_time)
    ax.set_xlabel(f"Time (ms), bin size = {bin_size_ms} ms", fontsize=12)
    ax.set_ylabel("Bytes Received", fontsize=12)
    ax.set_title("Aggregated Data per Time Unit", fontsize=14)
    ax.grid(True, axis='both')
    plt.tight_layout()
    plt.show(block=False)




def plot_data_per_time_unit_interactive(
    packets_received: list,
    start_time: float,
    normalized_end_time: float,
    bin_size_ms: float = 100.0
):
    # Bin setup
    num_bins = int(math.ceil(normalized_end_time / bin_size_ms))
    bins = [defaultdict(int) for _ in range(num_bins)]

    # Fill bins
    for packet in packets_received:
        bin_index = int((packet.time - start_time) // bin_size_ms)
        for stream in packet.streams:
            bins[bin_index][stream.ID] += stream.length

    # Gather all stream IDs
    all_streams = set()
    for bin_data in bins:
        all_streams.update(bin_data.keys())

    all_streams = sorted(all_streams)
    stream_traces = {sid: {'x': [], 'y': []} for sid in all_streams}
    totals_x = []
    totals_y = []

    for i, bin_data in enumerate(bins):
        bin_start = i * bin_size_ms
        totals_x.append(bin_start)
        total_bytes = sum(bin_data.values())
        totals_y.append(total_bytes)

        for sid in all_streams:
            stream_traces[sid]['x'].append(bin_start)
            stream_traces[sid]['y'].append(bin_data.get(sid, 0))

    # Build Plotly figure
    fig = go.Figure()

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
              '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

    for i, sid in enumerate(all_streams):
        fig.add_trace(go.Bar(
            name=f"Stream {sid}",
            x=stream_traces[sid]['x'],
            y=stream_traces[sid]['y'],
            marker_color=colors[i % len(colors)],
            hovertemplate=f"Stream {sid}<br>Time: %{{x}} ms<br>Bytes: %{{y}}<extra></extra>",
        ))

    # Add total values as line on top of bars
    fig.add_trace(go.Scatter(
        x=totals_x,
        y=totals_y,
        mode='text',
        text=[f"{v}" for v in totals_y],
        textposition="top center",
        textfont=dict(size=10, color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Layout
    fig.update_layout(
        barmode='stack',
        title='Interactive Aggregated Data per Time Unit',
        xaxis=dict(title=f'Time (ms), bin size = {bin_size_ms} ms'),
        yaxis=dict(title='Bytes Received'),
        hovermode='x unified',
        height=600
    )

    fig.show()