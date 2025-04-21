import embed from "vega-embed";
import { changeset } from "vega";

export class ChartManager {
  // Class to manage a Vega-Lite chart
  constructor(containerId) {
    // containerId: ID of an HTML element to put chart in
    this.containerId = containerId;
    this.maxPoints = 10;

    // Vega-Lite specification for the chart
    this.spec = {
      // Define we're using Vega-Lite schema
      $schema: "https://vega.github.io/schema/vega-lite/v6.json",
      // Define a named data source 'values'
      data: { name: "table" },
      // Create a line chart
      mark: "line",
      // Define how data maps to visual properties
      encoding: {
        // X-axis uses 'time' field from data
        x: { field: "time", type: "quantitative", scale: {zero: false} },
        // Y-axis uses 'value' field from data
        y: { field: "value", type: "quantitative" },
      }
    };
  }

  async initialize() {
    // Create the chart using Vega-Embed
    const result = await embed(`#${this.containerId}`, this.spec);
    // Store reference to the view for updates
    this.view = result.view;
  }

  updateData(data) {
    if (this.view) {
      const currentData = this.view.data("table");
      // Only set up removal if we're at or exceeding maxPoints
      if (currentData.length >= this.maxPoints) {
        // Get the oldest time we want to remove
        const oldestTime = currentData[0].time;

        const changeSet = changeset()
          .insert(data)
          .remove((t) => t.time === oldestTime); // Remove the point with oldest time
        this.view.change("table", changeSet).run();
      } else {
        // Just insert if we're under maxPoints
        const changeSet = changeset().insert(data);
        this.view.change("table", changeSet).run();
      }
    }
  }
}
