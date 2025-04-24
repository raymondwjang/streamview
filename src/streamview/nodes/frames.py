import os
import time
from dataclasses import dataclass
from pathlib import Path

import av
import numpy as np


@dataclass
class FrameStreamer:
    temp_dir: Path
    width: int = 480
    height: int = 320
    frame_rate: int = 30
    playlist_path: Path | str | None = None
    container: av.container.OutputContainer | None = None

    def __post_init__(self):
        self.playlist_path = os.path.join(self.temp_dir, 'stream.m3u8')
        # Create output container for HLS
        self.container = av.open(self.playlist_path, mode='w', format='hls', options={
            'hls_time': '2',  # Segment duration in seconds
            'hls_list_size': '5',  # Number of segments to keep
            'hls_flags': 'delete_segments',  # Auto-delete old segments
        })
        # Create a video stream
        self.stream = self.container.add_stream('h264', rate=self.frame_rate)
        self.stream.width = self.width
        self.stream.height = self.height
        self.stream.pix_fmt = 'yuv420p'

    def frame(self):
        t = time.time()
        frame = np.ones((self.width, self.height), dtype=np.uint8) * int(255 * (np.sin(t) + 1) / 2)
        return frame

    def gen_frame(self):
        while True:
            yield self.frame()
            time.sleep(1 / self.frame_rate)

    def stream(self):
        try:
            for frame_idx, array in enumerate(self.gen_frame()):
                # Create frame
                frame = av.VideoFrame.from_ndarray(array, format='rgb24')

                # Encode and write the packet
                packets = self.stream.encode(frame)
                for packet in packets:
                    self.container.mux(packet)

            # Flush stream
            for packet in self.stream.encode():
                self.container.mux(packet)

            # Close the file
            self.container.close()

        except Exception as e:
            print(f"Streaming error: {e}")
            self.container.close()
