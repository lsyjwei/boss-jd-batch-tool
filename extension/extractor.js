/**
 * Extract BOSS job detail from current page (logged-in browser context).
 */
(function (global) {
  const FIELD_RE = /(job_name|job_salary|company|job_id)\s*:\s*['"]([^'"]*)['"]/g;

  function parseJobInfoFromScripts() {
    const info = {};
    for (const script of document.querySelectorAll("script")) {
      const text = script.textContent || "";
      if (!text.includes("_jobInfo")) continue;
      const block = text.match(/var\s+_jobInfo\s*=\s*\{([^}]+)\}/);
      if (!block) continue;
      let m;
      const re = new RegExp(FIELD_RE.source, "g");
      while ((m = re.exec(block[1])) !== null) {
        info[m[1]] = m[2];
      }
      if (info.job_name) break;
    }
    return info;
  }

  function textFrom(el) {
    return el ? el.textContent.trim() : "";
  }

  function extractJdBody() {
    for (const section of document.querySelectorAll(".job-detail-section")) {
      if (
        section.querySelector(".job-detail-company, .more-job-section, .security-box")
      ) {
        continue;
      }
      const el = section.querySelector(".job-sec-text");
      if (!el) continue;
      const clone = el.cloneNode(true);
      clone.querySelectorAll("br").forEach((br) => br.replaceWith("\n"));
      const t = clone.textContent.replace(/\n{3,}/g, "\n\n").trim();
      if (t.includes("职位描述") || t.length > 80) return t;
    }
    return "";
  }

  function extractJobFromPage() {
    const info = parseJobInfoFromScripts();
    const title =
      info.job_name ||
      textFrom(document.querySelector(".name h1")) ||
      document.querySelector(".name h1")?.getAttribute("title") ||
      "";
    const salary =
      info.job_salary || textFrom(document.querySelector(".name .salary, span.salary"));
    const company =
      info.company ||
      document.querySelector(".sider-company a[title]")?.getAttribute("title") ||
      textFrom(document.querySelector(".detail-op .info")).split("\n")[0] ||
      "";
    const location = textFrom(document.querySelector(".text-city"));
    const experience = textFrom(
      document.querySelector(".text-experiece, .text-experience")
    );
    const degree = textFrom(document.querySelector(".text-degree"));
    const canonical = document.querySelector('link[rel="canonical"]')?.href || "";
    const source_url = canonical || location.href.split("?")[0];

    if (!title) {
      throw new Error("未识别到岗位页，请打开 BOSS 职位详情页");
    }

    return {
      job_id: info.job_id || "",
      title,
      company,
      salary,
      jd_body: extractJdBody(),
      source_url,
      location,
      experience,
      degree,
      collected_at: new Date().toISOString(),
    };
  }

  function jobKey(job) {
    return job.job_id || job.source_url || `${job.title}|${job.company}`;
  }

  global.BossJdExtractor = { extractJobFromPage, jobKey };
})(typeof window !== "undefined" ? window : globalThis);
