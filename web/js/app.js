/* ===================================================================
   Tab controller and initial startup of all panels.
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

  // Run the scheduling panel once at startup so the page does not look
  // empty when first opened and the user immediately sees a sample
  // result without pressing anything.
  const btn = $("#run-sched");
  if (btn) btn.click();
});
