const COLLECTION_KEY = "bossJdCollection";

async function getCollection() {
  const data = await chrome.storage.local.get(COLLECTION_KEY);
  return data[COLLECTION_KEY] || [];
}

async function setCollection(jobs) {
  await chrome.storage.local.set({ [COLLECTION_KEY]: jobs });
}

async function addCurrentJob() {
  const job = BossJdExtractor.extractJobFromPage();
  const jobs = await getCollection();
  const key = BossJdExtractor.jobKey(job);
  if (jobs.some((j) => BossJdExtractor.jobKey(j) === key)) {
    showToast("已在收集列表中");
    return jobs.length;
  }
  jobs.push(job);
  await setCollection(jobs);
  updateBadge(jobs.length);
  showToast(`已收集 (${jobs.length})`);
  return jobs.length;
}

function updateBadge(count) {
  try {
    chrome.runtime.sendMessage({ type: "badge", count });
  } catch (_) {
    /* popup/background may be unavailable */
  }
}

function showToast(msg) {
  let el = document.getElementById("boss-jd-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "boss-jd-toast";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = "boss-jd-toast show";
  setTimeout(() => el.classList.remove("show"), 2000);
}

function injectCollectButton() {
  if (document.getElementById("boss-jd-collect-btn")) return;
  const btn = document.createElement("button");
  btn.id = "boss-jd-collect-btn";
  btn.type = "button";
  btn.textContent = "＋ 收集 JD";
  btn.title = "加入收集列表，稍后在扩展弹窗批量导出";
  btn.addEventListener("click", () => addCurrentJob().catch((e) => showToast(e.message)));
  document.body.appendChild(btn);
}

function isJobDetailPage() {
  return /zhipin\.com\/job_detail\//.test(location.href);
}

if (isJobDetailPage()) {
  injectCollectButton();
  getCollection().then((jobs) => updateBadge(jobs.length));
}
