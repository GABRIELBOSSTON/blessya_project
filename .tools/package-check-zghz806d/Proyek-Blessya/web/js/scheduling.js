/* ===================================================================
   Panel 1 - Penjadwalan Proses
   =================================================================== */

const SCHED_SAMPLE = [
  { pid: "P1", arrival: 0, burst: 8, priority: 3 },
  { pid: "P2", arrival: 1, burst: 4, priority: 1 },
  { pid: "P3", arrival: 2, burst: 9, priority: 4 },
  { pid: "P4", arrival: 3, burst: 5, priority: 2 },
];

/** Gambar satu baris data proses di tabel masukan. */
function procRow(p) {
  return `<tr>
    <td><input class="pid" value="${esc(p.pid)}" maxlength="8"></td>
    <td><input type="number" class="arr" value="${p.arrival}" min="0" max="100"></td>
    <td><input type="number" class="bur" value="${p.burst}" min="1" max="50"></td>
    <td><input type="number" class="pri" value="${p.priority}" min="0" max="99"></td>
    <td><button class="btn ghost del" title="Hapus baris ini">&times;</button></td>
  </tr>`;
}

function renderProcTable(list) {
  $("#proc-table tbody").innerHTML = list.map(procRow).join("");
}

/** Baca kembali isi tabel masukan menjadi daftar objek. */
function readProcTable() {
  return $$("#proc-table tbody tr").map((tr, i) => ({
    pid: $(".pid", tr).value.trim() || `P${i + 1}`,
    arrival: parseInt($(".arr", tr).value, 10) || 0,
    burst: parseInt($(".bur", tr).value, 10) || 1,
    priority: parseInt($(".pri", tr).value, 10) || 0,
  }));
}

/** Gantt chart: satu batang per segmen, lebarnya sebanding durasinya. */
function ganttHTML(timeline) {
  if (!timeline.length) return "";
  const total = timeline[timeline.length - 1].end;
  const bars = timeline
    .map((s) => {
      const pct = (s.duration / total) * 100;
      const isIdle = s.pid === "IDLE";
      const label = pct > 4 ? esc(s.pid) : "";
      return `<div class="gantt-seg ${isIdle ? "idle" : ""}"
        style="width:${pct}%;${isIdle ? "" : `background:${colorFor(s.pid)}`}"
        title="${esc(s.pid)}: ${s.start} sampai ${s.end} (durasi ${s.duration})">${label}</div>`;
    })
    .join("");

  // Penanda waktu di bawah: titik awal dan setiap batas segmen.
  const marks = [timeline[0].start, ...timeline.map((s) => s.end)];
  const ticks = [...new Set(marks)]
    .map((t) => `<span class="gantt-tick" style="left:${(t / total) * 100}%">${t}</span>`)
    .join("");

  return `<div class="gantt">
    <div class="gantt-bars">${bars}</div>
    <div class="gantt-axis">${ticks}</div>
  </div>`;
}

function metricsTable(metrics, summary) {
  const rows = metrics.map((m) => [
    esc(m.pid), m.arrival, m.burst, m.completion, m.turnaround, m.waiting, m.response,
  ]);
  rows.push({
    __class: "avg-row",
    cells: ["RATA-RATA", "", "", "", summary.avg_turnaround, summary.avg_waiting, summary.avg_response],
  });
  return table(
    ["Proses", "Arrival", "Burst", "Selesai", "Turnaround", "Waiting", "Response"],
    rows,
    { numCols: [1, 2, 3, 4, 5, 6] }
  );
}

function schedResultHTML(r, best) {
  const s = r.summary;
  const isBestWait = r.algorithm === best.best_avg_waiting;
  const isBestResp = r.algorithm === best.best_avg_response;
  const badges = [];
  if (isBestWait) badges.push("waiting time terkecil");
  if (isBestResp) badges.push("response time terkecil");

  return `<div class="result ${badges.length ? "ok" : ""}">
    <h4>${esc(r.algorithm)}</h4>
    ${badges.length ? `<p class="desc">Terbaik untuk: ${esc(badges.join(", "))}</p>` : ""}
    ${ganttHTML(r.timeline)}
    <div class="chips">
      ${chip("Avg waiting", s.avg_waiting, isBestWait ? "good" : "")}
      ${chip("Avg turnaround", s.avg_turnaround)}
      ${chip("Avg response", s.avg_response, isBestResp ? "good" : "")}
      ${chip("Utilisasi CPU", s.cpu_utilization + "%")}
      ${chip("Total waktu", s.total_time)}
      ${chip("Context switch", s.context_switches)}
    </div>
    ${metricsTable(r.metrics, s)}
    ${logBlock(r.log, "Lihat keputusan scheduler langkah demi langkah")}
  </div>`;
}

/** Tabel ringkas yang membandingkan semua algoritma sekaligus. */
function comparisonTable(results, insight) {
  const minWait = Math.min(...results.map((r) => r.summary.avg_waiting));
  const minResp = Math.min(...results.map((r) => r.summary.avg_response));
  const rows = results.map((r) => {
    const s = r.summary;
    const best = s.avg_waiting === minWait;
    return {
      __class: best ? "best" : "",
      cells: [
        esc(r.algorithm),
        s.avg_waiting, s.avg_turnaround, s.avg_response,
        s.cpu_utilization + "%", s.context_switches,
      ],
    };
  });

  return `<div class="card">
    <h3>Tabel Perbandingan</h3>
    <p class="note">
      Seluruh algoritma dijalankan pada data proses yang sama, sehingga
      perbedaan angkanya murni berasal dari algoritmanya.
    </p>
    ${table(
      ["Algoritma", "Avg Waiting", "Avg Turnaround", "Avg Response", "Utilisasi CPU", "Context Switch"],
      rows,
      { numCols: [1, 2, 3, 4, 5] }
    )}
    <h4>Analisis</h4>
    <p class="note">
      <b>Average waiting time</b> terkecil dicapai
      <b>${esc(insight.best_avg_waiting)}</b> (${insight.best_avg_waiting_value}),
      sedangkan <b>average response time</b> terkecil dicapai
      <b>${esc(insight.best_avg_response)}</b> (${insight.best_avg_response_value}).
    </p>
    <p class="note">
      Kedua ukuran itu sering dimenangkan algoritma yang berbeda, dan di situlah
      inti persoalannya: tidak ada algoritma yang terbaik untuk segala keadaan.
      SJF dan SRTF unggul pada waiting time, tetapi membutuhkan burst time yang
      di sistem nyata tidak diketahui sebelum proses jalan, dan berisiko membuat
      proses panjang tidak pernah dilayani (starvation). Round Robin memberi
      response time yang merata sehingga sistem terasa responsif, dengan biaya
      jumlah context switch yang lebih besar.
    </p>
  </div>`;
}

async function runScheduling(btn) {
  await withBusy(btn, "#sched-out", "#sched-err", async () => {
    const data = await api("/api/scheduling", {
      algorithm: "all",
      processes: readProcTable(),
      quantum: parseInt($("#quantum").value, 10) || 2,
    });
    const blocks = data.results.map((r) => schedResultHTML(r, data.insight)).join("");
    $("#sched-out").innerHTML =
      comparisonTable(data.results, data.insight) +
      `<div class="card"><h3>Hasil Rinci per Algoritma</h3>
        <p class="note">Arahkan kursor ke batang Gantt chart untuk melihat waktu mulai dan selesainya.</p>
        ${blocks}</div>`;
  });
}

function initScheduling() {
  renderProcTable(SCHED_SAMPLE);

  $("#add-proc").addEventListener("click", () => {
    const n = $$("#proc-table tbody tr").length;
    if (n >= 12) {
      showErr("#sched-err", "Maksimal 12 proses agar tampilan tetap terbaca.");
      return;
    }
    $("#proc-table tbody").insertAdjacentHTML(
      "beforeend",
      procRow({ pid: `P${n + 1}`, arrival: n, burst: 4, priority: 0 })
    );
  });

  $("#reset-proc").addEventListener("click", () => {
    renderProcTable(SCHED_SAMPLE);
    clearErr("#sched-err");
  });

  // Satu listener untuk semua tombol hapus, termasuk baris yang
  // ditambahkan nanti (event delegation).
  $("#proc-table").addEventListener("click", (e) => {
    if (!e.target.classList.contains("del")) return;
    if ($$("#proc-table tbody tr").length <= 1) {
      showErr("#sched-err", "Harus ada minimal satu proses.");
      return;
    }
    e.target.closest("tr").remove();
  });

  $("#run-sched").addEventListener("click", (e) => runScheduling(e.target));
}
