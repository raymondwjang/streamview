import { ChartManager } from "./chart.js";
import { DataStream } from "./stream.js";

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
