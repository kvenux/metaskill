/* MetaSkill Frontend App — with i18n (EN default) */
(function () {
  "use strict";

  const API = "api";
  let allSkills = [];
  let searchIndex = [];
  let categories = [];
  let currentView = "grid";
  let currentLang = localStorage.getItem("lang") || "en";

  /* ── i18n ── */
  const STRINGS = {
    en: {
      hero_eyebrow: "Open Source · Community Driven · Always Updated",
      hero_title_line2: "Skill Catalog",
      hero_sub: "900+ curated skills. Search, browse, install in seconds.",
      install_instruction: "Fetch the installation guide and follow it:",
      copy: "Copy",
      copied: "Copied!",
      stat_skills: "Skills",
      stat_categories: "Categories",
      stat_packs: "Packs",
      stat_tags: "Tags",
      search_placeholder: "Search skills, tags, descriptions…",
      filter_all_cats: "All Categories",
      filter_all_repos: "All Sources",
      section_skills: "Skill Library",
      section_packs: "Skill Packs",
      loading: "Loading…",
      empty: "No matching skills found",
      modal_summary: "Summary",
      modal_description: "Description",
      modal_category: "Category",
      modal_tags: "Tags",
      modal_source: "Source",
      modal_security: "Security",
      modal_files: "Files",
      modal_install: "Install Command",
      pack_skills_suffix: "skills",
    },
    zh: {
      hero_eyebrow: "开源 · 社区驱动 · 每日更新",
      hero_title_line2: "技能目录",
      hero_sub: "聚合 900+ 编程技能，一键搜索、浏览、安装",
      install_instruction: "获取安装指引并按步骤完成：",
      copy: "复制",
      copied: "已复制！",
      stat_skills: "技能总数",
      stat_categories: "分类",
      stat_packs: "技能包",
      stat_tags: "标签",
      search_placeholder: "搜索技能名称、标签、描述…",
      filter_all_cats: "全部分类",
      filter_all_repos: "全部来源",
      section_skills: "技能列表",
      section_packs: "推荐技能包",
      loading: "加载中…",
      empty: "没有找到匹配的技能",
      modal_summary: "摘要",
      modal_description: "描述",
      modal_category: "分类",
      modal_tags: "标签",
      modal_source: "来源",
      modal_security: "安全状态",
      modal_files: "文件",
      modal_install: "安装命令",
      pack_skills_suffix: "个技能",
    }
  };

  function t(key) {
    return (STRINGS[currentLang] || STRINGS.en)[key] || key;
  }

  function applyLang() {
    // Update data-i18n text nodes
    document.querySelectorAll("[data-i18n]").forEach(el => {
      el.textContent = t(el.dataset.i18n);
    });
    // Update placeholders
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });
    // Update lang button active state
    document.querySelectorAll(".lang-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.lang === currentLang);
    });
    // Update html lang
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
    // Re-render category/repo filter first options
    const catFirst = document.querySelector("#categoryFilter option[value='']");
    if (catFirst) catFirst.textContent = t("filter_all_cats");
    const repoFirst = document.querySelector("#repoFilter option[value='']");
    if (repoFirst) repoFirst.textContent = t("filter_all_repos");
  }

  window.setLang = function (lang) {
    currentLang = lang;
    localStorage.setItem("lang", lang);
    applyLang();
    // Re-render pack count text
    renderPacks(window._packs || []);
  };

  /* ── Theme ── */
  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
      document.documentElement.setAttribute("data-theme", "light");
    }
  }

  window.toggleTheme = function () {
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    document.documentElement.setAttribute("data-theme", isLight ? "" : "light");
    localStorage.setItem("theme", isLight ? "dark" : "light");
  };

  /* ── Fetch ── */
  async function fetchJSON(path) {
    const resp = await fetch(`${API}/${path}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  /* ── Render skills ── */
  function renderSkillCard(skill) {
    const tags = (skill.tags || []).slice(0, 2).map(tag =>
      `<span class="tag">${esc(tag)}</span>`
    ).join("");
    const status = skill.security_status || "clean";
    const statusClass = status === "clean" ? "clean" : status === "warning" ? "warning" : "blocked";
    return `<div class="skill-card" onclick="showSkill('${esc(skill.id)}')" tabindex="0" role="button" aria-label="${esc(skill.name || skill.id)}">
      <div class="skill-card-header">
        <span class="skill-name">${esc(skill.name || skill.id)}</span>
        <span class="skill-status ${statusClass}" title="${esc(status)}"></span>
      </div>
      <div class="skill-summary">${esc(skill.summary || "")}</div>
      <div class="skill-meta">
        ${skill.category_id ? `<span class="cat-badge">${esc(skill.category_id)}</span>` : ""}
        ${tags}
      </div>
    </div>`;
  }

  function renderSkills(skills) {
    const grid = document.getElementById("skillGrid");
    const empty = document.getElementById("empty");
    const count = document.getElementById("skillCount");
    count.textContent = `(${skills.length})`;
    if (skills.length === 0) {
      grid.innerHTML = "";
      empty.style.display = "flex";
    } else {
      empty.style.display = "none";
      // Stagger animation via style
      grid.innerHTML = skills.map((s, i) =>
        renderSkillCard(s).replace('class="skill-card"', `class="skill-card" style="animation-delay:${Math.min(i * 20, 300)}ms"`)
      ).join("");
    }
  }

  function renderPacks(packs) {
    window._packs = packs;
    const grid = document.getElementById("packGrid");
    grid.innerHTML = packs.map(p => `<div class="pack-card">
      <div class="pack-name">${esc(p.name)}</div>
      <div class="pack-desc">${esc(p.description)}</div>
      <div class="pack-count">${p.skill_count || 0} ${t("pack_skills_suffix")}</div>
    </div>`).join("");
  }

  function renderStats(stats) {
    document.getElementById("hs-skills").textContent = stats.total_skills || 0;
    document.getElementById("hs-cats").textContent = stats.total_categories || 0;
    document.getElementById("hs-packs").textContent = stats.total_packs || 0;
    document.getElementById("hs-tags").textContent = stats.total_tags || 0;
  }

  function populateFilters() {
    const catSel = document.getElementById("categoryFilter");
    categories.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.skill_count || 0})`;
      catSel.appendChild(opt);
    });
    const repos = [...new Set(allSkills.map(s => s.source_repo).filter(Boolean))];
    const repoSel = document.getElementById("repoFilter");
    repos.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      repoSel.appendChild(opt);
    });
  }

  /* ── Filter & Search ── */
  function applyFilters() {
    const q = document.getElementById("searchInput").value.toLowerCase().trim();
    const cat = document.getElementById("categoryFilter").value;
    const repo = document.getElementById("repoFilter").value;
    const clearBtn = document.getElementById("searchClear");
    clearBtn.classList.toggle("visible", q.length > 0);

    let filtered = allSkills;
    if (cat) filtered = filtered.filter(s => s.category_id === cat);
    if (repo) filtered = filtered.filter(s => s.source_repo === repo);
    if (q) {
      const matchIds = new Set(searchIndex.filter(s => s.text && s.text.includes(q)).map(s => s.id));
      filtered = filtered.filter(s => matchIds.has(s.id));
    }
    renderSkills(filtered);
  }

  window.clearSearch = function () {
    document.getElementById("searchInput").value = "";
    applyFilters();
  };

  /* ── View toggle ── */
  window.setView = function (view) {
    currentView = view;
    const grid = document.getElementById("skillGrid");
    grid.classList.toggle("list-view", view === "list");
    document.getElementById("viewGrid").classList.toggle("active", view === "grid");
    document.getElementById("viewList").classList.toggle("active", view === "list");
  };

  /* ── Modal ── */
  window.showSkill = async function (id) {
    const modal = document.getElementById("modal");
    const content = document.getElementById("modalContent");
    content.innerHTML = `<div class="loading-state" style="padding:40px 0"><div class="loading-spinner"></div></div>`;
    modal.classList.add("active");
    try {
      const skill = await fetchJSON(`skills/${id}/index.json`);
      const tags = (skill.tags || []).map(tag => `<span class="tag">${esc(tag)}</span>`).join(" ");
      const files = (skill.file_list || []).map(f => `<li style="font-family:var(--font-mono);font-size:0.8rem;color:var(--text-muted)">${esc(f)}</li>`).join("");
      const installCmd = `python codeskill_cli.py install ${esc(skill.id)}`;
      const status = skill.security_status || "clean";
      const statusColor = status === "clean" ? "var(--green)" : status === "warning" ? "var(--orange)" : "var(--red)";
      content.innerHTML = `
        <h2 class="modal-title">${esc(skill.name)}</h2>
        <div class="detail-row">
          <span class="detail-label">${t("modal_summary")}</span>
          <div class="detail-value">${esc(skill.summary)}</div>
        </div>
        ${skill.description ? `<div class="detail-row">
          <span class="detail-label">${t("modal_description")}</span>
          <div class="detail-value">${esc(String(skill.description).substring(0, 400))}</div>
        </div>` : ""}
        <div class="detail-row">
          <span class="detail-label">${t("modal_category")}</span>
          <div class="detail-value"><span class="cat-badge">${esc(skill.category_id || "—")}</span></div>
        </div>
        ${tags ? `<div class="detail-row">
          <span class="detail-label">${t("modal_tags")}</span>
          <div class="detail-value" style="display:flex;gap:4px;flex-wrap:wrap">${tags}</div>
        </div>` : ""}
        <div class="detail-row">
          <span class="detail-label">${t("modal_source")}</span>
          <div class="detail-value"><a href="${esc(skill.source && skill.source.repo_url || "#")}" target="_blank" rel="noopener">${esc(skill.source && skill.source.repo || "—")}</a></div>
        </div>
        <div class="detail-row">
          <span class="detail-label">${t("modal_security")}</span>
          <div class="detail-value" style="color:${statusColor};font-family:var(--font-mono);font-size:0.82rem">${esc(status)}</div>
        </div>
        ${files ? `<div class="detail-row">
          <span class="detail-label">${t("modal_files")}</span>
          <ul style="padding-left:16px">${files}</ul>
        </div>` : ""}
        <div class="modal-install">
          <code>${installCmd}</code>
          <button class="copy-btn" onclick="copyText('${installCmd}', this)">${t("copy")}</button>
        </div>
      `;
    } catch (e) {
      content.innerHTML = `<p style="color:var(--text-muted);font-size:0.9rem">Failed to load: ${esc(e.message)}</p>`;
    }
  };

  window.closeModal = function () {
    document.getElementById("modal").classList.remove("active");
  };

  /* ── Tab switching ── */
  window.selectTool = function (tool) {
    document.querySelectorAll(".tool-tab").forEach(b => {
      const on = b.dataset.tool === tool;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", on);
    });
    document.querySelectorAll(".tool-panel").forEach(p => {
      p.classList.toggle("active", p.id === "tp-" + tool);
    });
  };

  window.selectMethod = function (btn, panelId) {
    const tablist = btn.closest(".method-tablist");
    tablist.querySelectorAll(".method-tab").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const panel = btn.closest(".tool-panel");
    panel.querySelectorAll(".cmd-panel").forEach(p => p.classList.remove("active"));
    document.getElementById(panelId).classList.add("active");
  };

  /* ── Clipboard ── */
  window.copyCmd = function (btn) {
    const instruction = t("install_instruction");
    const cmd = btn.dataset.cmd;
    const full = instruction + "\n" + cmd;
    copyText(full, btn);
  };

  window.copyInstall = function () {
    const btn = document.querySelector(".copy-btn");
    if (btn) copyCmd(btn);
  };

  window.copyText = function (text, btn) {
    navigator.clipboard.writeText(text).then(() => {
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = t("copied");
        btn.classList.add("copied");
        setTimeout(() => { btn.textContent = orig; btn.classList.remove("copied"); }, 2000);
      }
    }).catch(() => {});
  };

  /* ── Escape HTML ── */
  function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  /* ── Init ── */
  async function init() {
    initTheme();
    // Apply saved language
    applyLang();

    const loading = document.getElementById("loading");
    try {
      const [skillsData, searchData, catData, packsData, statsData] = await Promise.all([
        fetchJSON("skills/index.json"),
        fetchJSON("search/index.json"),
        fetchJSON("categories/index.json"),
        fetchJSON("packs/index.json"),
        fetchJSON("stats/index.json"),
      ]);
      allSkills = skillsData.items || [];
      searchIndex = searchData.items || [];
      categories = catData.items || [];
      loading.style.display = "none";
      populateFilters();
      renderSkills(allSkills);
      renderPacks(packsData.items || []);
      renderStats(statsData);
    } catch (e) {
      loading.innerHTML = `<div class="empty-icon">⚠</div><span>Failed to load data. Run the aggregator first.</span>`;
    }

    document.getElementById("searchInput").addEventListener("input", applyFilters);
    document.getElementById("categoryFilter").addEventListener("change", applyFilters);
    document.getElementById("repoFilter").addEventListener("change", applyFilters);
    document.getElementById("modal").addEventListener("click", function (e) {
      if (e.target === this) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeModal();
    });
  }

  init();
})();
