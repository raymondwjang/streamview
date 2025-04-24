from flask import Flask, send_from_directory, render_template_string
import av
import numpy as np
import tempfile
import os
import threading
import time

app = Flask(__name__)

# Global variable to store our stream path info
stream_info = {
    'temp_dir': None,
    'playlist_path': None
}

# HTML template as a string - we'll use render_template_string instead of render_template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Numpy Stream Viewer</title>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
</head>
<body>
    <h1>Numpy Stream Viewer</h1>
    <video-js id="stream-player" class="vjs-default-skin" controls width="400" height="400">
        <source src="/stream/stream.m3u8" type="application/x-mpegURL">
    </video-js>

    <script>
        var player = videojs('stream-player', {
            fluid: true,
            liveui: true
        });
        player.play();
    </script>
</body>
</html>
"""

def generate_dummy_frames():
    """Generate some dummy numpy arrays for testing"""
    while True:
        # Create a 400x400 array that changes over time
        t = time.time()
        frame = np.zeros((400, 400, 3), dtype=np.uint8)
        frame[:, :, 0] = int(255 * (np.sin(t) + 1) / 2)  # Red channel
        frame[:, :, 1] = int(255 * (np.cos(t) + 1) / 2)  # Green channel
        yield frame
        time.sleep(1/30)  # Simulate 30 FPS

def stream_numpy_arrays(temp_dir):
    playlist_path = os.path.join(temp_dir, 'stream.m3u8')
    
    # Create output container for HLS
    output = av.open(playlist_path, mode='w', format='hls', options = {
        'hls_time': '2',        # Segment duration in seconds
        'hls_list_size': '5',   # Number of segments to keep
        'hls_flags': 'delete_segments',  # Auto-delete old segments
    })
    
    # Create video stream
    stream = output.add_stream('h264', rate=30)
    stream.width = 400
    stream.height = 400
    stream.pix_fmt = 'yuv420p'
    
    
    try:
        for frame_idx, array in enumerate(generate_dummy_frames()):
            # Create frame
            frame = av.VideoFrame.from_ndarray(array, format='rgb24')
            
            # Encode and write the packet
            packets = stream.encode(frame)
            for packet in packets:
                output.mux(packet)
                
    except Exception as e:
        print(f"Streaming error: {e}")
        output.close()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream/<path:filename>')
def serve_stream(filename):
    """Serve the HLS stream files"""
    if stream_info['temp_dir']:
        return send_from_directory(stream_info['temp_dir'], filename)
    return "Stream not ready", 404

def start_streaming():
    """Initialize and start the streaming process"""
    # Create temporary directory
    stream_info['temp_dir'] = tempfile.mkdtemp()
    print(f"Streaming to directory: {stream_info['temp_dir']}")
    
    # Start streaming in a separate thread
    stream_thread = threading.Thread(
        target=stream_numpy_arrays, 
        args=(stream_info['temp_dir'],)
    )
    stream_thread.daemon = True
    stream_thread.start()

if __name__ == '__main__':
    # Start the streaming process
    start_streaming()
    
    # Run Flask app
    app.run(debug=True, threaded=True)