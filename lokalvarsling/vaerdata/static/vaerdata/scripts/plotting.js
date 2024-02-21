async function fetchDataAndPlot(url, plotElementId, plotFunctionName) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log(data); // For debugging purposes
        Plotly.newPlot(document.getElementById(plotElementId), data[plotFunctionName]);
    } catch (error) {
        console.error('Error fetching and plotting data:', error);
    }
}

async function updateSnowSenseData() {
    try {
        const response = await fetch(getSnowSenseUrl);
        const data = await response.json();
        console.log(data); // For debugging purposes
        // Update the table with the snowsense data
        ['location', 'time', 'temperature', 'wind', 'snowdepth', 
         'snowdepth_12h', 'snowdepth_24h', 'snowdepth_mtp', 'snowdepth_atp']
        .forEach((id, index) => document.getElementById(id).textContent = data.snowsense_data[index]);
    } catch (error) {
        console.error('Error fetching snowsense data:', error);
    }
}

window.onload = async function() {
    await updateSnowSenseData();
    await fetchDataAndPlot(getGraph1Url, 'graph1', 'graph1');
    await fetchDataAndPlot(getGraph2Url, 'graph2', 'graph2');
    await fetchDataAndPlot(getGraph3Url, 'graph3', 'graph3');
    await fetchDataAndPlot(getWindRoseUrl, 'windrose', 'get_windrose');
};