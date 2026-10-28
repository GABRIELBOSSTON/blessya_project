/* ===================================================================
   Helper functions shared by all panels.
   =================================================================== */

/** Send a request to the Python API and return the result as an object. */
async function api(path, payload) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
  const data = await res.json().catch(() => ({ error: "Server response is not JSON" }));
  if (!res.ok || data.error) {
    throw new Error(data.error || `Server responded with status ${res.status}`);
  }
  return data;
}

/** Escape text so it is safe to insert into HTML. */
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

const $ = (sel, root) => (root || document).querySelector(sel);
const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

/** Show an error message in the given element. */
function showErr(id, msg) {
  const el = $(id);
  if (!el) return;
  el.textContent = msg;
  el.hidden = false;
}
function clearErr(id) {
  const el = $(id);
  if (el) el.hidden = true;
}

/**
 * Wrap an API call: manage the disabled button, the "processing" message,
 * and error handling, so it is not repeated in every panel.
 */
async function withBusy(btn, outSel, errSel, fn) {
  const out = $(outSel);
  clearErr(errSel);
  btn.disabled = true;
  const label = btn.textContent;
  btn.textContent = "Processing...";
  if (out) out.innerHTML = '<p class="loading">Running simulation in Python...</p>';
  try {
    await fn();
  } catch (e) {
    if (out) out.innerHTML = "";
    showErr(errSel, e.message || String(e));
  } finally {
    btn.disabled = false;
    btn.textContent = label;
  }
}

/** Fixed color per process, so it stays consistent across Gantt charts. */
const PALETTE = [
  "#bfdbfe", "#bbf7d0", "#fde68a", "#ddd6fe", "#fecdd3",
  "#a5f3fc", "#fed7aa", "#d9f99d", "#f5d0fe", "#bae6fd",
  "#a7f3d0", "#fef08a",
];
const _colorMap = new Map();
function colorFor(pid) {
  if (pid === "IDLE") return "#f4f4f5";
  if (!_colorMap.has(pid)) _colorMap.set(pid, PALETTE[_colorMap.size % PALETTE.length]);
  return _colorMap.get(pid);
}

/** One summary number box. */
function chip(label, value, tone) {
  return `<div class="chip ${tone || ""}">
    <span class="k">${esc(label)}</span>
    <span class="v">${esc(value)}</span>
  </div>`;
}

/** Collapsible log block. */
function logBlock(lines, title) {
  if (!lines || !lines.length) return "";
  return `<details class="log">
    <summary>${esc(title || "View computation steps")} (${lines.length} lines)</summary>
    <pre class="log-body">${esc(lines.join("\n"))}</pre>
  </details>`;
}

/** Simple table built from a list of rows. */
function table(headers, rows, opts) {
  const o = opts || {};
  const head = headers
    .map((h, i) => `<th class="${o.numCols && o.numCols.includes(i) ? "num" : ""}">${esc(h)}</th>`)
    .join("");
  const body = rows
    .map((r) => {
      const cls = r.__class ? ` class="${r.__class}"` : "";
      const cells = (r.cells || r)
        .map((c, i) => `<td class="${o.numCols && o.numCols.includes(i) ? "num" : ""}">${c}</td>`)
        .join("");
      return `<tr${cls}>${cells}</tr>`;
    })
    .join("");
  return `<div class="table-scroll"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
