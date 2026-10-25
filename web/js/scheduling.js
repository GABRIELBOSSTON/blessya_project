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
    <td><button class="btn ghost del" title="Delete this row">&times;</button></td>
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
        title="${esc(s.pid)}: ${s.start} to ${s.end} (duration ${s.duration})">${label}</div>`;
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
    cells: ["AVERAGE", "", "", "", summary.avg_turnaround, summary.avg_waiting, summary.avg_response],
  });
  return table(
    ["Process", "Arrival", "Burst", "Completion", "Turnaround", "Waiting", "Response"],
    rows,
    { numCols: [1, 2, 3, 4, 5, 6] }
  );
}

function schedResultHTML(r, best) {
  const s = r.summary;
  const isBestWait = r.algorithm === best.best_avg_waiting;
  const isBestResp = r.algorithm === best.best_avg_response;
  const badges = [];
  if (isBestWait) badges.push("lowest waiting time");
  if (isBestResp) badges.push("lowest response time");

  return `<div class="result ${badges.length ? "ok" : ""}">
    <h4>${esc(r.algorithm)}</h4>
    ${badges.length ? `<p class="desc">Best for: ${esc(badges.join(", "))}</p>` : ""}
    ${ganttHTML(r.timeline)}
    <div class="chips">
      ${chip("Avg waiting", s.avg_waiting, isBestWait ? "good" : "")}
      ${chip("Avg turnaround", s.avg_turnaround)}
      ${chip("Avg response", s.avg_response, isBestResp ? "good" : "")}
      ${chip("CPU utilization", s.cpu_utilization + "%")}
      ${chip("Total time", s.total_time)}
      ${chip("Context switches", s.context_switches)}
    </div>
    ${metricsTable(r.metrics, s)}
    ${logBlock(r.log, "View scheduler decisions step by step")}
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
    <h3>Comparison Table</h3>
    <p class="note">
      All algorithms are run on the same process data, so the
      differences in numbers purely come from the algorithms themselves.
    </p>
    ${table(
      ["Algorithm", "Avg Waiting", "Avg Turnaround", "Avg Response", "CPU Utilization", "Context Switches"],
      rows,
      { numCols: [1, 2, 3, 4, 5] }
    )}
    <h4>Analysis</h4>
    <p class="note">
      The lowest <b>average waiting time</b> is achieved by
      <b>${esc(insight.best_avg_waiting)}</b> (${insight.best_avg_waiting_value}),
      while the lowest <b>average response time</b> is achieved by
      <b>${esc(insight.best_avg_response)}</b> (${insight.best_avg_response_value}).
    </p>
    <p class="note">
      These two measures are often won by different algorithms, and therein lies
      the core issue: no single algorithm is best for all situations.
      SJF and SRTF excel at waiting time, but require burst time which
      in real systems is unknown before a process runs, and risk making
      long processes never get served (starvation). Round Robin provides
      evenly distributed response time making the system feel responsive, at the cost
      of a higher number of context switches.
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
      `<div class="card"><h3>Detailed Results per Algorithm</h3>
        <p class="note">Hover over Gantt chart bars to see start and end times.</p>
        ${blocks}</div>`;
  });
}

function initScheduling() {
  renderProcTable(SCHED_SAMPLE);

  $("#add-proc").addEventListener("click", () => {
    const n = $$("#proc-table tbody tr").length;
    if (n >= 12) {
      showErr("#sched-err", "Maximum 12 processes to keep the display readable.");
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
      showErr("#sched-err", "There must be at least one process.");
      return;
    }
    e.target.closest("tr").remove();
  });

  $("#run-sched").addEventListener("click", (e) => runScheduling(e.target));
}
