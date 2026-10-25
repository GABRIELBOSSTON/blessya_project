'use strict';
const $ = s => document.querySelector(s);
const SAMPLE = [{pid:'P1',arrival:0,burst:5},{pid:'P2',arrival:1,burst:3},{pid:'P3',arrival:2,burst:1}];
const COLORS = ['var(--chart-1)','var(--chart-2)','var(--chart-3)','var(--chart-4)','var(--chart-5)','var(--chart-6)'];
const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const fmt = value => Number(value).toLocaleString('id-ID',{maximumFractionDigits:2});
let replay = null, replayIndex = 0, timer = null, cpuExport = null;
function error(id, message=''){const el=$(id); el.textContent=message; el.hidden=!message;}
function integer(value,label,min,max){
  if(!/^\d+$/.test(String(value).trim())) throw Error(`${label} harus bilangan bulat ${min}–${max}.`);
  const n=Number(value); if(!Number.isSafeInteger(n)||n<min||n>max) throw Error(`${label} harus ${min}–${max}.`); return n;
}
async function request(path,payload){
  const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),20000);
  try {
    const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});
    const data=await response.json(); if(!response.ok||data.error) throw Error(data.error||'Percobaan gagal. Periksa masukan.'); return data;
  } catch(e){if(e.name==='AbortError') throw Error('Percobaan terlalu lama. Coba lagi dengan jumlah barang lebih kecil.'); if(e instanceof TypeError) throw Error('Server tidak terhubung. Buka aplikasi melalui mulai.bat.'); throw e;}
  finally{clearTimeout(timeout);}
}
function lockSetup(panel,locked){document.querySelectorAll(`${panel} .setup input, ${panel} .setup select, ${panel} .setup button`).forEach(el=>{el.disabled=locked;});}
function processRow(p){return `<tr><td><input aria-label="Nama proses" class="pid" maxlength="12" value="${esc(p.pid)}"></td><td><input aria-label="Waktu datang ${esc(p.pid)}" class="arrival" type="number" min="0" max="100" step="1" value="${p.arrival}"></td><td><input aria-label="Lama proses ${esc(p.pid)}" class="burst" type="number" min="1" max="50" step="1" value="${p.burst}"></td><td><button class="delete" type="button" aria-label="Hapus proses ${esc(p.pid)}">×</button></td></tr>`;}
function sample(){ $('#processes').innerHTML=SAMPLE.map(processRow).join(''); error('#cpu-error'); }
function readProcesses(){
  const seen=new Set();return [...$('#processes').rows].map((row,i)=>{
    const pid=row.querySelector('.pid').value.trim();
    if(!pid||pid.length>12) throw Error(`Nama proses pada baris ${i+1} harus diisi (maksimal 12 karakter).`);
    if(pid.toUpperCase()==='IDLE') throw Error('Nama IDLE digunakan untuk CPU kosong. Gunakan nama lain.');
    if(seen.has(pid)) throw Error(`Nama ${pid} dipakai dua kali. Setiap proses harus berbeda.`); seen.add(pid);
    return {pid,arrival:integer(row.querySelector('.arrival').value,`Waktu datang ${pid}`,0,100),burst:integer(row.querySelector('.burst').value,`Lama proses ${pid}`,1,50)};
  });
}
function stats(items){return `<div class="stats">${items.map(([label,n])=>`<div class="stat"><strong>${fmt(n)}</strong><span>${label}</span></div>`).join('')}</div>`;}
function scheduleHTML(r){
  const color=pid=>pid==='IDLE'?'var(--color-muted)':COLORS[r.metrics.findIndex(m=>m.pid===pid)%COLORS.length];
  const total=r.summary.total_time, width=Math.max(500,total*20);
  const bars=r.timeline.map((s,i)=>`<div class="slice${s.pid==='IDLE'?' idle':''}" style="width:${s.duration/total*100}%;background:${color(s.pid)}" title="${esc(s.pid)}: ${s.start} sampai ${s.end}, durasi ${s.duration}"><span>${esc(s.pid)}</span><span class="start">${s.start}</span>${i===r.timeline.length-1?`<span class="end">${s.end}</span>`:''}</div>`).join('');
  const fcfs=r.algorithm.startsWith('FCFS');
  const rows=r.metrics.map(m=>`<tr><td>${esc(m.pid)}</td><td>${m.completion}</td><td>${m.waiting}</td><td>${m.turnaround}</td><td>${m.response}</td></tr>`).join('');
  return `<article class="card cpu-result"><div class="result-heading"><h3>${fcfs?'FCFS':esc(r.algorithm)}</h3><span class="pill">${fcfs?'Sampai selesai':'Bergantian'}</span></div><p class="result-note">${fcfs?'Proses yang datang lebih awal dilayani sampai selesai.':'Setiap proses mendapat waktu sesuai quantum, lalu mengantre lagi jika belum selesai.'}</p><h4>Urutan penggunaan CPU</h4><div class="gantt-scroll" tabindex="0" aria-label="Gantt chart, dapat digeser mendatar"><div class="gantt-track" style="width:${width}px" role="img" aria-label="${esc(r.timeline.map(s=>`${s.pid} dari ${s.start} sampai ${s.end}`).join('; '))}">${bars}</div></div><p class="hint">Angka di bawah batang menunjukkan waktu simulasi. Geser mendatar jika urutannya panjang.</p>${stats([['Rata-rata menunggu',r.summary.avg_waiting],['Rata-rata turnaround',r.summary.avg_turnaround],['Rata-rata respons',r.summary.avg_response]])}<div class="table-scroll"><table><thead><tr><th>Proses</th><th>Selesai</th><th>Menunggu</th><th>Turnaround</th><th>Respons</th></tr></thead><tbody>${rows}</tbody></table></div><p class="hint">Menunggu: lama berada di antrean. Turnaround: dari datang sampai selesai. Respons: dari datang sampai pertama mendapat CPU.</p><details><summary>Lihat perhitungan dan langkah</summary><p>Turnaround = selesai − datang. Menunggu = turnaround − lama proses. Respons = mulai pertama − datang.</p><p>Pergantian antarproses: <strong>${r.summary.context_switches}</strong>. Peralihan ke/dari CPU kosong dan giliran berulang proses yang sama tidak dihitung. Biaya waktu perpindahan tidak dimodelkan.</p><ol>${r.log.map(line=>`<li>${esc(line)}</li>`).join('')}</ol></details></article>`;
}
function comparisonHTML(a,b){
  const difference=b.summary.avg_response-a.summary.avg_response;
  let text=difference<0?'Pada contoh ini, Round Robin membuat proses rata-rata lebih cepat mendapat giliran pertama.':difference>0?'Pada contoh ini, FCFS memberi rata-rata respons yang lebih kecil.':'Pada contoh ini, rata-rata respons kedua algoritma sama.';
  return `<div class="card comparison"><h3>Apa yang berubah?</h3><div class="table-scroll"><table><thead><tr><th>Ukuran</th><th>FCFS</th><th>Round Robin</th></tr></thead><tbody>${[['Menunggu','avg_waiting'],['Turnaround','avg_turnaround'],['Respons','avg_response'],['Pergantian proses','context_switches']].map(([name,key])=>`<tr><td>${name}</td><td>${fmt(a.summary[key])}</td><td>${fmt(b.summary[key])}</td></tr>`).join('')}</tbody></table></div><p>${text} Ubah quantum untuk melihat pengaruhnya. Hasil ini berlaku untuk data yang kamu masukkan.</p></div>`;
}
function exportJSON(data,name){const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function runCPU(){
  error('#cpu-error');
  try {
    const processes=readProcesses(), algorithm=$('#algorithm').value;
    const quantum=algorithm==='fcfs'?2:integer($('#quantum').value,'Quantum',1,20);
    lockSetup('#panel-cpu',true);$('#cpu-output').innerHTML='<div class="card loading" role="status">Menghitung urutan proses…</div>';
    const names=algorithm==='compare'?['fcfs','rr']:[algorithm];
    const responses=await Promise.all(names.map(name=>request('/api/scheduling',{algorithm:name,processes,quantum})));
    const results=responses.map(d=>d.results[0]); cpuExport={processes,quantum,results};
    $('#cpu-output').innerHTML=(results.length===2?comparisonHTML(...results):'')+results.map(scheduleHTML).join('')+'<button id="export-cpu" class="text-button full">Simpan hasil JSON</button>';
    $('#export-cpu').addEventListener('click',()=>exportJSON(cpuExport,'hasil-penjadwalan.json'));
  } catch(e){error('#cpu-error',e.message); if($('#cpu-output .loading')) $('#cpu-output').innerHTML='<div class="card empty"><h3>Hasil belum tersedia</h3><p>Perbaiki masukan lalu jalankan kembali.</p></div>';}
  finally{lockSetup('#panel-cpu',false);}
}
function stopReplay(){clearInterval(timer);timer=null;const play=$('#play');if(play)play.textContent='Putar ulang';}
function renderReplay(){
  if(!replay)return;
  const event=replayIndex?replay.events[replayIndex-1]:null, items=event?event.items:[];
  const actor=event?event.actor.replace(/^(Produsen|Konsumen)-1$/,'$1'):'';
  $('#buffer-slots').innerHTML=Array.from({length:replay.capacity},(_,i)=>`<div class="slot ${i<items.length?'filled':''}">${i<items.length?esc(items[i]):'kosong'}</div>`).join('');
  $('#buffer-count').textContent=`${items.length} dari ${replay.capacity} tempat terisi`;
  $('#event-caption').innerHTML=event?`<strong>${esc(actor)} · ${esc(event.action)}</strong><br>${esc(event.detail)}<small>Langkah ${replayIndex} dari ${replay.events.length} · tercatat pada ${fmt(event.t)} ms</small>`:`<strong>Buffer mulai dalam keadaan kosong.</strong><small>Gunakan tombol Berikutnya atau Putar ulang untuk melihat kejadian satu per satu.</small>`;
  $('#replay-range').value=replayIndex;$('#previous').disabled=replayIndex===0;$('#next').disabled=replayIndex===replay.events.length;
  if(replayIndex===replay.events.length)stopReplay();
}
async function runPC(){
  error('#pc-error');stopReplay();
  try {
    const config={capacity:integer($('#capacity').value,'Kapasitas',1,10),items:integer($('#items').value,'Jumlah barang',1,12),producers:1,consumers:1,produce_ms:Number($('#produce-delay').value),consume_ms:Number($('#consume-delay').value)};
    lockSetup('#panel-pc',true);$('#pc-output').innerHTML='<div class="card loading" role="status">Produsen dan konsumen sedang bekerja…</div>';
    const data=await request('/api/ipc/producer-consumer',config);
    if(!data.completed||data.stuck_threads.length)throw Error('Percobaan tidak selesai. Coba lagi dengan jumlah barang lebih kecil.');
    replay=data;replayIndex=0;
    $('#pc-output').innerHTML=`<article class="card"><div class="result-heading"><h3>Perjalanan barang di buffer</h3><span class="pill">Percobaan selesai</span></div><p class="result-note">Ini pemutaran ulang kejadian dari thread nyata. Pemutaran diperlambat agar mudah diamati; bukan tampilan langsung saat thread berjalan.</p><div class="flow"><span class="actor">Produsen</span><span aria-hidden="true">→</span><span>Buffer</span><span aria-hidden="true">→</span><span class="actor">Konsumen</span></div><div id="buffer-slots" class="slots" role="img" aria-label="Isi buffer pada langkah terpilih"></div><p id="buffer-count" class="hint"></p><div id="event-caption" class="event-caption" aria-live="polite"></div><div class="playback"><button class="secondary" id="previous">Sebelumnya</button><button class="primary" id="play">Putar ulang</button><button class="secondary" id="next">Berikutnya</button></div><input class="range" id="replay-range" type="range" min="0" max="${data.events.length}" value="0" aria-label="Pilih langkah rekaman"><p class="playback-note">Satu langkah setiap 0,6 detik saat diputar. Waktu asli tertera pada kejadian.</p><details><summary>Mengapa perlu menunggu?</summary><p>Produsen perlu izin slot kosong sebelum menaruh barang. Konsumen perlu izin barang tersedia sebelum mengambilnya. Jika izin belum tersedia saat dicoba, thread menunggu semaphore.</p><p>Snapshot buffer menunjukkan isi saat pencatatan. Thread lain dapat mengubah keadaan antara percobaan memperoleh izin dan pencatatan kejadian menunggu.</p></details></article><article class="card"><h3>Hasil akhir percobaan</h3>${stats([['Barang dibuat',data.produced],['Barang diambil',data.consumed],['Isi tertinggi',data.peak_buffer_usage]])}<p class="result-note">Semua barang selesai dipindahkan. Buffer akhir kosong dan tidak melebihi kapasitas.</p><div class="table-scroll"><table><tbody><tr><td>Produsen sempat menunggu</td><td>${data.blocked_producers} kali</td></tr><tr><td>Konsumen sempat menunggu</td><td>${data.blocked_consumers} kali</td></tr><tr><td>Thread belum selesai</td><td>${data.stuck_threads.length}</td></tr></tbody></table></div><p class="hint">Jumlah menunggu bergantung urutan thread pada percobaan ini; bukan angka tetap.</p><button id="export-pc" class="text-button">Simpan hasil JSON</button></article>`;
    renderReplay();
    $('#previous').addEventListener('click',()=>{stopReplay();replayIndex=Math.max(0,replayIndex-1);renderReplay();});
    $('#next').addEventListener('click',()=>{stopReplay();replayIndex=Math.min(replay.events.length,replayIndex+1);renderReplay();});
    $('#replay-range').addEventListener('input',e=>{stopReplay();replayIndex=Number(e.target.value);renderReplay();});
    $('#play').addEventListener('click',()=>{if(timer){stopReplay();return;}if(replayIndex===replay.events.length){replayIndex=0;renderReplay();}$('#play').textContent='Jeda';timer=setInterval(()=>{replayIndex++;renderReplay();},600);});
    $('#export-pc').addEventListener('click',()=>exportJSON({config,...data},'hasil-producer-consumer.json'));
  } catch(e){error('#pc-error',e.message); if($('#pc-output .loading'))$('#pc-output').innerHTML='<div class="card empty"><h3>Percobaan belum selesai</h3><p>Periksa pesan kesalahan lalu coba kembali.</p></div>';}
  finally{lockSetup('#panel-pc',false);}
}
['cpu','pc'].forEach(name=>{$(`#tab-${name}`).addEventListener('click',()=>{stopReplay();['cpu','pc'].forEach(n=>{const active=n===name;$(`#panel-${n}`).hidden=!active;$(`#tab-${n}`).classList.toggle('active',active);$(`#tab-${n}`).setAttribute('aria-pressed',String(active));});});});
$('#algorithm').addEventListener('change',()=>{$('#quantum-field').hidden=$('#algorithm').value==='fcfs';$('#algorithm-help').textContent=$('#algorithm').value==='fcfs'?'Setiap proses dikerjakan sampai selesai, lalu proses berikutnya.':$('#algorithm').value==='rr'?'Proses bergantian sesuai jatah waktu, sampai semuanya selesai.':'Dua algoritma memakai data proses yang sama agar hasilnya dapat dibandingkan.';});
$('#sample').addEventListener('click',sample);
$('#add').addEventListener('click',()=>{error('#cpu-error');if($('#processes').rows.length>=12){error('#cpu-error','Maksimal 12 proses.');return;}const names=[...document.querySelectorAll('.pid')].map(el=>el.value.trim());let n=1;while(names.includes(`P${n}`))n++;$('#processes').insertAdjacentHTML('beforeend',processRow({pid:`P${n}`,arrival:0,burst:2}));});
$('#processes').addEventListener('click',e=>{if(!e.target.matches('.delete'))return;if($('#processes').rows.length===1){error('#cpu-error','Sisakan minimal satu proses.');return;}e.target.closest('tr').remove();error('#cpu-error');});
$('#run-cpu').addEventListener('click',runCPU);$('#run-pc').addEventListener('click',runPC);
$('#producer-fast').addEventListener('click',()=>{$('#produce-delay').value='10';$('#consume-delay').value='80';});
$('#consumer-fast').addEventListener('click',()=>{$('#produce-delay').value='80';$('#consume-delay').value='10';});
window.addEventListener('pagehide',stopReplay);sample();
