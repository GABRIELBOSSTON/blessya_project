/* ===================================================================
   Panel 3 - Deadlock: Banker's Algorithm, Deteksi, dan Recovery
   =================================================================== */

let bankerState = null; // keadaan terakhir, untuk mengisi pilihan proses

/* ---------------- A. Banker's Algorithm ---------------- */

/** Tabel Allocation / Max / Need / Available. */
function bankerTable(st) {
  const res = st.resources;
  const head =
    `<tr>
      <th rowspan="2">Proses</th>
      <th colspan="${res.length}">Allocation</th>
      <th colspan="${res.length}">Max</th>
      <th colspan="${res.length}">Need = Max - Alloc</th>
    </tr>
    <tr>${[...res, ...res, ...res].map((r) => `<th class="num">${esc(r)}</th>`).join("")}</tr>`;

  const body = st.processes
    .map((p, i) => {
      const cells = [
        ...st.allocation[i],
        ...st.maximum[i],
        ...st.need[i].map((v) => `<b style="color:var(--accent)">${v}</b>`),
      ];
      return `<tr><td>${esc(p)}</td>${cells.map((c) => `<td class="num">${c}</td>`).join("")}</tr>`;
    })
    .join("");

  const avail = res.map((r, j) => `${esc(r)}=${st.available[j]}`).join("  ");
  const total = res.map((r, j) => `${esc(r)}=${st.total[j]}`).join("  ");

  return `<div class="table-scroll"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>
    <div class="chips" style="margin-top:12px">
      ${chip("Available", avail)}
      ${chip("Total sistem", total)}
    </div>`;
}

function safetyHTML(s) {
  return `<div class="verdict ${s.safe ? "ok" : "bad"}">
      ${
        s.safe
          ? `SAFE STATE &mdash; safe sequence: <span class="seq">&lt; ${esc(s.sequence.join(" → "))} &gt;</span>`
          : `UNSAFE STATE &mdash; proses yang tidak bisa dijamin selesai: ${esc(s.unfinished.join(", "))}`
      }
    </div>
    ${
      s.safe
        ? `<p class="note">
            Artinya ada urutan eksekusi di mana setiap proses pasti bisa
            memperoleh seluruh kebutuhannya, selesai, lalu mengembalikan sumber
            dayanya untuk dipakai proses berikutnya.
          </p>`
        : `<p class="note">
            <b>Unsafe bukan berarti sudah deadlock.</b> Unsafe hanya berarti
            deadlock <i>mungkin</i> terjadi bila proses-proses itu benar-benar
            menarik kebutuhan maksimalnya. Banker&rsquo;s Algorithm menolak
            keadaan seperti ini karena tidak bisa lagi memberi jaminan.
          </p>`
    }
    ${logBlock(s.log, "Lihat jalannya Safety Algorithm langkah demi langkah")}`;
}

function bankerHTML(d) {
  bankerState = d.state;
  const sel = $("#bk-proc");
  sel.innerHTML = d.state.processes.map((p) => `<option>${esc(p)}</option>`).join("");
  $("#bk-amt").value = d.state.resources.map(() => "0").join(",");

  let html = `<h4>Keadaan sistem saat ini</h4>${bankerTable(d.state)}
    <h4>Hasil pemeriksaan</h4>${safetyHTML(d.safety)}`;

  if (d.request) html += requestHTML(d.request, d.state.resources);
  return html;
}

const REQ_TONE = { safe: "ok", unsafe: "bad", must_wait: "warn", exceeds_need: "bad" };
const REQ_TITLE = {
  safe: "DIKABULKAN",
  unsafe: "DITOLAK",
  must_wait: "DITUNDA",
  exceeds_need: "DITOLAK (kesalahan proses)",
};

function requestHTML(r, resources) {
  const tone = REQ_TONE[r.reason] || "warn";
  return `<h4>Hasil pengajuan permintaan</h4>
    <div class="verdict ${tone === "ok" ? "ok" : "bad"}">
      ${esc(REQ_TITLE[r.reason] || r.reason)} &mdash; ${esc(r.reason_text)}
    </div>
    ${
      r.reason === "unsafe"
        ? `<p class="note">
            Perhatikan baik-baik: sumber dayanya <b>tersedia</b>, tetapi
            permintaan tetap ditolak karena mengabulkannya akan membawa sistem
            ke unsafe state. Inilah sifat konservatif deadlock avoidance &mdash;
            ia mengorbankan sebagian pemanfaatan sumber daya untuk mendapat
            jaminan bahwa deadlock tidak akan pernah terjadi.
          </p>`
        : ""
    }
    ${
      r.reason === "exceeds_need"
        ? `<p class="note">
            Permintaan ini melebihi <code>Need</code>, artinya proses meminta
            lebih banyak daripada <code>Max</code> yang ia deklarasikan sendiri
            di awal. Ini kesalahan proses, bukan kekurangan sumber daya.
          </p>`
        : ""
    }
    ${logBlock(r.log, "Lihat ketiga tahap pemeriksaan permintaan")}`;
}

async function runBanker(btn, payload) {
  await withBusy(btn, "#bk-out", "#bk-err", async () => {
    const d = await api("/api/deadlock/bankers", payload || {});
    $("#bk-out").innerHTML = bankerHTML(d);
  });
}

async function runBankerRequest(btn) {
  await withBusy(btn, "#bk-out", "#bk-err", async () => {
    const amounts = $("#bk-amt")
      .value.split(",")
      .map((s) => parseInt(s.trim(), 10));
    if (amounts.some(Number.isNaN)) {
      throw new Error("Permintaan harus berupa angka dipisah koma, contoh: 1,0,2");
    }
    if (bankerState && amounts.length !== bankerState.resources.length) {
      throw new Error(
        `Harus ada ${bankerState.resources.length} angka (satu per jenis sumber daya: ${bankerState.resources.join(", ")}).`
      );
    }
    const d = await api("/api/deadlock/bankers", {
      example: bankerState && bankerState.processes.length === 3 ? "unsafe" : "classic",
      request: { process: $("#bk-proc").value, amounts },
    });
    $("#bk-out").innerHTML = bankerHTML(d);
  });
}

/* ---------------- B. Wait-For Graph ---------------- */

/** Gambar Wait-For Graph: node proses, panah menunjukkan siapa menunggu siapa. */
function wfgSVG(graph, cycles) {
  const procs = graph.processes;
  const n = procs.length;
  const cx = 190, cy = 125, r = 78;
  const pos = {};
  procs.forEach((p, i) => {
    const a = (i / n) * 2 * Math.PI - Math.PI / 2;
    pos[p] = { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
  });

  const inCycle = new Set(cycles.flat());
  const cycleEdges = new Set();
  cycles.forEach((c) => {
    for (let i = 0; i < c.length - 1; i++) cycleEdges.add(`${c[i]}->${c[i + 1]}`);
  });

  let edges = "";
  Object.entries(graph.wait_for_graph || {}).forEach(([from, list]) => {
    list.forEach((to) => {
      const a = pos[from], b = pos[to];
      if (!a || !b) return;
      // Pendekkan panah agar ujungnya tidak tertutup bulatan node.
      const dx = b.x - a.x, dy = b.y - a.y;
      const len = Math.hypot(dx, dy) || 1;
      const pad = 24;
      const x1 = a.x + (dx / len) * pad, y1 = a.y + (dy / len) * pad;
      const x2 = b.x - (dx / len) * pad, y2 = b.y - (dy / len) * pad;
      const bad = cycleEdges.has(`${from}->${to}`);
      edges += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}"
        x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
        stroke="${bad ? "#dc2626" : "#71717a"}" stroke-width="${bad ? 2.6 : 1.8}"
        marker-end="url(#${bad ? "arrowBad" : "arrowOk"})"/>`;
    });
  });

  let nodes = "";
  procs.forEach((p) => {
    const { x, y } = pos[p];
    const bad = inCycle.has(p);
    nodes += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="21"
        fill="${bad ? "#fee2e2" : "#ffffff"}" stroke="${bad ? "#dc2626" : "#18181b"}" stroke-width="2"/>
      <text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="middle"
        font-size="12" font-weight="700" fill="${bad ? "#991b1b" : "#111827"}">${esc(p)}</text>`;
  });

  return `<div class="graph-box">
    <svg viewBox="0 0 380 250" role="img" aria-label="Wait-For Graph">
      <defs>
        <marker id="arrowOk" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#71717a"/>
        </marker>
        <marker id="arrowBad" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/>
        </marker>
      </defs>
      ${edges}${nodes}
    </svg>
  </div>`;
}

function graphHTML(d) {
  const det = d.detection;
  const holdRows = Object.entries(d.graph.held_by).map(([r, p]) => [esc(r), esc(p)]);
  const waitRows = Object.entries(d.graph.waiting).map(([p, r]) => [esc(p), esc(r)]);

  return `<h4>Keadaan sumber daya</h4>
    <div class="phil-grid">
      <div style="flex:1;min-width:220px">
        ${table(["Sumber daya", "Dipegang oleh"], holdRows)}
      </div>
      <div style="flex:1;min-width:220px">
        ${table(["Proses", "Menunggu sumber daya"], waitRows)}
      </div>
    </div>
    <h4>Wait-For Graph</h4>
    <p class="note">
      Node sumber daya dihilangkan. Panah <b>P1 &rarr; P2</b> berarti
      &ldquo;P1 menunggu sumber daya yang sedang dipegang P2&rdquo;.
      Deadlock terjadi <b>jika dan hanya jika</b> graf ini punya siklus.
    </p>
    ${wfgSVG({ ...d.graph, wait_for_graph: det.wait_for_graph }, det.cycles)}
    <div class="verdict ${det.deadlock ? "bad" : "ok"}">
      ${
        det.deadlock
          ? `DEADLOCK TERDETEKSI &mdash; siklus: <span class="seq" style="color:var(--bad)">${det.cycles
              .map((c) => esc(c.join(" → ")))
              .join(" | ")}</span>`
          : "TIDAK ADA DEADLOCK &mdash; graf bebas siklus (asiklik)"
      }
    </div>
    ${logBlock(det.log, "Lihat proses pembangunan graf dan pencarian siklus")}`;
}

/* ---------------- C. Banyak instance + recovery ---------------- */

function multiHTML(d) {
  const st = d.state, det = d.detection;
  const res = st.resources;
  const head = `<tr>
      <th rowspan="2">Proses</th>
      <th colspan="${res.length}">Allocation</th>
      <th colspan="${res.length}">Request (diminta sekarang)</th>
    </tr>
    <tr>${[...res, ...res].map((r) => `<th class="num">${esc(r)}</th>`).join("")}</tr>`;
  const body = st.processes
    .map((p, i) => {
      const stuck = det.deadlocked_processes.includes(p);
      const cells = [...st.allocation[i], ...st.request[i]];
      return `<tr${stuck ? ' style="background:rgba(244,113,106,.08)"' : ""}>
        <td>${esc(p)}${stuck ? ' <span class="tag block">macet</span>' : ""}</td>
        ${cells.map((c) => `<td class="num">${c}</td>`).join("")}
      </tr>`;
    })
    .join("");

  let html = `<h4>Keadaan sistem</h4>
    <div class="table-scroll"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>
    <div class="chips" style="margin-top:12px">
      ${chip("Available", res.map((r, j) => `${esc(r)}=${st.available[j]}`).join("  "))}
    </div>
    <p class="note">
      Perhatikan kolomnya: di sini yang dipakai adalah <b>Request</b>
      (permintaan nyata saat ini), bukan <b>Need</b> (kebutuhan maksimal
      seperti pada Banker&rsquo;s Algorithm). Deteksi memeriksa apa yang
      sedang terjadi; avoidance memperkirakan apa yang mungkin terjadi.
    </p>
    <div class="verdict ${det.deadlock ? "bad" : "ok"}">
      ${
        det.deadlock
          ? `DEADLOCK TERDETEKSI &mdash; proses yang macet: ${esc(det.deadlocked_processes.join(", "))}`
          : `TIDAK ADA DEADLOCK &mdash; urutan penyelesaian: <span class="seq">&lt; ${esc(det.safe_order.join(" → "))} &gt;</span>`
      }
    </div>
    ${logBlock(det.log, "Lihat jalannya Detection Algorithm")}`;

  if (d.recovery) {
    const rec = d.recovery;
    html += `<h4>Recovery &mdash; terminasi proses korban</h4>
      <div class="verdict ${rec.resolved ? "ok" : "bad"}">${esc(rec.summary)}</div>
      ${table(
        ["Korban", "Sumber daya yang dilepas", "Alasan dipilih"],
        rec.victim_details.map((v) => [esc(v.process), `[${v.released.join(", ")}]`, esc(v.reason)])
      )}
      ${logBlock(rec.log, "Lihat putaran deteksi dan terminasi")}`;
  }

  if (d.recovery_comparison) {
    const minV = Math.min(...d.recovery_comparison.map((c) => c.victim_count));
    html += `<h4>Perbandingan strategi pemilihan korban</h4>
      ${table(
        ["Strategi", "Jumlah korban", "Korban", "Deadlock teratasi"],
        d.recovery_comparison.map((c) => ({
          __class: c.victim_count === minV ? "best" : "",
          cells: [
            esc(c.strategy),
            c.victim_count,
            esc(c.victims.join(", ")),
            c.resolved ? '<b style="color:var(--ok)">ya</b>' : '<b style="color:var(--bad)">tidak</b>',
          ],
        })),
        { numCols: [1] }
      )}
      <p class="note">
        Strategi <code>most_resources</code> biasanya memerlukan korban paling
        sedikit, karena mematikan satu proses yang memegang banyak sumber daya
        langsung membebaskan banyak sekaligus. Namun di sistem nyata pemilihan
        korban tidak hanya soal jumlah: prioritas proses, sudah berapa lama ia
        berjalan, dan apakah ia aman untuk di-restart juga diperhitungkan.
        Proses yang sedang menulis ke basis data misalnya, tidak boleh
        sembarangan dimatikan karena bisa meninggalkan data setengah jadi.
      </p>`;
  }

  return html;
}

/* ---------------- D. Ostrich ---------------- */

function ostrichHTML(o) {
  return `<h4>Ostrich Algorithm</h4>
    ${table(
      ["Aspek", "Keterangan"],
      [
        ["Tindakan saat deadlock", `<b>${esc(o.action_taken)}</b>`],
        ["Biaya / overhead", esc(o.overhead)],
        ["Cocok dipakai bila", esc(o.when_appropriate)],
        ["Tidak boleh dipakai di", esc(o.when_unacceptable)],
      ]
    )}
    <p class="note" style="margin-top:14px">${esc(o.explanation)}</p>
    <p class="note">
      Namanya berasal dari perumpamaan burung unta yang menyembunyikan kepala
      di pasir. Pendekatan ini <b>digunakan secara nyata</b>: UNIX dan Windows
      menerapkannya untuk banyak jenis sumber daya. Alasannya ekonomi &mdash; jika
      deadlock terjadi sekali setahun sementara pencegahannya memperlambat
      sistem setiap hari, maka merestart proses lebih murah daripada
      mencegahnya. Keputusannya adalah trade-off rekayasa, bukan kemalasan.
    </p>`;
}

/* ---------------- init ---------------- */

async function runDetection(btn, kind) {
  await withBusy(btn, "#det-out", "#det-err", async () => {
    let payload, render;
    if (kind === "graph-deadlock") {
      payload = { kind: "graph", example: "deadlock" };
      render = graphHTML;
    } else if (kind === "graph-safe") {
      payload = { kind: "graph", example: "safe" };
      render = graphHTML;
    } else if (kind === "multi") {
      payload = { kind: "multi" };
      render = multiHTML;
    } else {
      payload = { kind: "ostrich" };
      render = (d) => ostrichHTML(d.ostrich);
    }
    const d = await api("/api/deadlock/detection", payload);
    $("#det-out").innerHTML = render(d);
  });
}

function initDeadlock() {
  $("#run-banker").addEventListener("click", (e) => runBanker(e.target, {}));
  $("#run-banker-unsafe").addEventListener("click", (e) =>
    runBanker(e.target, { example: "unsafe" })
  );
  $("#run-banker-req").addEventListener("click", (e) => runBankerRequest(e.target));
  $$("[data-det]").forEach((b) =>
    b.addEventListener("click", (e) => runDetection(e.target, e.target.dataset.det))
  );
}
