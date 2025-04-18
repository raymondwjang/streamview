import embed from 'vega-embed';

export class ChartManager {
  // Class to manage a Vega-Lite chart
  constructor(containerId) {
    // containerId: ID of HTML element to put chart in
    this.containerId = containerId;

    // Vega-Lite specification for the chart
    this.spec = {
      // Define we're using Vega-Lite schema
      $schema: "https://vega.github.io/schema/vega-lite/v6.json",
      // Define a named data source 'values'
      data: { name: "values" },
      // Create a line chart
      mark: "line",
      // Define how data maps to visual properties
      encoding: {
        // X-axis uses 'time' field from data
        x: { field: "time", type: "quantitative" },
        // Y-axis uses 'value' field from data
        y: { field: "value", type: "quantitative" },
      },
    };
  }

  async initialize() {
    // Create the chart using Vega-Embed
    const result = await embed(`#${this.containerId}`, this.spec);
    // Store reference to the view for updates
    this.view = result.view;
  }

  updateData(data) {
    // Update chart with new data if view exists
    if (this.view) {
      // Update 'values' data source and redraw
      this.view.data("values", [data]).run();
    }
  }
}
