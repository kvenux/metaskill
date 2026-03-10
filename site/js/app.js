/* MetaSkill Frontend App */
(function () {
  "use strict";

  const API = "api";
  let allSkills = [];
  let searchIndex = [];
  let categories = [];

  // --- Theme ---
  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || (!saved && matchMedia("(prefers-color-scheme:dark)").matches)) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  }
  window.toggleTheme = function () {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
    localStorage.setItem("theme", isDark ? "light" : "dark");
  };

  // --- Fetch helpers ---
  async function fetchJSON(path) {
    const resp = await fetch(`${API}/${path}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  // --- Render ---
  function renderSkillCard(skill) {
    const tags = (skill.tags || []).slice(0, 3).map(t => `<span class="tag">${esc(t)}</span>`).join("");
    const statusClass = skill.security_status === "safe" ? "badge-safe" : skill.security_status === "warning" ? "badge-warning" : "badge-blocked";
    const statusIcon = skill.security_status === "safe" ? "✓" : skill.security_status === "warning" ? "⚠" : "✗";
    return `<div class="skill-card" onclick="showSkill('${esc(skill.id)}')">
      <h3>${esc(skill.name || skill.id)}</h3>
      <div class="summary">${esc(skill.summary || "")}</div>
      <div class="meta">
        <span class="category-badge">${esc(skill.category_id || "")}</span>
        ${tags}
        <span class="${statusClass}">${statusIcon}</span>
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
      empty.style.display = "block";
    } else {
      empty.style.display = "none";
      grid.innerHTML = skills.map(renderSkillCard).join("");
    }
  }

  function renderPacks(packs) {
    const grid = document.getElementById("packGrid");
    grid.innerHTML = packs.map(p => `<div class="pack-card">
      <h3>${esc(p.name)}</h3>
      <div class="desc">${esc(p.description)}</div>
      <div class="count">${p.skill_count || 0} 个技能</div>
    </div>`).join("");
  }

  function renderStats(stats) {
    const bar = document.getElementById("statsBar");
    bar.innerHTML = `
      <div class="stat-item">技能总数 <span>${stats.total_skills || 0}</span></div>
      <div class="stat-item">分类 <span>${stats.total_categories || 0}</span></div>
      <div class="stat-item">标签 <span>${stats.total_tags || 0}</span></div>
      <div class="stat-item">技能包 <span>${stats.total_packs || 0}</span></div>
    `;
  }

  function populateFilters() {
    const catSel = document.getElementById("categoryFilter");
    categories.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.skill_count})`;
      catSel.appendChild(opt);
    });
    // Repo filter
    const repos = [...new Set(allSkills.map(s => s.source_repo))];
    const repoSel = document.getElementById("repoFilter");
    repos.forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      repoSel.appendChild(opt);
    });
  }

  // --- Filter & Search ---
  function applyFilters() {
    const q = document.getElementById("searchInput").value.toLowerCase().trim();
    const cat = document.getElementById("categoryFilter").value;
    const repo = document.getElementById("repoFilter").value;

    let filtered = allSkills;
    if (cat) filtered = filtered.filter(s => s.category_id === cat);
    if (repo) filtered = filtered.filter(s => s.source_repo === repo);
    if (q) {
      const matchIds = new Set(
        searchIndex.filter(s => s.text.includes(q)).map(s => s.id)
      );
      filtered = filtered.filter(s => matchIds.has(s.id));
    }
    renderSkills(filtered);
  }

  // --- Modal ---
  window.showSkill = async function (id) {
    const modal = document.getElementById("modal");
    const content = document.getElementById("modalContent");
    content.innerHTML = "<p>加载中...</p>";
    modal.classList.add("active");
    try {
      const skill = await fetchJSON(`skills/${id}/index.json`);
      const tags = (skill.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join(" ");
      const files = (skill.file_list || []).map(f => `<li>${esc(f)}</li>`).join("");
      content.innerHTML = `
        <h2>${esc(skill.name)}</h2>
        <div class="detail-row"><span class="detail-label">摘要</span><p>${esc(skill.summary)}</p></div>
        <div class="detail-row"><span class="detail-label">描述</span><p>${esc(skill.description).substring(0, 500)}</p></div>
        <div class="detail-row"><span class="detail-label">分类</span> ${esc(skill.category_id)}</div>
        <div class="detail-row"><span class="detail-label">标签</span> ${tags}</div>
        <div class="detail-row"><span class="detail-label">来源</span> <a href="${esc(skill.source.repo_url)}" target="_blank">${esc(skill.source.repo)}</a> / ${esc(skill.source.path)}</div>
        <div class="detail-row"><span class="detail-label">安全状态</span> <span class="badge-${skill.security_status}">${esc(skill.security_status)}</span></div>
        <div class="detail-row"><span class="detail-label">文件</span><ul>${files}</ul></div>
        <div class="detail-row">
          <span class="detail-label">安装命令</span>
          <div class="install-cmd">
            <code>python codeskill_cli.py install ${esc(skill.id)}</code>
            <button onclick="copyText('python codeskill_cli.py install ${esc(skill.id)}')">复制</button>
          </div>
        </div>
      `;
    } catch (e) {
      content.innerHTML = `<p>加载失败: ${esc(e.message)}</p>`;
    }
  };

  window.closeModal = function () {
    document.getElementById("modal").classList.remove("active");
  };

  // --- Clipboard ---
  window.copyInstall = function () {
    copyText("curl -s https://<your-domain>/api/codeskill/install-sh | bash");
  };
  window.copyText = function (text) {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  // --- Escape HTML ---
  function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  // --- Init ---
  async function init() {
    initTheme();
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
      loading.textContent = "加载数据失败，请确认 API 文件已生成。";
    }

    document.getElementById("searchInput").addEventListener("input", applyFilters);
    document.getElementById("categoryFilter").addEventListener("change", applyFilters);
    document.getElementById("repoFilter").addEventListener("change", applyFilters);
    document.getElementById("modal").addEventListener("click", function (e) {
      if (e.target === this) closeModal();
    });
  }

  init();
})();
