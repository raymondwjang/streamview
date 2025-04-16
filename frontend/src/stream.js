export class DataStream {
  // Class to manage WebSocket connection
  constructor(chartManager) {
    // Takes a ChartManager instance to update
    this.chartManager = chartManager;
    // WebSocket connection reference
    this.ws = null;
  }

  connect() {
    // Create WebSocket connection
    this.ws = new WebSocket("ws://localhost:8000/ws");
    // Set up message handler
    this.ws.onmessage = (event) => {
      // Parse incoming JSON data
      const data = JSON.parse(event.data);
      // Send to chart for visualization
      this.chartManager.updateData(data);
    };
  }
}
