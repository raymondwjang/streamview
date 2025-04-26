import os
from dataclasses import dataclass
from pathlib import Path

import av
import numpy as np


@dataclass
class FrameStreamer:
    temp_dir: Path
    width: int
    height: int
    frame_rate: int
    playlist_path: Path | str | None = None
    container: av.container.OutputContainer | None = None

    def __post_init__(self):
        self.playlist_path = os.path.join(self.temp_dir, "stream.m3u8")
        # Create output container for HLS
        self.container = av.open(
            self.playlist_path,
            mode="w",
            format="hls",
            options={
                "hls_time": "2",  # Segment duration in seconds
                "hls_list_size": "5",  # Number of segments to keep
                "hls_flags": "delete_segments",  # Auto-delete old segments
            },
        )
        # Create a video stream
        self.stream = self.container.add_stream("h264", rate=self.frame_rate)
        self.stream.width = self.width
        self.stream.height = self.height
        self.stream.pix_fmt = "yuv420p"

    def process(self, frame):
        try:
            frame = frame.astype(np.uint8)
            # Create frame
            frame = av.VideoFrame.from_ndarray(frame, format="gray").reformat(
                format="yuv420p"
            )

            # Encode and write the packet
            packets = self.stream.encode(frame)
            for packet in packets:
                self.container.mux(packet)

        except Exception as e:
            print(f"VideoStreamError: {e}")
            self.container.close()

    def close(self):
        # Flush any remaining packets
        if self.stream:
            for packet in self.stream.encode(None):  # Flush encoder
                self.container.mux(packet)

        # Close the container
        if self.container:
            self.container.close()
