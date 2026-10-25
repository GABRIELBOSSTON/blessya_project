/* ===================================================================
   Panel 2 - Thread, Race Condition, dan IPC
   =================================================================== */

/* ---------------- A. Race condition ---------------- */

function raceHTML(d) {
  const rows = d.trials.map((t) => {
    const broken = t.lost !== 0;
    return {
      __class: broken ? "" : "best",
      cells: [
        t.trial,
        t.expected.toLocaleString("en-US"),
        `<b style="color:${broken ? "var(--bad)" : "var(--ok)"}">${t.unsafe.toLocaleString("en-US")}</b>`,
        t.lost.toLocaleString("en-US"),
        t.percent + "%",
        `<b style="color:var(--ok)">${t.safe.toLocaleString("en-US")}</b>`,
      ],
    };
  });

  const anyBroken = d.runs_corrupted > 0;

  return `<div class="verdict ${anyBroken ? "bad" : "ok"}">
      ${esc(d.conclusion)}
    </div>
    ${table(
      ["Trial", "Expected", "Without Lock", "Lost", "Corrupted", "With Lock"],
      rows,
      { numCols: [0, 1, 2, 3, 4, 5] }
    )}
    <h4>Why this happens</h4>
    <p class="note">
      The instruction <code>counter = counter + 1</code> looks like a single step,
      but at the machine level it consists of three separate steps:
      <b>read</b> the value from memory, <b>add</b> one, then <b>write</b> it back.
      If thread A is preempted right after reading, then thread B completes
      all three steps, when A resumes it writes the old value
      plus one &mdash; overwriting B's work. One increment is lost.
    </p>
    <p class="note">
      The region of memory that should only be accessed by one thread at a time is called
      the <b>critical section</b>. A <b>mutex</b> guards it by forcing other threads
      to wait at the door until the one inside finishes.
    </p>
    ${
      !anyBroken
        ? `<p class="note" style="color:var(--warn)">
            <b>Note:</b> in this trial the result without lock happened to be correct,
            but the code is still unsafe. This is why race conditions are dangerous:
            errors can pass many tests, then corrupt data
            under different conditions.
          </p>`
        : ""
    }`;
}

async function runRace(btn) {
  await withBusy(btn, "#race-out", "#race-err", async () => {
    const d = await api("/api/ipc/race", {
      threads: parseInt($("#race-threads").value, 10),
      increments: parseInt($("#race-incr").value, 10),
      trials: parseInt($("#race-trials").value, 10),
      force_preemption: $("#race-force").checked,
    });
    $("#race-out").innerHTML = raceHTML(d);
  });
}

/* ---------------- B. Producer - Consumer ---------------- */

const PC_TAG = {
  PRODUCE: "prod", CONSUME: "cons", BLOCKED: "block", RESUMED: "cont",
};

function pcHTML(d) {
  const timeline = d.events
    .map((e) => {
      const slots = Array.from({ length: e.buffer_capacity }, (_, i) =>
        `<span class="slot ${i < e.buffer_size ? "filled" : ""}"></span>`
      ).join("");
      return `<div class="buffer-row">
        <span class="buffer-time">${e.t} ms</span>
        <span class="buffer-actor">${esc(e.actor)}</span>
        <span class="tag ${PC_TAG[e.action] || ""}">${esc(e.action)}</span>
        <span class="buffer-slots">${slots}</span>
        <span class="buffer-detail">${esc(e.detail)}</span>
      </div>`;
    })
    .join("");

  return `<div class="chips">
      ${chip("Produced", d.produced)}
      ${chip("Consumed", d.consumed)}
      ${chip("Peak usage", `${d.peak_buffer_usage} / ${d.capacity}`, d.overflow_detected ? "bad" : "good")}
      ${chip("Producer blocked", d.blocked_producers, d.blocked_producers ? "warn" : "")}
      ${chip("Consumer blocked", d.blocked_consumers, d.blocked_consumers ? "warn" : "")}
    </div>
    <div class="verdict ${d.overflow_detected || !d.balanced ? "bad" : "ok"}">
      ${esc(d.conclusion)}
    </div>
    <h4>Event timeline</h4>
    <p class="note">
      Black boxes indicate filled buffer slots. Note that the number of
      black boxes <b>never exceeds the capacity</b>, and whenever the buffer
      is full, the producer is automatically labeled <span class="tag block">BLOCKED</span>
      until the consumer frees a slot.
    </p>
    <div>${timeline}</div>
    <h4>Role of each synchronization tool</h4>
    <p class="note">
      <code>empty</code> is a semaphore counting empty slots; the producer
      waits here when the buffer is full.
      <code>full</code> counts filled slots; the consumer waits here when the
      buffer is empty.
      <code>mutex</code> protects operations on the buffer itself so that two
      threads do not modify it simultaneously.
    </p>
    <p class="note">
      The order must not be reversed. If the mutex is locked before
      waiting for an empty slot, the producer could hold the mutex while sleeping
      waiting for a slot &mdash; while the consumer that could free a slot
      cannot enter because the mutex is held. Both wait for each other
      forever: that is deadlock.
    </p>`;
}

async function runPC(btn) {
  await withBusy(btn, "#pc-out", "#pc-err", async () => {
    const d = await api("/api/ipc/producer-consumer", {
      capacity: parseInt($("#pc-cap").value, 10),
      producers: parseInt($("#pc-prod").value, 10),
      consumers: parseInt($("#pc-cons").value, 10),
      items: parseInt($("#pc-items").value, 10),
    });
    $("#pc-out").innerHTML = pcHTML(d);
  });
}

/* ---------------- C. Dining Philosophers ---------------- */

/** Gambar meja bundar: 5 filsuf dan 5 garpu di antaranya. */
function philSVG(snapshot, deadlocked) {
  const N = 5, cx = 150, cy = 150, rP = 100, rF = 62;
  let out = "";

  // Garpu di antara setiap dua filsuf.
  for (let i = 0; i < N; i++) {
    const a = (i / N) * 2 * Math.PI - Math.PI / 2 + Math.PI / N;
    const x = cx + rF * Math.cos(a), y = cy + rF * Math.sin(a);
    const holder = Object.entries(snapshot).find(([, s]) => s.holding.includes(i + 1));
    const used = Boolean(holder);
    out += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="11"
        fill="${used ? "#fef3c7" : "#f4f4f5"}" stroke="${used ? "#d97706" : "#a1a1aa"}" stroke-width="2"/>
      <text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="middle"
        font-size="11" font-weight="700" fill="${used ? "#78350f" : "#52525b"}">${i + 1}</text>`;
  }

  // Filsuf.
  for (let i = 0; i < N; i++) {
    const a = (i / N) * 2 * Math.PI - Math.PI / 2;
    const x = cx + rP * Math.cos(a), y = cy + rP * Math.sin(a);
    const st = snapshot[`F${i + 1}`] || { holding: [], waiting_for: null, meals_eaten: 0 };
    let fill = "#f4f4f5", label = "#52525b", ring = "#a1a1aa";
    if (st.waiting_for) { fill = "#fee2e2"; label = "#991b1b"; ring = "#dc2626"; }
    else if (st.holding.length === 2) { fill = "#dcfce7"; label = "#14532d"; ring = "#16a34a"; }
    else if (st.holding.length === 1) { fill = "#fef3c7"; label = "#78350f"; ring = "#d97706"; }

    out += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="23"
        fill="${fill}" stroke="${ring}" stroke-width="2"/>
      <text x="${x.toFixed(1)}" y="${(y - 1).toFixed(1)}" text-anchor="middle"
        font-size="12" font-weight="700" fill="${label}">F${i + 1}</text>
      <text x="${x.toFixed(1)}" y="${(y + 11).toFixed(1)}" text-anchor="middle"
        font-size="9" fill="${label}">${st.meals_eaten}x</text>`;
  }

  return `<div class="graph-box">
    <svg viewBox="0 0 300 300" role="img" aria-label="Round table with five philosophers">
      <circle cx="${cx}" cy="${cy}" r="40" fill="none" stroke="#d4d4d8" stroke-width="1" stroke-dasharray="3 3"/>
      <text x="${cx}" y="${cy + 4}" text-anchor="middle" font-size="11"
        fill="${deadlocked ? "#dc2626" : "#15803d"}" font-weight="700">
        ${deadlocked ? "DEADLOCK" : "OK"}
      </text>
      ${out}
    </svg>
  </div>`;
}

function philOne(r) {
  const rows = Object.entries(r.state_snapshot).map(([who, s]) => [
    esc(who),
    s.holding.length ? s.holding.join(", ") : "&mdash;",
    s.waiting_for ? `<b style="color:var(--bad)">${s.waiting_for}</b>` : "&mdash;",
    s.meals_eaten,
  ]);

  return `<div class="result ${r.deadlocked ? "bad" : "ok"}">
    <h4>${esc(r.strategy_label)}</h4>
    <div class="verdict ${r.deadlocked ? "bad" : "ok"}">${esc(r.conclusion)}</div>
    <div class="phil-grid">
      <div class="phil-table">${philSVG(r.state_snapshot, r.deadlocked)}</div>
      <div style="flex:1;min-width:260px">
        ${table(["Philosopher", "Holding forks", "Waiting for fork", "Meals eaten"], rows, { numCols: [3] })}
        ${
          r.cycle && r.cycle.length
            ? `<p class="note" style="margin-top:12px">
                <b style="color:var(--bad)">Circular wait detected:</b>
                <span class="seq" style="color:var(--bad)">${esc(r.cycle.join(" → "))}</span><br>
                Each philosopher holds one fork and waits for the fork
                held by its neighbor. This wait cycle is the
                fourth Coffman condition.
              </p>`
            : ""
        }
      </div>
    </div>
  </div>`;
}

function philHTML(d) {
  const sum = table(
    ["Strategy", "Deadlock", "Meals eaten"],
    d.summary.map((s) => ({
      __class: s.deadlocked ? "" : "best",
      cells: [
        esc(s.label),
        s.deadlocked
          ? '<b style="color:var(--bad)">YES</b>'
          : '<b style="color:var(--ok)">no</b>',
        `${s.total_eaten} / ${s.target}`,
      ],
    })),
    { numCols: [2] }
  );

  return `<h4>Summary</h4>
    ${sum}
    <p class="note" style="margin-top:12px">
      Color key: <b style="color:var(--ok)">green</b> = eating
      (holding 2 forks), <b style="color:var(--warn)">yellow</b> = holding
      1 fork, <b style="color:var(--bad)">red</b> = waiting for a fork,
      gray = thinking or finished.
    </p>
    ${d.results.map(philOne).join("")}
    <h4>Why both solutions succeed</h4>
    <p class="note">
      <b>Resource ordering</b> breaks <i>circular wait</i>. Because all philosophers
      must pick up the lower-numbered fork first, a wait cycle is impossible:
      there is always one philosopher whose request is the most
      "downstream" and can therefore be fulfilled.
    </p>
    <p class="note">
      <b>Waiter / semaphore</b> effectively breaks <i>hold and wait</i>
      by limiting only 4 philosophers to attempt eating simultaneously.
      With 4 people competing for 5 forks, there is always at least one person who can
      get two forks, so the system cannot be completely stuck.
    </p>`;
}

async function runPhil(btn) {
  await withBusy(btn, "#ph-out", "#ph-err", async () => {
    const d = await api("/api/ipc/philosophers", {
      strategy: "all",
      meals: parseInt($("#ph-meals").value, 10),
    });
    $("#ph-out").innerHTML = philHTML(d);
  });
}

function initIPC() {
  $("#run-race").addEventListener("click", (e) => runRace(e.target));
  $("#run-pc").addEventListener("click", (e) => runPC(e.target));
  $("#run-ph").addEventListener("click", (e) => runPhil(e.target));
}
