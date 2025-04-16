from fastapi import FastAPI, WebSocket
# StaticFiles - for serving JavaScript and other static files
from fastapi.staticfiles import StaticFiles
# Jinja2Templates - for serving HTML templates
from fastapi.templating import Jinja2Templates
# Request - needed for template context
from fastapi.requests import Request

app = FastAPI()

# Mount the static directory to serve static files (like our JavaScript)
# First arg "/static" - URL path where files will be served
# StaticFiles(directory="static") - points to the actual 'static' folder in your project
# name="static" - name used for URL generation
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a templates object pointing to your templates directory
# This will be used to render HTML templates
templates = Jinja2Templates(directory="templates")

# Define a route for the main page
@app.get("/")  # Handle HTTP GET requests to the root URL "/"
async def get(request: Request):
    """Serve the dashboard page"""
    # Render and return the index.html template
    # request is required by Jinja2 for template context
    return templates.TemplateResponse("index.html", {"request": request})

# Define a WebSocket endpoint
@app.websocket("/ws")  # Handle WebSocket connections at "/ws"
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection and stream data"""
    # Import required libraries for data generation
    import asyncio
    import random
    import time

    # Accept the WebSocket connection
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "time": time.time(),
                "value": random.random()
            })
            await asyncio.sleep(1)
    except:
        # Handle any disconnection or errors silently
        # In a production environment, you'd want proper error handling here
        pass