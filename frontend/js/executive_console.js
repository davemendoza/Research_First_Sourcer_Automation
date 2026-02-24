document.getElementById("loadBtn").onclick = async function() {

const res = await fetch("http://127.0.0.1:8000/api/ecosystem");
const data = await res.json();

renderGraph(data.nodes, data.links);
renderCandidates();
renderSimulation();
renderTrajectory();

};

function renderGraph(nodes, links) {

const canvas = document.getElementById("ecosystemCanvas");
const ctx = canvas.getContext("2d");

canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

ctx.clearRect(0,0,canvas.width,canvas.height);

nodes.forEach((node,i)=>{

const x = canvas.width/2 + Math.cos(i)*120;
const y = canvas.height/2 + Math.sin(i)*120;

ctx.beginPath();
ctx.arc(x,y,10,0,Math.PI*2);
ctx.fillStyle = "#3b82f6";
ctx.fill();

ctx.fillText(node.id,x+15,y);

});

}

function renderCandidates() {

document.getElementById("candidateList").innerHTML =
"<div>Paulius Micikevicius — Signal Strength 92</div>";

}

function renderSimulation() {

document.getElementById("simulationMetrics").innerHTML =
"<div>Projected Inference Gain: +18%</div>";

}

function renderTrajectory() {

const canvas = document.getElementById("trajectoryCanvas");
const ctx = canvas.getContext("2d");

canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

ctx.beginPath();
ctx.moveTo(0,200);
ctx.lineTo(200,100);
ctx.strokeStyle = "#10b981";
ctx.stroke();

}
