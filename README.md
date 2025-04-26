# Streamview

A proof-of-concept application for concurrently streaming video frames and metrics data using a runner & nodes architecture. This app showcases how to efficiently stream numpy-based frames and live-updating graphs through a web interface.
This is the only success I've had at shoveling this amount of data through (30 fps) after exploring every major Python dashboard package out there.

## Architecture

### Runner & Nodes System

The architecture closely resembles how `cala` is structured, to ensure streamlined porting.

This means the `Runner` takes care of where things go and connecting backend to frontend.
All backend `Node`s need to do is to stream data out.

#### Runner (`runner.py`)

- Central coordinator for the streaming system
- Manages the lifecycle of streaming nodes and web connections
- Three main responsibilities:
  1. **Resource Management**: Creates and manages temporary directories for HLS streaming and websocket connections for metric streaming
  2. **Frame Assignment**: Assigns frames to the video node
  3. **Node Orchestration**: Orchestrates the video and metric nodes to run concurrently

#### Nodes

Modular components that handle actual data streaming:

1. **Video Node** (`nodes/frames.py`)
   - Takes a temporary directory from runner
   - Converts numpy arrays into HLS video stream
   - Segments video into chunks
   - Manages video encoding using `PyAV` (FFMPEG)
   - Generates HLS playlist
   - Saves playlist and video chunks to the temporary directory
   - Automatic cleanup of old segments

2. **Metric Node** (`nodes/numerics.py`)
   - Takes a websocket from runner
   - Sends JSON-formatted metrics in real-time

### Backend

- **FastAPI** server handling HTTP and WebSocket connections
- **PyAV (FFMPEG)** for video encoding and HLS (HTTP Live Streaming) generation

### Frontend

- **video.js** for HLS video playback
- **Vega/Vega-Lite/Vega-Embed** for real-time data visualization
- Responsive dashboard layout showing both video and metrics simultaneously

## Installation

1. Ensure you have Python 3.13+ installed
2. Install PDM (Python Dependency Manager) if you haven't already
3. Install the project with development dependencies:

```shell
pdm install --dev
```

## Running the Application

Start the server with:

```shell
python -m streamview
```

The dashboard will be available at `http://127.0.0.1:8000`

## Project Structure

- `runner.py`: Core application runner that coordinates nodes and handles web requests
- `nodes/`:
  - `frames.py`: Video streaming node implementation
  - `numerics.py`: Metric streaming node implementation
- `frontend/`: Contains the dashboard template and client-side logic
