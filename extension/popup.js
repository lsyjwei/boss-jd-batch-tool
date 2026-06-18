const COLLECTION_KEY = "bossJdCollection";

async function getCollection() {
  const data = await chrome.storage.local.get(COLLECTION_KEY);
  return data[COLLECTION_KEY] || [];
}

async function setCollection(jobs) {
  await chrome.storage.local.set({ [COLLECTION_KEY]: jobs });
  chrome.runtime.sendMessage({ type: "badge", count: jobs.length });
}

function renderList(jobs) {
  const list = document.getElementById("list");
  const count = document.getElementById("count");
  count.textContent = jobs.length;

  if (!jobs.length) {
    list.innerHTML = '<li class="empty">暂无收集<br/>打开 BOSS 岗位页点击「＋ 收集 JD」</li>';
    return;
  }

  list.innerHTML = jobs
    .map(
      (job, i) => `
    <li data-index="${i}">
      <div class="job-info">
        <div class="job-title" title="${escapeHtml(job.title)}">${escapeHtml(job.title)}</div>
        <div class="job-meta">${escapeHtml(job.company || "—")} · ${escapeHtml(job.salary || "—")}</div>
      </div>
      <button class="remove" title="移除">×</button>
    </li>`
    )
    .join("");

  list.querySelectorAll(".remove").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const idx = Number(e.target.closest("li").dataset.index);
      const next = await getCollection();
      next.splice(idx, 1);
      await setCollection(next);
      renderList(next);
    });
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatExportFilename() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `boss-jd-batch-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}.json`;
}

async function exportBatch() {
  const jobs = await getCollection();
  if (!jobs.length) {
    document.getElementById("status").textContent = "列表为空，请先收集岗位";
    return;
  }

  const payload = {
    exported_at: new Date().toISOString(),
    source: "boss-jd-extension",
    count: jobs.length,
    jobs,
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const filename = formatExportFilename();

  await chrome.downloads.download({
    url,
    filename,
    saveAs: true,
  });

  document.getElementById("status").textContent =
    `已导出 ${jobs.length} 条 → 请保存到项目的 input/inbox/，然后运行 import-all`;

  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

document.getElementById("export").addEventListener("click", exportBatch);
document.getElementById("clear").addEventListener("click", async () => {
  if (!confirm("确定清空收集列表？")) return;
  await setCollection([]);
  renderList([]);
  document.getElementById("status").textContent = "已清空";
});

getCollection().then(renderList);
