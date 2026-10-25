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
        t.expected.toLocaleString("id-ID"),
        `<b style="color:${broken ? "var(--bad)" : "var(--ok)"}">${t.unsafe.toLocaleString("id-ID")}</b>`,
        t.lost.toLocaleString("id-ID"),
        t.percent + "%",
        `<b style="color:var(--ok)">${t.safe.toLocaleString("id-ID")}</b>`,
      ],
    };
  });

  const anyBroken = d.runs_corrupted > 0;

  return `<div class="verdict ${anyBroken ? "bad" : "ok"}">
      ${esc(d.conclusion)}
    </div>
    ${table(
      ["Percobaan", "Seharusnya", "Tanpa Lock", "Hilang", "Rusak", "Dengan Lock"],
      rows,
      { numCols: [0, 1, 2, 3, 4, 5] }
    )}
    <h4>Mengapa ini terjadi</h4>
    <p class="note">
      Perintah <code>counter = counter + 1</code> terlihat seperti satu langkah,
      tetapi di tingkat mesin ia terdiri dari tiga langkah terpisah:
      <b>baca</b> nilai dari memori, <b>tambah</b> satu, lalu <b>tulis</b> kembali.
      Bila thread A disela tepat setelah membaca, lalu thread B menyelesaikan
      ketiga langkahnya, maka ketika A melanjutkan ia menuliskan nilai lama
      ditambah satu &mdash; menimpa hasil kerja B. Satu increment hilang.
    </p>
    <p class="note">
      Bagian memori yang hanya boleh diakses satu thread pada satu waktu disebut
      <b>critical section</b>. <b>Mutex</b> menjaganya dengan memaksa thread lain
      menunggu di depan pintu sampai yang di dalam selesai.
    </p>
    ${
      !anyBroken
        ? `<p class="note" style="color:var(--warn)">
            <b>Catatan penting:</b> kali ini hasil tanpa lock kebetulan benar,
            tetapi kodenya TETAP salah. Inilah yang membuat race condition
            berbahaya &mdash; ia bisa lolos pengujian berkali-kali lalu
            merusak data di keadaan lain.
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
  PRODUKSI: "prod", KONSUMSI: "cons", BLOKIR: "block", LANJUT: "cont",
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
      ${chip("Diproduksi", d.produced)}
      ${chip("Dikonsumsi", d.consumed)}
      ${chip("Isi tertinggi", `${d.peak_buffer_usage} / ${d.capacity}`, d.overflow_detected ? "bad" : "good")}
      ${chip("Produsen diblokir", d.blocked_producers, d.blocked_producers ? "warn" : "")}
      ${chip("Konsumen diblokir", d.blocked_consumers, d.blocked_consumers ? "warn" : "")}
    </div>
    <div class="verdict ${d.overflow_detected || !d.balanced ? "bad" : "ok"}">
      ${esc(d.conclusion)}
    </div>
    <h4>Garis waktu kejadian</h4>
    <p class="note">
      Kotak biru menunjukkan slot buffer yang terisi. Perhatikan bahwa jumlah
      kotak biru <b>tidak pernah melebihi kapasitas</b>, dan setiap kali buffer
      penuh, produsen otomatis berlabel <span class="tag block">BLOKIR</span>
      sampai konsumen mengosongkan satu slot.
    </p>
    <div>${timeline}</div>
    <h4>Peran setiap alat sinkronisasi</h4>
    <p class="note">
      <code>empty</code> adalah semaphore penghitung slot kosong; produsen
      menunggu di sini ketika buffer penuh.
      <code>full</code> menghitung slot terisi; konsumen menunggu di sini ketika
      buffer kosong.
      <code>mutex</code> melindungi operasi pada buffer itu sendiri agar dua
      thread tidak mengubahnya bersamaan.
    </p>
    <p class="note">
      Urutannya tidak boleh dibalik. Jika mutex dikunci lebih dulu sebelum
      menunggu slot kosong, produsen bisa memegang mutex sambil tertidur
      menunggu slot &mdash; sementara konsumen yang dapat mengosongkan slot
      tidak bisa masuk karena mutex sedang dipegang. Keduanya saling menunggu
      selamanya: itu deadlock.
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
    const holder = Object.entries(snapshot).find(([, s]) => s.memegang.includes(i + 1));
    const used = Boolean(holder);
    out += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="11"
        fill="${used ? "#f0b429" : "#2b3542"}" stroke="#171d26" stroke-width="2"/>
      <text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="middle"
        font-size="11" font-weight="700" fill="${used ? "#07121d" : "#94a3b2"}">${i + 1}</text>`;
  }

  // Filsuf.
  for (let i = 0; i < N; i++) {
    const a = (i / N) * 2 * Math.PI - Math.PI / 2;
    const x = cx + rP * Math.cos(a), y = cy + rP * Math.sin(a);
    const st = snapshot[`F${i + 1}`] || { memegang: [], menunggu: null, sudah_makan: 0 };
    let fill = "#2b3542", label = "#94a3b2";
    if (st.menunggu) { fill = "#f4716a"; label = "#07121d"; }
    else if (st.memegang.length === 2) { fill = "#3ecf8e"; label = "#07121d"; }
    else if (st.memegang.length === 1) { fill = "#f0b429"; label = "#07121d"; }

    out += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="23"
        fill="${fill}" stroke="#171d26" stroke-width="2"/>
      <text x="${x.toFixed(1)}" y="${(y - 1).toFixed(1)}" text-anchor="middle"
        font-size="12" font-weight="700" fill="${label}">F${i + 1}</text>
      <text x="${x.toFixed(1)}" y="${(y + 11).toFixed(1)}" text-anchor="middle"
        font-size="9" fill="${label}">${st.sudah_makan}x</text>`;
  }

  return `<div class="graph-box">
    <svg viewBox="0 0 300 300" role="img" aria-label="Meja bundar lima filsuf">
      <circle cx="${cx}" cy="${cy}" r="40" fill="none" stroke="#2b3542" stroke-width="1" stroke-dasharray="3 3"/>
      <text x="${cx}" y="${cy + 4}" text-anchor="middle" font-size="11"
        fill="${deadlocked ? "#f4716a" : "#3ecf8e"}" font-weight="700">
        ${deadlocked ? "DEADLOCK" : "LANCAR"}
      </text>
      ${out}
    </svg>
  </div>`;
}

function philOne(r) {
  const rows = Object.entries(r.state_snapshot).map(([who, s]) => [
    esc(who),
    s.memegang.length ? s.memegang.join(", ") : "&mdash;",
    s.menunggu ? `<b style="color:var(--bad)">${s.menunggu}</b>` : "&mdash;",
    s.sudah_makan,
  ]);

  return `<div class="result ${r.deadlocked ? "bad" : "ok"}">
    <h4>${esc(r.strategy_label)}</h4>
    <div class="verdict ${r.deadlocked ? "bad" : "ok"}">${esc(r.conclusion)}</div>
    <div class="phil-grid">
      <div class="phil-table">${philSVG(r.state_snapshot, r.deadlocked)}</div>
      <div style="flex:1;min-width:260px">
        ${table(["Filsuf", "Memegang garpu", "Menunggu garpu", "Sudah makan"], rows, { numCols: [3] })}
        ${
          r.cycle && r.cycle.length
            ? `<p class="note" style="margin-top:12px">
                <b style="color:var(--bad)">Circular wait terdeteksi:</b>
                <span class="seq" style="color:var(--bad)">${esc(r.cycle.join(" &rarr; "))}</span><br>
                Setiap filsuf memegang satu garpu dan menunggu garpu yang
                dipegang tetangganya. Lingkaran tunggu ini adalah syarat
                keempat Coffman.
              </p>`
            : ""
        }
      </div>
    </div>
  </div>`;
}

function philHTML(d) {
  const sum = table(
    ["Strategi", "Deadlock", "Berhasil makan"],
    d.summary.map((s) => ({
      __class: s.deadlocked ? "" : "best",
      cells: [
        esc(s.label),
        s.deadlocked
          ? '<b style="color:var(--bad)">YA</b>'
          : '<b style="color:var(--ok)">tidak</b>',
        `${s.total_eaten} / ${s.target}`,
      ],
    })),
    { numCols: [2] }
  );

  return `<h4>Ringkasan</h4>
    ${sum}
    <p class="note" style="margin-top:12px">
      Keterangan warna: <b style="color:var(--ok)">hijau</b> = sedang makan
      (memegang 2 garpu), <b style="color:var(--warn)">kuning</b> = memegang
      1 garpu, <b style="color:var(--bad)">merah</b> = menunggu garpu,
      abu-abu = sedang berpikir atau sudah selesai.
    </p>
    ${d.results.map(philOne).join("")}
    <h4>Mengapa kedua solusi berhasil</h4>
    <p class="note">
      <b>Resource ordering</b> memutus <i>circular wait</i>. Karena semua filsuf
      wajib mengambil garpu bernomor kecil lebih dulu, mustahil terbentuk
      lingkaran tunggu: selalu ada satu filsuf yang permintaannya paling
      "belakang" dan karena itu bisa dipenuhi.
    </p>
    <p class="note">
      <b>Waiter / semaphore</b> memutus <i>hold and wait</i> secara efektif
      dengan membatasi hanya 4 filsuf yang boleh mencoba makan bersamaan.
      Dengan 4 orang berebut 5 garpu, selalu ada minimal satu orang yang bisa
      mendapat dua garpu, sehingga sistem tidak mungkin macet total.
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
