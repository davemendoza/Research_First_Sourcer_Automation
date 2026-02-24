(function () {

console.log("Network Graph Loaded");

const API_BASE = "http://127.0.0.1:8000";

async function init() {

    const container =
        document.getElementById("ecosystem-graph");

    if (!container) return;

    const response =
        await fetch(API_BASE + "/intel/graph");

    const data =
        await response.json();

    console.log(data);

}

document.addEventListener("DOMContentLoaded", init);

})();
