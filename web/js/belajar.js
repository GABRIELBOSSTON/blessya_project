'use strict';
const $ = s => document.querySelector(s);
const SAMPLE = [{pid:'P1',arrival:0,burst:5},{pid:'P2',arrival:1,burst:3},{pid:'P3',arrival:2,burst:1}];
const COLORS = ['var(--chart-1)','var(--chart-2)','var(--chart-3)','var(--chart-4)','var(--chart-5)','var(--chart-6)'];
const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt = value => Number(value).toLocaleString('en-US',{maximumFractionDigits:2});
let replay = null, replayIndex = 0, timer = null, cpuExport = null;
function error(id, message=''){const el=$(id); el.textContent=message; el.hidden=!message;}
function integer(value,label,min,max){
  if(!/^\d+$/.test(String(value).trim())) throw Error(`${label} must be an integer between ${min}–${max}.`);
  const n=Number(value); if(!Number.isSafeInteger(n)||n<min||n>max) throw Error(`${label} must be ${min}–${max}.`); return n;
}
async function request(path,payload){
  const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),20000);
  try {
    const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});
    const data=await response.json(); if(!response.ok||data.error) throw Error(data.error||'Request failed. Check your input.'); return data;
  } catch(e){if(e.name==='AbortError') throw Error('Request timed out. Try again with fewer items.'); if(e instanceof TypeError) throw Error('Server not connected. Open the application through mulai.bat.'); throw e;}
  finally{clearTimeout(timeout);}
}
function lockSetup(panel,locked){document.querySelectorAll(`${panel} .setup input, ${panel} .setup select, ${panel} .setup button`).forEach(el=>{el.disabled=locked;});}
function processRow(p){return `<tr><td><input aria-label="Process name" class="pid" maxlength="12" value="${esc(p.pid)}"></td><td><input aria-label="Arrival time ${esc(p.pid)}" class="arrival" type="number" min="0" max="100" step="1" value="${p.arrival}"></td><td><input aria-label="Burst time ${esc(p.pid)}" class="burst" type="number" min="1" max="50" step="1" value="${p.burst}"></td><td><button class="delete" type="button" aria-label="Delete process ${esc(p.pid)}">×</button></td></tr>`;}
function sample(){ $('#processes').innerHTML=SAMPLE.map(processRow).join(''); error('#cpu-error'); }
function readProcesses(){
  const seen=new Set();return [...$('#processes').rows].map((row,i)=>{
    const pid=row.querySelector('.pid').value.trim();
    if(!pid||pid.length>12) throw Error(`Process name on row ${i+1} is required (max 12 characters).`);
    if(pid.toUpperCase()==='IDLE') throw Error('The name IDLE is reserved for idle CPU. Use a different name.');
    if(seen.has(pid)) throw Error(`Name ${pid} is used twice. Each process must have a unique name.`); seen.add(pid);
    return {pid,arrival:integer(row.querySelector('.arrival').value,`Arrival time ${pid}`,0,100),burst:integer(row.querySelector('.burst').value,`Burst time ${pid}`,1,50)};
  });
}
function stats(items){return `<div class="stats">${items.map(([label,n])=>`<div class="stat"><strong>${fmt(n)}</strong><span>${label}</span></div>`).join('')}</div>`;}
function scheduleHTML(r){
  const color=pid=>pid==='IDLE'?'var(--color-muted)':COLORS[r.metrics.findIndex(m=>m.pid===pid)%COLORS.length];
  const total=r.summary.total_time, width=Math.max(500,total*20);
  const bars=r.timeline.map((s,i)=>`<div class="slice${s.pid==='IDLE'?' idle':''}" style="width:${s.duration/total*100}%;background:${color(s.pid)}" title="${esc(s.pid)}: ${s.start} to ${s.end}, duration ${s.duration}"><span>${esc(s.pid)}</span><span class="start">${s.start}</span>${i===r.timeline.length-1?`<span class="end">${s.end}</span>`:''}</div>`).join('');
  const fcfs=r.algorithm.startsWith('FCFS');
  const rows=r.metrics.map(m=>`<tr><td>${esc(m.pid)}</td><td>${m.completion}</td><td>${m.waiting}</td><td>${m.turnaround}</td><td>${m.response}</td></tr>`).join('');
  return `<article class="card cpu-result"><div class="result-heading"><h3>${fcfs?'FCFS':esc(r.algorithm)}</h3><span class="pill">${fcfs?'Non-preemptive':'Preemptive'}</span></div><p class="result-note">${fcfs?'Processes are executed to completion in arrival order.':'Each process runs for at most one quantum, then returns to the back of the queue if not finished.'}</p><h4>Gantt chart</h4><div class="gantt-scroll" tabindex="0" aria-label="Gantt chart, can be scrolled horizontally"><div class="gantt-track" style="width:${width}px" role="img" aria-label="${esc(r.timeline.map(s=>`${s.pid} from ${s.start} to ${s.end}`).join('; '))}">${bars}</div></div><p class="hint">The axis shows simulation time units. Scroll horizontally if the chart exceeds the screen width.</p>${stats([['Avg waiting time',r.summary.avg_waiting],['Avg turnaround',r.summary.avg_turnaround],['Avg response time',r.summary.avg_response]])}<div class="table-scroll"><table><thead><tr><th>Process</th><th>Completion</th><th>Waiting time</th><th>Turnaround</th><th>Response</th></tr></thead><tbody>${rows}</tbody></table></div><p class="hint">Turnaround = completion − arrival. Waiting time = turnaround − burst. Response = first execution − arrival.</p><details><summary>Computation details and scheduling log</summary><p>Context switches: <strong>${r.summary.context_switches}</strong>. Only direct switches between different processes are counted; switches to/from IDLE and consecutive turns of the same process are not counted. Context switch time cost is not modeled.</p><ol>${r.log.map(line=>`<li>${esc(line)}</li>`).join('')}</ol></details></article>`;
}
function comparisonHTML(a,b){
  const difference=b.summary.avg_response-a.summary.avg_response;
  let text=difference<0?'For this data, Round Robin produces a lower average response time than FCFS.':difference>0?'For this data, FCFS produces a lower average response time than Round Robin.':'For this data, the average response time of both algorithms is the same.';
  return `<div class="card comparison"><h3>Metric comparison</h3><div class="table-scroll"><table><thead><tr><th>Metric</th><th>FCFS</th><th>Round Robin</th></tr></thead><tbody>${[['Avg waiting time','avg_waiting'],['Avg turnaround','avg_turnaround'],['Avg response time','avg_response'],['Context switches','context_switches']].map(([name,key])=>`<tr><td>${name}</td><td>${fmt(a.summary[key])}</td><td>${fmt(b.summary[key])}</td></tr>`).join('')}</tbody></table></div><p>${text} This result only applies to the entered data; change the quantum to analyze its effect.</p></div>`;
}
function exportJSON(data,name){const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function runCPU(){
  error('#cpu-error');
  try {
    const processes=readProcesses(), algorithm=$('#algorithm').value;
    const quantum=algorithm==='fcfs'?2:integer($('#quantum').value,'Quantum',1,20);
    lockSetup('#panel-cpu',true);$('#cpu-output').innerHTML='<div class="card loading" role="status">Running scheduling simulation…</div>';
    const names=algorithm==='compare'?['fcfs','rr']:[algorithm];
    const responses=await Promise.all(names.map(name=>request('/api/scheduling',{algorithm:name,processes,quantum})));
    const results=responses.map(d=>d.results[0]); cpuExport={processes,quantum,results};
    $('#cpu-output').innerHTML=(results.length===2?comparisonHTML(...results):'')+results.map(scheduleHTML).join('')+'<button id="export-cpu" class="text-button full">Export results (JSON)</button>';
    $('#export-cpu').addEventListener('click',()=>exportJSON(cpuExport,'scheduling-results.json'));
  } catch(e){error('#cpu-error',e.message); if($('#cpu-output .loading')) $('#cpu-output').innerHTML='<div class="card empty"><h3>Results not available</h3><p>Fix the input, then run again.</p></div>';}
  finally{lockSetup('#panel-cpu',false);}
}
function stopReplay(){clearInterval(timer);timer=null;const play=$('#play');if(play)play.textContent='Replay';}
function renderReplay(){
  if(!replay)return;
  const event=replayIndex?replay.events[replayIndex-1]:null, items=event?event.items:[];
  const actor=event?event.actor.replace(/^(Producer|Consumer)-1$/,'$1'):'';
  $('#buffer-slots').innerHTML=Array.from({length:replay.capacity},(_,i)=>`<div class="slot ${i<items.length?'filled':''}">${i<items.length?esc(items[i]):'empty'}</div>`).join('');
  $('#buffer-count').textContent=`Filled ${items.length} of ${replay.capacity} slots`;
  $('#event-caption').innerHTML=event?`<strong>${esc(actor)} · ${esc(event.action)}</strong><br>${esc(event.detail)}<small>Step ${replayIndex}/${replay.events.length} · t = ${fmt(event.t)} ms</small>`:`<strong>Initial state: empty buffer.</strong><small>Use Next or Replay to step through each event.</small>`;
  $('#replay-range').value=replayIndex;$('#previous').disabled=replayIndex===0;$('#next').disabled=replayIndex===replay.events.length;
  if(replayIndex===replay.events.length)stopReplay();
}
async function runPC(){
  error('#pc-error');stopReplay();
  try {
    const config={capacity:integer($('#capacity').value,'Capacity',1,10),items:integer($('#items').value,'Number of items',1,12),producers:1,consumers:1,produce_ms:Number($('#produce-delay').value),consume_ms:Number($('#consume-delay').value)};
    lockSetup('#panel-pc',true);$('#pc-output').innerHTML='<div class="card loading" role="status">Producer and consumer threads are running…</div>';
    const data=await request('/api/ipc/producer-consumer',config);
    if(!data.completed||data.stuck_threads.length)throw Error('Simulation did not complete. Try again with fewer items.');
    replay=data;replayIndex=0;
    $('#pc-output').innerHTML=`<article class="card"><div class="result-heading"><h3>Buffer activity recording</h3><span class="pill">Completed</span></div><p class="result-note">Replay from real thread execution log. The speed is slowed down for easy observation and is shown after execution completes, not in real-time.</p><div class="flow"><span class="actor">Producer</span><span aria-hidden="true">→</span><span>Buffer</span><span aria-hidden="true">→</span><span class="actor">Consumer</span></div><div id="buffer-slots" class="slots" role="img" aria-label="Buffer contents at selected step"></div><p id="buffer-count" class="hint"></p><div id="event-caption" class="event-caption" aria-live="polite"></div><div class="playback"><button class="secondary" id="previous">Previous</button><button class="primary" id="play">Replay</button><button class="secondary" id="next">Next</button></div><input class="range" id="replay-range" type="range" min="0" max="${data.events.length}" value="0" aria-label="Select recording step"><p class="playback-note">Replay speed 0.6 seconds per step. The t value shows the actual execution time since the simulation started.</p><details><summary>Why do threads wait (BLOCKED)?</summary><p>The producer needs permission from the empty semaphore (empty slots) before storing an item, and the consumer needs permission from the full semaphore (available items) before retrieving one. If permission is not available, the thread waits until its counterpart releases permission. This condition is normal and is not a deadlock.</p><p>The buffer contents displayed are a snapshot when the event was recorded. Other threads may change the state between the attempt to acquire permission and the recording of the BLOCKED event.</p></details></article><article class="card"><h3>Results summary</h3>${stats([['Items produced',data.produced],['Items consumed',data.consumed],['Peak buffer usage',data.peak_buffer_usage]])}<p class="result-note">All items were successfully transferred. The buffer ends empty and never exceeded capacity.</p><div class="table-scroll"><table><tbody><tr><td>Producer was blocked (BLOCKED)</td><td>${data.blocked_producers} times</td></tr><tr><td>Consumer was blocked (BLOCKED)</td><td>${data.blocked_consumers} times</td></tr><tr><td>Unfinished threads</td><td>${data.stuck_threads.length}</td></tr></tbody></table></div><p class="hint">The number of BLOCKED events depends on OS thread scheduling, so it may differ between runs.</p><button id="export-pc" class="text-button">Export results (JSON)</button></article>`;
    renderReplay();
    $('#previous').addEventListener('click',()=>{stopReplay();replayIndex=Math.max(0,replayIndex-1);renderReplay();});
    $('#next').addEventListener('click',()=>{stopReplay();replayIndex=Math.min(replay.events.length,replayIndex+1);renderReplay();});
    $('#replay-range').addEventListener('input',e=>{stopReplay();replayIndex=Number(e.target.value);renderReplay();});
    $('#play').addEventListener('click',()=>{if(timer){stopReplay();return;}if(replayIndex===replay.events.length){replayIndex=0;renderReplay();}$('#play').textContent='Pause';timer=setInterval(()=>{replayIndex++;renderReplay();},600);});
    $('#export-pc').addEventListener('click',()=>exportJSON({config,...data},'producer-consumer-results.json'));
  } catch(e){error('#pc-error',e.message); if($('#pc-output .loading'))$('#pc-output').innerHTML='<div class="card empty"><h3>Simulation not completed</h3><p>Check the error message, then run again.</p></div>';}
  finally{lockSetup('#panel-pc',false);}
}
['cpu','pc'].forEach(name=>{$(`#tab-${name}`).addEventListener('click',()=>{stopReplay();['cpu','pc'].forEach(n=>{const active=n===name;$(`#panel-${n}`).hidden=!active;$(`#tab-${n}`).classList.toggle('active',active);$(`#tab-${n}`).setAttribute('aria-pressed',String(active));});});});
$('#algorithm').addEventListener('change',()=>{$('#quantum-field').hidden=$('#algorithm').value==='fcfs';$('#algorithm-help').textContent=$('#algorithm').value==='fcfs'?'Non-preemptive: processes are executed to completion in arrival order.':$('#algorithm').value==='rr'?'Preemptive: each process gets a time slice (quantum), then returns to the queue if not finished.':'Both algorithms are run with the same process data so the results can be compared fairly.';});
$('#sample').addEventListener('click',sample);
$('#add').addEventListener('click',()=>{error('#cpu-error');if($('#processes').rows.length>=12){error('#cpu-error','Maximum 12 processes.');return;}const names=[...document.querySelectorAll('.pid')].map(el=>el.value.trim());let n=1;while(names.includes(`P${n}`))n++;$('#processes').insertAdjacentHTML('beforeend',processRow({pid:`P${n}`,arrival:0,burst:2}));});
$('#processes').addEventListener('click',e=>{if(!e.target.matches('.delete'))return;if($('#processes').rows.length===1){error('#cpu-error','Keep at least one process.');return;}e.target.closest('tr').remove();error('#cpu-error');});
$('#run-cpu').addEventListener('click',runCPU);$('#run-pc').addEventListener('click',runPC);
$('#producer-fast').addEventListener('click',()=>{$('#produce-delay').value='10';$('#consume-delay').value='80';});
$('#consumer-fast').addEventListener('click',()=>{$('#produce-delay').value='80';$('#consume-delay').value='10';});
window.addEventListener('pagehide',stopReplay);sample();
