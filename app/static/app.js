const stateElement = document.querySelector('[data-state]');
const distanceElement = document.querySelector('[data-distance]');
const updatedElement = document.querySelector('[data-updated]');
const sourceElement = document.querySelector('[data-source]');
const unackedElement = document.querySelector('[data-unacked]');
const closedElement = document.querySelector('[data-closed]');
const openElement = document.querySelector('[data-open]');
const door = document.querySelector('[data-door]');
const eventsBody = document.querySelector('[data-events]');
const chart = document.querySelector('[data-chart]');
const context = chart.getContext('2d');
const history = [];
let openThreshold = 35;

function renderReading(reading, summary) {
  stateElement.textContent = reading.state;
  distanceElement.textContent = Number(reading.distance_cm).toFixed(1);
  updatedElement.textContent = new Date(reading.recorded_at).toLocaleTimeString();
  sourceElement.textContent = reading.source;
  door.className = `door ${reading.state}`;
  if (summary) {
    unackedElement.textContent = summary.unacknowledged_count;
    closedElement.textContent = summary.thresholds.closed_cm;
    openElement.textContent = summary.thresholds.open_cm;
    openThreshold = summary.thresholds.open_cm;
  }
  history.push(Number(reading.distance_cm));
  if (history.length > 60) history.shift();
  drawChart();
}

function drawChart() {
  const width = chart.width, height = chart.height;
  context.clearRect(0, 0, width, height);
  context.strokeStyle = '#25303d'; context.lineWidth = 1;
  for (let row = 1; row < 5; row++) { const y = row * height / 5; context.beginPath(); context.moveTo(0,y); context.lineTo(width,y); context.stroke(); }
  const max = 60;
  const thresholdY = height - (openThreshold / max) * height;
  context.strokeStyle = '#f6c65b'; context.setLineDash([8,8]); context.beginPath(); context.moveTo(0,thresholdY); context.lineTo(width,thresholdY); context.stroke(); context.setLineDash([]);
  if (history.length < 2) return;
  context.strokeStyle = '#54d7ff'; context.lineWidth = 4; context.lineJoin = 'round'; context.beginPath();
  history.forEach((value,index) => { const x = index * width / 59; const y = height - Math.max(0,Math.min(max,value)) / max * height; index ? context.lineTo(x,y) : context.moveTo(x,y); });
  context.stroke();
}

async function loadEvents() {
  const response = await fetch('/api/events');
  const events = await response.json();
  eventsBody.innerHTML = events.length ? events.slice(0,10).map(event => `<tr><td>${new Date(event.recorded_at).toLocaleString()}</td><td>${event.previous_state} → ${event.state}</td><td>${Number(event.distance_cm).toFixed(1)} cm</td><td><span class="pill">${event.acknowledged ? 'acknowledged' : 'new'}</span></td></tr>`).join('') : '<tr><td colspan="4">No state transition recorded yet.</td></tr>';
}
document.querySelector('[data-refresh]').addEventListener('click', loadEvents);

async function loadStatus() {
  const response = await fetch('/api/status');
  const summary = await response.json();
  renderReading(summary.reading, summary);
}
loadStatus(); loadEvents();

function connect() {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${location.host}/ws`);
  socket.addEventListener('message', (event) => { const data = JSON.parse(event.data); if (data.type === 'reading') { renderReading(data, data.summary); if (data.changed) loadEvents(); } else if (data.reading) renderReading(data.reading, data); });
  socket.addEventListener('close', () => setTimeout(connect, 1500));
  socket.addEventListener('open', () => socket.send('ready'));
}
connect();

document.querySelector('[data-simulate]').addEventListener('submit', async (event) => {
  event.preventDefault();
  const error = document.querySelector('[data-error]'); error.textContent = '';
  const distance = Number(document.querySelector('#manual-distance').value);
  const response = await fetch('/api/simulate', {method:'POST',headers:{'Content-Type':'application/json','X-API-Key':'doorsense-local-demo'},body:JSON.stringify({distance_cm:distance})});
  const data = await response.json();
  if (!response.ok) error.textContent = data.detail || 'Manual simulation failed.';
});
