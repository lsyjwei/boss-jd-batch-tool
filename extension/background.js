chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "badge") {
    const n = msg.count || 0;
    chrome.action.setBadgeText({ text: n > 0 ? String(n) : "" });
    chrome.action.setBadgeBackgroundColor({ color: "#00bebd" });
  }
});
