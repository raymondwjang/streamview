// Initialize video player
var player = videojs("stream-player", {
    fluid: true,
    liveui: true,
});
player.play();

// Initialize Vega plot
const spec = {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    description: "Live data stream",
    width: window.config.video.width,
    height: window.config.video.height,
    data: { name: "table" },
    mark: "line",
    encoding: {
        x: {
            field: "index",
            type: "quantitative",
        },
        y: { field: "value", type: "quantitative" },
    },
};

// Create WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws`);
let values = [];

vegaEmbed("#plot-container", spec).then((result) => {
    const view = result.view;

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const currentData = view.data("table");
        if (currentData.length >= 100) {
            // Get the oldest time we want to remove
            const oldestIdx = currentData[0].index;
            const changeSet = vega.changeset().insert(data).remove((t) => t.index === oldestIdx); // Remove the point with oldest time


            view.change("table", changeSet).run();
        } else {
            // Just insert if we're under maxPoints
            const changeSet = vega.changeset().insert(data);
            view.change("table", changeSet).run();
        }
    };
});