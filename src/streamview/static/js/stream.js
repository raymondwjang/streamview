class DataStream {
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

// When DOM is ready...
document.addEventListener("DOMContentLoaded", async () => {
  // 1. Create chart manager for 'vis' element
  const chart = new ChartManager("vis");
  // 2. Initialize the chart
  await chart.initialize();
  // 3. Create data stream connected to chart
  const stream = new DataStream(chart);
  // 4. Start WebSocket connection
  stream.connect();
});
