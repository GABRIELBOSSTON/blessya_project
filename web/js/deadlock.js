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
      <th rowspan="2">Process</th>
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
      ${chip("System total", total)}
    </div>`;
}

function safetyHTML(s) {
  return `<div class="verdict ${s.safe ? "ok" : "bad"}">
      ${
        s.safe
          ? `SAFE STATE &mdash; safe sequence: <span class="seq">&lt; ${esc(s.sequence.join(" → "))} &gt;</span>`
          : `UNSAFE STATE &mdash; processes that cannot be guaranteed to finish: ${esc(s.unfinished.join(", "))}`
      }
    </div>
    ${
      s.safe
        ? `<p class="note">
            This means there exists an execution order where every process can
            obtain all its needs, finish, then return its resources
            for the next process to use.
          </p>`
        : `<p class="note">
            <b>Unsafe does not mean deadlock has occurred.</b> Unsafe only means
            deadlock <i>could</i> happen if those processes actually
            request their maximum needs. Banker&rsquo;s Algorithm rejects
            such states because it can no longer provide a guarantee.
          </p>`
    }
    ${logBlock(s.log, "View the Safety Algorithm step by step")}`;
}

function bankerHTML(d) {
  bankerState = d.state;
  const sel = $("#bk-proc");
  sel.innerHTML = d.state.processes.map((p) => `<option>${esc(p)}</option>`).join("");
  $("#bk-amt").value = d.state.resources.map(() => "0").join(",");

  let html = `<h4>Current system state</h4>${bankerTable(d.state)}
    <h4>Check result</h4>${safetyHTML(d.safety)}`;

  if (d.request) html += requestHTML(d.request, d.state.resources);
  return html;
}

const REQ_TONE = { safe: "ok", unsafe: "bad", must_wait: "warn", exceeds_need: "bad" };
const REQ_TITLE = {
  safe: "GRANTED",
  unsafe: "DENIED",
  must_wait: "DEFERRED",
  exceeds_need: "DENIED (process error)",
};

function requestHTML(r, resources) {
  const tone = REQ_TONE[r.reason] || "warn";
  return `<h4>Request result</h4>
    <div class="verdict ${tone === "ok" ? "ok" : "bad"}">
      ${esc(REQ_TITLE[r.reason] || r.reason)} &mdash; ${esc(r.reason_text)}
    </div>
    ${
      r.reason === "unsafe"
        ? `<p class="note">
            Pay close attention: the resources <b>are available</b>, but
            the request is still denied because granting it would bring the system
            to an unsafe state. This is the conservative nature of deadlock avoidance &mdash;
            it sacrifices some resource utilization to guarantee
            that deadlock will never occur.
          </p>`
        : ""
    }
    ${
      r.reason === "exceeds_need"
        ? `<p class="note">
            This request exceeds <code>Need</code>, meaning the process is requesting
            more than the <code>Max</code> it declared itself
            at the beginning. This is a process error, not a resource shortage.
          </p>`
        : ""
    }
    ${logBlock(r.log, "View the three request verification stages")}`;
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
      throw new Error("Request must be numbers separated by commas, e.g.: 1,0,2");
    }
    if (bankerState && amounts.length !== bankerState.resources.length) {
      throw new Error(
        `Must have ${bankerState.resources.length} numbers (one per resource type: ${bankerState.resources.join(", ")}).`
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

  return `<h4>Resource state</h4>
    <div class="phil-grid">
      <div style="flex:1;min-width:220px">
        ${table(["Resource", "Held by"], holdRows)}
      </div>
      <div style="flex:1;min-width:220px">
        ${table(["Process", "Waiting for resource"], waitRows)}
      </div>
    </div>
    <h4>Wait-For Graph</h4>
    <p class="note">
      Resource nodes are removed. An arrow <b>P1 &rarr; P2</b> means
      &ldquo;P1 is waiting for a resource currently held by P2&rdquo;.
      Deadlock occurs <b>if and only if</b> this graph has a cycle.
    </p>
    ${wfgSVG({ ...d.graph, wait_for_graph: det.wait_for_graph }, det.cycles)}
    <div class="verdict ${det.deadlock ? "bad" : "ok"}">
      ${
        det.deadlock
          ? `DEADLOCK DETECTED &mdash; cycle: <span class="seq" style="color:var(--bad)">${det.cycles
              .map((c) => esc(c.join(" → ")))
              .join(" | ")}</span>`
          : "NO DEADLOCK &mdash; graph is cycle-free (acyclic)"
      }
    </div>
    ${logBlock(det.log, "View graph construction and cycle detection process")}`;
}

/* ---------------- C. Banyak instance + recovery ---------------- */

function multiHTML(d) {
  const st = d.state, det = d.detection;
  const res = st.resources;
  const head = `<tr>
      <th rowspan="2">Process</th>
      <th colspan="${res.length}">Allocation</th>
      <th colspan="${res.length}">Request (currently requested)</th>
    </tr>
    <tr>${[...res, ...res].map((r) => `<th class="num">${esc(r)}</th>`).join("")}</tr>`;
  const body = st.processes
    .map((p, i) => {
      const stuck = det.deadlocked_processes.includes(p);
      const cells = [...st.allocation[i], ...st.request[i]];
      return `<tr${stuck ? ' style="background:rgba(244,113,106,.08)"' : ""}>
        <td>${esc(p)}${stuck ? ' <span class="tag block">stuck</span>' : ""}</td>
        ${cells.map((c) => `<td class="num">${c}</td>`).join("")}
      </tr>`;
    })
    .join("");

  let html = `<h4>System state</h4>
    <div class="table-scroll"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>
    <div class="chips" style="margin-top:12px">
      ${chip("Available", res.map((r, j) => `${esc(r)}=${st.available[j]}`).join("  "))}
    </div>
    <p class="note">
      Note the columns: here <b>Request</b> is used
      (actual current requests), not <b>Need</b> (maximum needs
      as in Banker&rsquo;s Algorithm). Detection checks what is
      currently happening; avoidance estimates what might happen.
    </p>
    <div class="verdict ${det.deadlock ? "bad" : "ok"}">
      ${
        det.deadlock
          ? `DEADLOCK DETECTED &mdash; stuck processes: ${esc(det.deadlocked_processes.join(", "))}`
          : `NO DEADLOCK &mdash; completion order: <span class="seq">&lt; ${esc(det.safe_order.join(" → "))} &gt;</span>`
      }
    </div>
    ${logBlock(det.log, "View the Detection Algorithm steps")}`;

  if (d.recovery) {
    const rec = d.recovery;
    html += `<h4>Recovery &mdash; victim process termination</h4>
      <div class="verdict ${rec.resolved ? "ok" : "bad"}">${esc(rec.summary)}</div>
      ${table(
        ["Victim", "Released resources", "Reason chosen"],
        rec.victim_details.map((v) => [esc(v.process), `[${v.released.join(", ")}]`, esc(v.reason)])
      )}
      ${logBlock(rec.log, "View detection and termination rounds")}`;
  }

  if (d.recovery_comparison) {
    const minV = Math.min(...d.recovery_comparison.map((c) => c.victim_count));
    html += `<h4>Victim selection strategy comparison</h4>
      ${table(
        ["Strategy", "Victim count", "Victims", "Deadlock resolved"],
        d.recovery_comparison.map((c) => ({
          __class: c.victim_count === minV ? "best" : "",
          cells: [
            esc(c.strategy),
            c.victim_count,
            esc(c.victims.join(", ")),
            c.resolved ? '<b style="color:var(--ok)">yes</b>' : '<b style="color:var(--bad)">no</b>',
          ],
        })),
        { numCols: [1] }
      )}
      <p class="note">
        The <code>most_resources</code> strategy usually requires the fewest
        victims, because terminating one process holding many resources
        immediately frees many at once. However, in real systems victim
        selection is not just about quantity: process priority, how long it has
        been running, and whether it is safe to restart are also considered.
        A process writing to a database, for example, should not be
        terminated carelessly as it could leave data in an inconsistent state.
      </p>`;
  }

  return html;
}

/* ---------------- D. Ostrich ---------------- */

function ostrichHTML(o) {
  return `<h4>Ostrich Algorithm</h4>
    ${table(
      ["Aspect", "Description"],
      [
        ["Action on deadlock", `<b>${esc(o.action_taken)}</b>`],
        ["Cost / overhead", esc(o.overhead)],
        ["Appropriate when", esc(o.when_appropriate)],
        ["Unacceptable for", esc(o.when_unacceptable)],
      ]
    )}
    <p class="note" style="margin-top:14px">${esc(o.explanation)}</p>
    <p class="note">
      The name comes from the metaphor of an ostrich burying its head
      in the sand. This approach is <b>used in practice</b>: UNIX and Windows
      employ it for many types of resources. The reason is economic &mdash; if
      deadlock occurs once a year while prevention slows down
      the system every day, then restarting processes is cheaper than
      preventing it. The decision is an engineering trade-off, not laziness.
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
