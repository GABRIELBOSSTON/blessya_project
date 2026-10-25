/* ===================================================================
   Pengatur tab dan penyalaan awal semua panel.
   =================================================================== */

function initTabs() {
  const tabs = $$(".tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      $$(".panel").forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      const panel = document.getElementById(tab.dataset.panel);
      if (panel) panel.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initScheduling();
  initIPC();
  initDeadlock();

  // Jalankan panel penjadwalan sekali di awal, supaya halaman tidak
  // tampak kosong saat pertama dibuka dan pengguna langsung melihat
  // contoh hasil tanpa perlu menekan apa pun.
  const btn = $("#run-sched");
  if (btn) btn.click();
});
