/* MetaSkill Frontend App — v2 with ratings, roles, enhanced search, full-screen modal */
(function () {
  "use strict";

  const API = "api";
  let allSkills = [];
  let searchIndex = [];
  let categories = [];
  let rankings = [];
  let synonyms = {};
  let currentView = "grid";
  let currentLang = localStorage.getItem("lang") || "en";
  let currentSort = "recommended";
  let currentCategory = "";
  let currentRole = "all";
  let activeGrades = new Set();

  /* ── Role → category/tag mapping ── */
  const ROLE_MAP = {
    all: { categories: [], tags: [] },
    frontend: { categories: ["frontend", "design"], tags: ["react", "vue", "css", "html", "ui"] },
    backend: { categories: ["backend", "data"], tags: ["api", "server", "database", "rest"] },
    fullstack: { categories: ["development", "frontend", "backend", "testing"], tags: ["fullstack", "dev"] },
    devops: { categories: ["devops", "cloud", "security"], tags: ["docker", "ci-cd", "deploy", "k8s"] },
    "data-ai": { categories: ["data", "ai-ml"], tags: ["ml", "ai", "analytics", "llm", "agent"] },
    writer: { categories: ["writing", "documentation"], tags: ["article", "doc", "blog", "translate"] },
    designer: { categories: ["design", "media"], tags: ["ui", "ux", "brand", "art", "image"] },
    mobile: { categories: ["mobile", "frontend"], tags: ["ios", "android", "react-native", "flutter"] },
  };

  /* ── i18n ── */
  const STRINGS = {
    en: {
      hero_eyebrow: "Open Source · Community Driven · Always Updated",
      hero_title_line2: "Skill Catalog",
      hero_sub: "900+ curated skills. Search, browse, install in seconds.",
      install_instruction: "Fetch the installation guide and follow it:",
      copy: "Copy", copied: "Copied!",
      stat_skills: "Skills", stat_categories: "Categories", stat_packs: "Packs", stat_tags: "Tags",
      search_placeholder: "Search skills, tags, descriptions…",
      filter_all: "All", filter_all_repos: "All Sources",
      sort_label: "Sort:", sort_recommended: "Recommended", sort_rating: "Rating ↓", sort_newest: "Newest",
      rating_label: "Rating:",
      section_skills: "Skill Library", section_packs: "Skill Packs",
      section_rankings: "Must-Have Skills", section_faq: "FAQ",
      loading: "Loading…", empty: "No matching skills found",
      pack_skills_suffix: "skills", search_results: "results",
      role_label: "I am a...", role_all: "All", role_frontend: "Frontend", role_backend: "Backend",
      role_fullstack: "Full Stack", role_devops: "DevOps", role_data_ai: "Data/AI",
      role_writer: "Tech Writer", role_designer: "Designer", role_mobile: "Mobile",
      modal_summary: "Summary", modal_description: "Description", modal_category: "Category",
      modal_tags: "Tags", modal_source: "Source", modal_security: "Security",
      modal_files: "Files", modal_install: "Install Command",
      modal_flow: "Logic Flow", modal_preview: "Output Preview", modal_audience: "Target Audience",
      modal_rating: "AI Score", modal_dimensions: "Rating Dimensions",
      modal_works_with: "Works With", modal_file_browser: "File Browser",
      modal_tab_skill: "SKILL.md", modal_tab_rating: "Rating Details",
      modal_fullscreen: "Fullscreen", modal_copy_preview: "Copy",
      dim_practicality: "Practicality", dim_clarity: "Clarity", dim_automation: "Automation",
      dim_quality: "Quality", dim_impact: "Impact",
      faq_q1: "What is a Skill?", faq_a1: "A Skill is a set of instructions and scripts that enhance your AI coding assistant (Claude Code, OpenCode, Codex) with specialized capabilities — like generating documents, running tests, or publishing to social media.",
      faq_q2: "How to install a Skill?", faq_a2: "Use the one-line install command at the top of this page to install the MetaSkill browser. Then use it to search and install individual skills with a single command.",
      faq_q3: "Which AI agents are supported?", faq_a3: "Currently supports Claude Code (~/.claude/skills/), OpenCode (~/.config/opencode/skills/), and Codex CLI (~/.codex/skills/). More agents coming soon.",
      faq_q4: "How to submit your own Skill?", faq_a4: "Create a SKILL.md file following the standard format, push it to a GitHub repo, and submit a PR to one of our source repositories. The aggregator will pick it up automatically.",
      faq_q5: "What do ratings mean?", faq_a5: "Each skill is rated by AI across 5 dimensions: Practicality, Clarity, Automation, Quality, and Impact. Grades range from S (exceptional, ≥9.0) to D (below 6.0).",
    },
    zh: {
      hero_eyebrow: "开源 · 社区驱动 · 每日更新",
      hero_title_line2: "技能目录",
      hero_sub: "聚合 900+ 编程技能，一键搜索、浏览、安装",
      install_instruction: "获取安装指引并按步骤完成：",
      copy: "复制", copied: "已复制！",
      stat_skills: "技能总数", stat_categories: "分类", stat_packs: "技能包", stat_tags: "标签",
      search_placeholder: "搜索技能名称、标签、描述…",
      filter_all: "全部", filter_all_repos: "全部来源",
      sort_label: "排序：", sort_recommended: "推荐", sort_rating: "评分 ↓", sort_newest: "最新",
      rating_label: "评分：",
      section_skills: "技能列表", section_packs: "推荐技能包",
      section_rankings: "必装神器", section_faq: "常见问题",
      loading: "加载中…", empty: "没有找到匹配的技能",
      pack_skills_suffix: "个技能", search_results: "个结果",
      role_label: "我是...", role_all: "全部", role_frontend: "前端开发", role_backend: "后端开发",
      role_fullstack: "全栈开发", role_devops: "DevOps", role_data_ai: "数据/AI",
      role_writer: "技术写作", role_designer: "设计师", role_mobile: "移动端",
      modal_summary: "摘要", modal_description: "描述", modal_category: "分类",
      modal_tags: "标签", modal_source: "来源", modal_security: "安全状态",
      modal_files: "文件", modal_install: "安装命令",
      modal_flow: "逻辑流程", modal_preview: "输出预览", modal_audience: "适合人群",
      modal_rating: "AI 评分", modal_dimensions: "评分维度",
      modal_works_with: "兼容 Agent", modal_file_browser: "文件浏览",
      modal_tab_skill: "SKILL.md", modal_tab_rating: "测评详情",
      modal_fullscreen: "全屏", modal_copy_preview: "复制",
      dim_practicality: "实用性", dim_clarity: "指令清晰度", dim_automation: "自动化程度",
      dim_quality: "输出质量", dim_impact: "影响力",
      faq_q1: "什么是 Skill？", faq_a1: "Skill 是一组指令和脚本，能增强你的 AI 编程助手（Claude Code、OpenCode、Codex）的专项能力——比如生成文档、运行测试、发布到社交媒体等。",
      faq_q2: "如何安装 Skill？", faq_a2: "使用页面顶部的一行安装命令安装 MetaSkill 浏览器，然后用它搜索和安装各种技能。",
      faq_q3: "支持哪些 AI Agent？", faq_a3: "目前支持 Claude Code (~/.claude/skills/)、OpenCode (~/.config/opencode/skills/) 和 Codex CLI (~/.codex/skills/)，更多 Agent 即将支持。",
      faq_q4: "如何提交自己的 Skill？", faq_a4: "按标准格式创建 SKILL.md 文件，推送到 GitHub 仓库，然后向我们的源仓库提交 PR。聚合器会自动收录。",
      faq_q5: "评分是什么意思？", faq_a5: "每个技能由 AI 从 5 个维度评分：实用性、清晰度、自动化、质量和影响力。等级从 S（卓越，≥9.0）到 D（低于 6.0）。",
    }
  };

  function t(key) { return (STRINGS[currentLang] || STRINGS.en)[key] || key; }

  function applyLang() {
    document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
    document.querySelectorAll(".lang-btn").forEach(btn => { btn.classList.toggle("active", btn.dataset.lang === currentLang); });
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
    const repoFirst = document.querySelector("#repoFilter option[value='']");
    if (repoFirst) repoFirst.textContent = t("filter_all_repos");
    renderFAQ();
  }

  window.setLang = function (lang) {
    currentLang = lang;
    localStorage.setItem("lang", lang);
    applyLang();
    renderPacks(window._packs || []);
    renderRankings();
  };

  /* ── Theme ── */
  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "light") document.documentElement.setAttribute("data-theme", "light");
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

  /* ── Escape HTML ── */
  function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  /* ── Grade helpers ── */
  function gradeColor(grade) {
    const map = { S: "#f0b429", A: "#2dd4a7", B: "#60a5fa", C: "#6b6b8a", D: "#3d3d55" };
    return map[grade] || map.C;
  }
  function gradeBg(grade) {
    const map = { S: "rgba(240,180,41,0.15)", A: "rgba(45,212,167,0.15)", B: "rgba(96,165,250,0.15)", C: "rgba(107,107,138,0.1)", D: "rgba(61,61,85,0.1)" };
    return map[grade] || map.C;
  }

  /* ── Search: fuzzy match (Levenshtein ≤ 1) ── */
  function levenshtein1(a, b) {
    if (Math.abs(a.length - b.length) > 1) return false;
    let diff = 0;
    for (let i = 0, j = 0; i < a.length || j < b.length;) {
      if (a[i] !== b[j]) {
        diff++;
        if (diff > 1) return false;
        if (a.length > b.length) i++;
        else if (a.length < b.length) j++;
        else { i++; j++; }
      } else { i++; j++; }
    }
    return true;
  }

  function expandSynonyms(query) {
    const terms = [query];
    for (const [key, vals] of Object.entries(synonyms)) {
      if (query === key || vals.includes(query)) {
        terms.push(key, ...vals);
      }
    }
    return [...new Set(terms)];
  }

  function highlightText(text, query) {
    if (!query) return esc(text);
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`(${escaped})`, "gi");
    return esc(text).replace(re, '<mark class="search-highlight">$1</mark>');
  }

  function scoreMatch(text, query) {
    const t = text.toLowerCase();
    const q = query.toLowerCase();
    if (t === q) return 100;
    if (t.startsWith(q)) return 80;
    if (t.includes(q)) return 60;
    // fuzzy: check words
    const words = t.split(/[\s\-_]+/);
    for (const w of words) {
      if (levenshtein1(w, q)) return 30;
    }
    return 0;
  }
/* RENDER_PLACEHOLDER */

  /* ── Render skill card (enhanced) ── */
  function renderSkillCard(skill, query) {
    const tags = (skill.tags || []).slice(0, 4).map(tag =>
      `<span class="tag">${query ? highlightText(tag, query) : esc(tag)}</span>`
    ).join("");
    const grade = skill.rating_grade || "D";
    const rating = skill.rating || 0;
    const repo = skill.source_repo || "";
    const repoShort = repo.replace(/-skills?$/, "").substring(0, 12);
    const name = query ? highlightText(skill.name || skill.id, query) : esc(skill.name || skill.id);
    const summary = query ? highlightText(skill.summary || "", query) : esc(skill.summary || "");
    const catId = skill.category_id || "";
    const catObj = categories.find(c => c.id === catId);
    const catLabel = catObj ? (currentLang === "zh" ? catObj.name : (catObj.name_en || catObj.name)) : catId;

    return `<div class="skill-card" onclick="showSkill('${esc(skill.id)}')" tabindex="0" role="button" aria-label="${esc(skill.name || skill.id)}">
      <div class="skill-card-header">
        <div class="skill-repo"><span class="repo-avatar">${esc(repoShort[0] || "?").toUpperCase()}</span> @${esc(repoShort)}</div>
        <div class="skill-grade" style="background:${gradeBg(grade)};color:${gradeColor(grade)}">${grade} <span class="grade-score">${rating}</span></div>
      </div>
      <div class="skill-card-title">
        <span class="skill-name">${name}</span>
      </div>
      <div class="skill-summary">${summary}</div>
      <div class="skill-tags">${tags}</div>
      <div class="skill-card-footer">
        <button class="try-btn" onclick="event.stopPropagation();showSkill('${esc(skill.id)}')">Try</button>
        <span class="cat-badge">${esc(catLabel)}</span>
      </div>
    </div>`;
  }

  function renderSkills(skills, query) {
    const grid = document.getElementById("skillGrid");
    const empty = document.getElementById("empty");
    const count = document.getElementById("skillCount");
    count.textContent = `(${skills.length})`;
    if (skills.length === 0) {
      grid.innerHTML = "";
      empty.style.display = "flex";
    } else {
      empty.style.display = "none";
      grid.innerHTML = skills.map((s, i) =>
        renderSkillCard(s, query).replace('class="skill-card"', `class="skill-card" style="animation-delay:${Math.min(i * 20, 300)}ms"`)
      ).join("");
    }
  }

  function renderPacks(packs) {
    window._packs = packs;
    const grid = document.getElementById("packGrid");
    grid.innerHTML = packs.map(p => {
      const featured = p.featured ? `<span class="pack-featured">Featured</span>` : "";
      return `<div class="pack-card${p.featured ? " pack-featured-card" : ""}">
        <div class="pack-header">
          <span class="pack-emoji">${p.emoji || "📦"}</span>
          ${featured}
        </div>
        <div class="pack-name">${esc(p.name)}</div>
        <div class="pack-desc">${esc(p.description)}</div>
        <div class="pack-count">${p.skill_count || 0} ${t("pack_skills_suffix")}</div>
      </div>`;
    }).join("");
  }

  function renderStats(stats) {
    document.getElementById("hs-skills").textContent = stats.total_skills || 0;
    document.getElementById("hs-cats").textContent = stats.total_categories || 0;
    document.getElementById("hs-packs").textContent = stats.total_packs || 0;
    document.getElementById("hs-tags").textContent = stats.total_tags || 0;
  }

  function renderRankings() {
    const grid = document.getElementById("rankingsGrid");
    const top12 = rankings.slice(0, 12);
    if (!top12.length) { document.getElementById("rankingsSection").style.display = "none"; return; }
    document.getElementById("rankingsSection").style.display = "";
    grid.innerHTML = top12.map(s => {
      const grade = s.rating_grade || "D";
      const name = esc(s.name || s.id);
      return `<div class="ranking-card" onclick="showSkill('${esc(s.id)}')">
        <div class="ranking-grade" style="background:${gradeBg(grade)};color:${gradeColor(grade)}">${grade}</div>
        <div class="ranking-info">
          <div class="ranking-name">${name}</div>
          <div class="ranking-summary">${esc(s.summary || "").substring(0, 60)}</div>
        </div>
        <div class="ranking-score">${s.rating || 0}</div>
      </div>`;
    }).join("");
  }

  function renderFAQ() {
    const list = document.getElementById("faqList");
    if (!list) return;
    const faqs = [1, 2, 3, 4, 5].map(i => ({ q: t(`faq_q${i}`), a: t(`faq_a${i}`) }));
    list.innerHTML = faqs.map((f, i) => `<div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)" aria-expanded="false">
        <span>${esc(f.q)}</span>
        <svg class="faq-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
      </button>
      <div class="faq-a"><p>${esc(f.a)}</p></div>
    </div>`).join("");
  }
  window.toggleFaq = function (btn) {
    const item = btn.closest(".faq-item");
    const open = item.classList.toggle("open");
    btn.setAttribute("aria-expanded", open);
  };

  /* ── Category pills ── */
  function renderCategoryPills() {
    const container = document.getElementById("categoryPills");
    const allBtn = container.querySelector(".pill");
    let html = "";
    categories.forEach(c => {
      const label = currentLang === "zh" ? c.name : (c.name_en || c.name);
      html += `<button class="pill" data-cat="${esc(c.id)}" onclick="selectCategory('${esc(c.id)}')">${esc(label)}</button>`;
    });
    allBtn.insertAdjacentHTML("afterend", html);
  }
  window.selectCategory = function (cat) {
    currentCategory = cat;
    document.querySelectorAll("#categoryPills .pill").forEach(p => {
      p.classList.toggle("active", p.dataset.cat === cat);
    });
    applyFilters();
  };

  /* ── Role selector ── */
  window.selectRole = function (role) {
    currentRole = role;
    document.querySelectorAll(".role-chip").forEach(c => {
      c.classList.toggle("active", c.dataset.role === role);
    });
    applyFilters();
  };

  /* ── Sort ── */
  window.setSort = function (sort) {
    currentSort = sort;
    document.querySelectorAll(".sort-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.sort === sort);
    });
    applyFilters();
  };

  /* ── Grade filter ── */
  window.toggleGrade = function (grade) {
    const btn = document.querySelector(`.grade-btn[data-grade="${grade}"]`);
    if (activeGrades.has(grade)) {
      activeGrades.delete(grade);
      btn.classList.remove("active");
    } else {
      activeGrades.add(grade);
      btn.classList.add("active");
    }
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

  function populateFilters() {
    const repos = [...new Set(allSkills.map(s => s.source_repo).filter(Boolean))];
    const repoSel = document.getElementById("repoFilter");
    repos.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      repoSel.appendChild(opt);
    });
    renderCategoryPills();
  }
/* FILTERS_PLACEHOLDER */

  /* ── Filter & Search (enhanced) ── */
  function applyFilters() {
    const q = document.getElementById("searchInput").value.toLowerCase().trim();
    const repo = document.getElementById("repoFilter").value;
    const clearBtn = document.getElementById("searchClear");
    const countEl = document.getElementById("searchResultCount");
    clearBtn.classList.toggle("visible", q.length > 0);

    let filtered = allSkills;

    // Category filter
    if (currentCategory) filtered = filtered.filter(s => s.category_id === currentCategory);

    // Repo filter
    if (repo) filtered = filtered.filter(s => s.source_repo === repo);

    // Role filter
    if (currentRole !== "all") {
      const rm = ROLE_MAP[currentRole];
      if (rm) {
        filtered = filtered.filter(s => {
          if (rm.categories.length && rm.categories.includes(s.category_id)) return true;
          if (rm.tags.length) {
            const st = s.tags || [];
            return rm.tags.some(t => st.includes(t));
          }
          return false;
        });
      }
    }

    // Grade filter
    if (activeGrades.size > 0) {
      filtered = filtered.filter(s => activeGrades.has(s.rating_grade));
    }

    // Search
    let searchQuery = "";
    if (q) {
      searchQuery = q;
      const expanded = expandSynonyms(q);
      const scored = [];
      for (const s of filtered) {
        const si = searchIndex.find(x => x.id === s.id);
        const text = si ? si.text : `${s.name} ${s.summary} ${(s.tags || []).join(" ")}`.toLowerCase();
        let bestScore = 0;
        for (const term of expanded) {
          const ns = scoreMatch(s.name || s.id, term);
          const ts = scoreMatch(text, term);
          bestScore = Math.max(bestScore, ns, ts);
        }
        if (bestScore > 0) scored.push({ skill: s, score: bestScore });
      }
      scored.sort((a, b) => b.score - a.score);
      filtered = scored.map(x => x.skill);
    }

    // Sort (when not searching)
    if (!q) {
      if (currentSort === "rating") {
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      } else if (currentSort === "newest") {
        filtered.sort((a, b) => (b.id > a.id ? 1 : -1));
      }
      // "recommended" = default order (by rating for non-search)
      if (currentSort === "recommended") {
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      }
    }

    countEl.textContent = q ? `${filtered.length} ${t("search_results")}` : "";
    renderSkills(filtered, searchQuery);
  }

  window.clearSearch = function () {
    document.getElementById("searchInput").value = "";
    applyFilters();
  };
/* MODAL_PLACEHOLDER */

  /* ── File tree builder ── */
  function buildFileTree(files) {
    const tree = {};
    (files || []).forEach(f => {
      const parts = f.split("/");
      let node = tree;
      parts.forEach((p, i) => {
        if (!node[p]) node[p] = i === parts.length - 1 ? null : {};
        if (node[p] !== null) node = node[p];
      });
    });
    function renderNode(obj, prefix) {
      let html = "";
      const entries = Object.entries(obj).sort(([, a], [, b]) => (a === null ? 1 : 0) - (b === null ? 1 : 0));
      for (const [name, children] of entries) {
        if (children === null) {
          html += `<div class="ft-file" style="padding-left:${prefix}px">📄 ${esc(name)}</div>`;
        } else {
          html += `<div class="ft-dir" onclick="this.classList.toggle('open')" style="padding-left:${prefix}px">📁 ${esc(name)}</div>`;
          html += `<div class="ft-children">${renderNode(children, prefix + 16)}</div>`;
        }
      }
      return html;
    }
    return renderNode(tree, 0);
  }

  /* ── Rating bar ── */
  function renderRatingBars(dims) {
    if (!dims || !Object.keys(dims).length) return "";
    const dimKeys = ["practicality", "clarity", "automation", "quality", "impact"];
    return dimKeys.map(d => {
      const val = dims[d] || 0;
      const pct = val * 10;
      return `<div class="rating-bar-row">
        <span class="rating-bar-label">${t("dim_" + d)}</span>
        <div class="rating-bar-track"><div class="rating-bar-fill" style="width:${pct}%"></div></div>
        <span class="rating-bar-val">${val}</span>
      </div>`;
    }).join("");
  }

  /* ── Modal ── */
  window.showSkill = async function (id) {
    const modal = document.getElementById("modal");
    const content = document.getElementById("modalContent");
    content.innerHTML = `<div class="loading-state" style="padding:40px 0"><div class="loading-spinner"></div></div>`;
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
    try {
      const skill = await fetchJSON(`skills/${id}/index.json`);
      const tags = (skill.tags || []).map(tag => `<span class="tag">${esc(tag)}</span>`).join(" ");
      const grade = skill.rating_grade || "D";
      const rating = skill.rating || 0;
      const installCmd = `python codeskill_cli.py install ${esc(skill.id)}`;
      const status = skill.security_status || "clean";
      const statusColor = status === "clean" ? "var(--green)" : status === "warning" ? "var(--orange)" : "var(--red)";
      const repo = skill.source && skill.source.repo || "";
      const repoUrl = skill.source && skill.source.repo_url || "#";
      const catObj = categories.find(c => c.id === skill.category_id);
      const catLabel = catObj ? (currentLang === "zh" ? catObj.name : (catObj.name_en || catObj.name)) : (skill.category_id || "—");

      // Left column
      let leftCol = `
        <div class="modal-left">
          <h2 class="modal-title">${esc(skill.name)}</h2>
          <div class="modal-meta-row">
            <span>by <a href="${esc(repoUrl)}" target="_blank" rel="noopener">${esc(repo)}</a></span>
            <span class="modal-cat-badge">${esc(catLabel)}</span>
            <span style="color:${statusColor};font-family:var(--font-mono);font-size:0.75rem">${esc(status)}</span>
          </div>
          ${skill.summary ? `<p class="modal-summary">${esc(skill.summary)}</p>` : ""}
          ${tags ? `<div class="modal-tags">${tags}</div>` : ""}`;

      // Flow diagram
      if (skill.flow_diagram) {
        leftCol += `
          <div class="modal-section">
            <div class="modal-section-header">
              <span class="modal-section-title">${t("modal_flow")}</span>
              <button class="modal-fs-btn" onclick="toggleFlowFullscreen()" title="${t("modal_fullscreen")}">⛶</button>
            </div>
            <div class="flow-container" id="flowContainer">
              <div class="mermaid" id="flowDiagram">${esc(skill.flow_diagram)}</div>
            </div>
          </div>`;
      }

      // Output preview
      if (skill.output_preview) {
        leftCol += `
          <div class="modal-section">
            <div class="modal-section-header">
              <span class="modal-section-title">${t("modal_preview")}</span>
              <button class="copy-btn small" onclick="copyText(\`${skill.output_preview.replace(/`/g, "\\`").replace(/\\/g, "\\\\")}\`, this)">${t("modal_copy_preview")}</button>
            </div>
            <pre class="output-preview">${esc(skill.output_preview)}</pre>
          </div>`;
      }

      // Target audience
      if (skill.target_audience) {
        leftCol += `
          <div class="modal-section">
            <span class="modal-section-title">${t("modal_audience")}</span>
            <p class="modal-audience">${esc(skill.target_audience)}</p>
          </div>`;
      }

      // Description (tab area)
      if (skill.description) {
        leftCol += `
          <div class="modal-section">
            <span class="modal-section-title">${t("modal_description")}</span>
            <div class="modal-desc">${esc(String(skill.description).substring(0, 800))}</div>
          </div>`;
      }

      // Compatible agents
      leftCol += `
          <div class="modal-section">
            <span class="modal-section-title">${t("modal_works_with")}</span>
            <div class="agent-list">
              <div class="agent-item"><span class="agent-name">Claude Code</span><code>~/.claude/skills/</code></div>
              <div class="agent-item"><span class="agent-name">Codex CLI</span><code>~/.codex/skills/</code></div>
              <div class="agent-item"><span class="agent-name">OpenCode</span><code>~/.config/opencode/skills/</code></div>
            </div>
          </div>
        </div>`;

      // Right column
      let rightCol = `
        <div class="modal-right">
          <div class="modal-grade-box" style="background:${gradeBg(grade)};border-color:${gradeColor(grade)}">
            <span class="modal-grade-letter" style="color:${gradeColor(grade)}">${grade}</span>
            <span class="modal-grade-score">${rating}</span>
            <span class="modal-grade-label">${t("modal_rating")}</span>
          </div>
          <div class="modal-actions">
            <button class="modal-action-btn primary" onclick="copyText('${installCmd}', this)">${t("modal_install")}</button>
          </div>
          <div class="modal-sidebar-section">
            <span class="modal-section-title">${t("modal_file_browser")}</span>
            <div class="file-tree">${buildFileTree(skill.file_list)}</div>
          </div>
          <div class="modal-sidebar-section">
            <span class="modal-section-title">${t("modal_dimensions")}</span>
            ${renderRatingBars(skill.rating_dimensions)}
          </div>
        </div>`;

      content.innerHTML = leftCol + rightCol;

      // Render Mermaid if present
      if (skill.flow_diagram) {
        try {
          const el = document.getElementById("flowDiagram");
          const { svg } = await mermaid.render("flowSvg_" + Date.now(), skill.flow_diagram);
          el.innerHTML = svg;
        } catch (e) {
          console.warn("Mermaid render failed:", e);
        }
      }
    } catch (e) {
      content.innerHTML = `<p style="color:var(--text-muted);font-size:0.9rem">Failed to load: ${esc(e.message)}</p>`;
    }
  };

  window.closeModal = function () {
    document.getElementById("modal").classList.remove("active");
    document.body.style.overflow = "";
  };

  window.toggleFlowFullscreen = function () {
    const container = document.getElementById("flowContainer");
    if (container) container.classList.toggle("fullscreen");
  };
/* TABS_PLACEHOLDER */

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
    copyText(instruction + "\n" + cmd, btn);
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

  /* ── Init ── */
  async function init() {
    initTheme();
    applyLang();
    const loading = document.getElementById("loading");
    try {
      const [skillsData, searchData, catData, packsData, statsData, rankingsData, synData] = await Promise.all([
        fetchJSON("skills/index.json"),
        fetchJSON("search/index.json"),
        fetchJSON("categories/index.json"),
        fetchJSON("packs/index.json"),
        fetchJSON("stats/index.json"),
        fetchJSON("rankings/index.json").catch(() => ({ items: [] })),
        fetchJSON("synonyms/index.json").catch(() => ({})),
      ]);
      allSkills = skillsData.items || [];
      searchIndex = searchData.items || [];
      categories = catData.items || [];
      rankings = (rankingsData.items || []).filter(s => (s.rating_grade === "S" || s.rating_grade === "A"));
      synonyms = synData || {};
      loading.style.display = "none";
      populateFilters();
      renderSkills(allSkills);
      renderPacks(packsData.items || []);
      renderStats(statsData);
      renderRankings();
      renderFAQ();
    } catch (e) {
      loading.innerHTML = `<div class="empty-icon">⚠</div><span>Failed to load data. Run the aggregator first.</span>`;
    }

    document.getElementById("searchInput").addEventListener("input", applyFilters);
    document.getElementById("repoFilter").addEventListener("change", applyFilters);
    document.getElementById("modal").addEventListener("click", function (e) {
      if (e.target === this) closeModal();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        const fc = document.getElementById("flowContainer");
        if (fc && fc.classList.contains("fullscreen")) { fc.classList.remove("fullscreen"); return; }
        closeModal();
      }
    });
  }

  init();
})();
