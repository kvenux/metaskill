"""Configuration: source repos, categories, security rules, skill packs."""

import os

# --- LLM Configuration ---
LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://api-s.zwenooo.link/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-5.4")

# --- Source Repositories ---
SOURCE_REPOS = [
    {
        "id": "anthropics-skills",
        "url": "https://github.com/anthropics/skills.git",
        "repo_url": "https://github.com/anthropics/skills",
        "skills_dirs": ["skills"],
        "raw_base": "https://raw.githubusercontent.com/anthropics/skills/main",
    },
    {
        "id": "baoyu-skills",
        "url": "https://github.com/JimLiu/baoyu-skills.git",
        "repo_url": "https://github.com/JimLiu/baoyu-skills",
        "skills_dirs": ["skills"],
        "raw_base": "https://raw.githubusercontent.com/JimLiu/baoyu-skills/main",
    },
    {
        "id": "awesome-claude-skills",
        "url": "https://github.com/ComposioHQ/awesome-claude-skills.git",
        "repo_url": "https://github.com/ComposioHQ/awesome-claude-skills",
        "skills_dirs": ["", "composio-skills"],
        "raw_base": "https://raw.githubusercontent.com/ComposioHQ/awesome-claude-skills/master",
    },
    {
        "id": "myclaude",
        "url": "https://github.com/cexll/myclaude.git",
        "repo_url": "https://github.com/cexll/myclaude",
        "skills_dirs": ["skills"],
        "raw_base": "https://raw.githubusercontent.com/cexll/myclaude/main",
    },
]

REPOS_DIR = os.path.join(os.path.dirname(__file__), "_repos")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "api")
LLM_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".llm_cache")

# --- Categories (20) ---
CATEGORIES = {
    "development-tools": {"name": "开发工具", "description": "代码审查、调试、重构、changelog、lint"},
    "development-workflow": {"name": "开发工作流", "description": "开发编排、多Agent协作、特性开发流程"},
    "testing-qa": {"name": "测试质量", "description": "单元测试、Web测试、测试用例生成、Playwright"},
    "office-documents": {"name": "办公文档", "description": "Word/PPT/Excel/PDF 创建编辑处理"},
    "design-ui": {"name": "设计与UI", "description": "前端设计、品牌规范、主题、原型、UI/UX"},
    "generative-art": {"name": "生成式创意", "description": "算法艺术、画布设计、GIF动画、视觉艺术"},
    "image-generation": {"name": "图像生成", "description": "AI图像、信息图、漫画、封面图、幻灯片"},
    "content-processing": {"name": "内容处理", "description": "翻译、Markdown转换、URL抓取、格式化"},
    "content-writing": {"name": "内容写作", "description": "文章撰写、研究写作、文档协作、内部沟通"},
    "social-media": {"name": "社交媒体", "description": "发布到X/微信/微博/小红书、推文优化"},
    "media-processing": {"name": "媒体处理", "description": "图像压缩、视频下载、图像增强、格式转换"},
    "business-crm": {"name": "商业与CRM", "description": "CRM、销售、客户管理、发票、竞品分析"},
    "project-management": {"name": "项目管理", "description": "任务管理、看板、敏捷、需求管理"},
    "communication-collab": {"name": "沟通协作", "description": "即时通讯、邮件、会议、团队协作"},
    "devops-cloud": {"name": "DevOps与云", "description": "CI/CD、代码托管、云服务、监控、部署"},
    "data-analytics": {"name": "数据分析", "description": "数据库、BI、分析平台、数据处理"},
    "finance-accounting": {"name": "财务会计", "description": "记账、支付、发票、财务报表"},
    "marketing-growth": {"name": "营销增长", "description": "广告、SEO、邮件营销、社交营销、线索"},
    "ai-agents": {"name": "AI智能体", "description": "多Agent编排、自主Agent、长任务框架"},
    "utility": {"name": "实用工具", "description": "文件整理、域名生成、抽奖、浏览器自动化、技能管理"},
}

# --- Keyword-based fallback categorization rules ---
CATEGORY_KEYWORDS = {
    "development-tools": ["code-review", "debug", "refactor", "changelog", "lint", "claude-api", "mcp-builder", "api-integration"],
    "development-workflow": ["dev", "workflow", "orchestrat", "harness", "sparv", "omo", "feature-develop"],
    "testing-qa": ["test", "playwright", "qa", "webapp-testing", "e2e", "unit-test"],
    "office-documents": ["docx", "pptx", "xlsx", "pdf", "word", "excel", "powerpoint", "office"],
    "design-ui": ["frontend-design", "brand", "theme", "prototype", "ui-ux", "ui", "ux", "design-system"],
    "generative-art": ["algorithmic-art", "canvas-design", "gif", "generative", "visual-art", "p5js"],
    "image-generation": ["image-gen", "infographic", "comic", "cover-image", "slide-deck", "illustration", "xhs-image"],
    "content-processing": ["translat", "markdown", "url-to-", "format-markdown", "html-convert", "content-capture"],
    "content-writing": ["article", "writing", "coauthor", "internal-comms", "research-writ", "newsletter"],
    "social-media": ["post-to-", "twitter", "wechat", "weibo", "xiaohongshu", "social-publish"],
    "media-processing": ["compress-image", "video-download", "image-enhance", "format-convert", "media"],
    "business-crm": ["salesforce", "hubspot", "apollo", "crm", "invoice", "customer", "lead"],
    "project-management": ["asana", "jira", "trello", "notion", "project", "task-manage", "kanban", "agile", "product-require"],
    "communication-collab": ["slack", "discord", "gmail", "email", "meeting", "teams", "chat", "messaging"],
    "devops-cloud": ["github", "gitlab", "aws", "vercel", "docker", "kubernetes", "ci-cd", "deploy", "terraform", "jenkins"],
    "data-analytics": ["snowflake", "databricks", "analytics", "database", "data-pipeline", "bi", "warehouse"],
    "finance-accounting": ["quickbooks", "stripe", "xero", "accounting", "payment", "billing", "payroll", "expense"],
    "marketing-growth": ["mailchimp", "facebook", "ads", "seo", "email-campaign", "marketing", "lead-research", "competitive"],
    "ai-agents": ["codeagent", "multi-agent", "autonomous", "agent", "orchestration"],
    "utility": ["file-organizer", "domain-name", "browser", "skill-creator", "skill-install", "lottery", "organiz"],
}

# --- Security Scanning Rules ---
SECURITY_CRITICAL_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r"nc\s+-e",
    r"xmrig|cryptonight|stratum\+tcp|coinhive|minergate",
    r":(){ :\|:& };:",  # fork bomb
]

SECURITY_CRITICAL_EXTENSIONS = {".exe", ".dll", ".so", ".dylib"}

SECURITY_WARNING_PATTERNS = [
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(",
    r"subprocess.*shell\s*=\s*True",
    r"curl\s+.*-d\s+.*@",
    r"base64\s+-d\s*\|",
    r"\.ssh/",
    r"\.aws/",
    r"\.env\b",
    r"/etc/passwd",
    r"/etc/shadow",
]

SECURITY_SCAN_EXTENSIONS = {".md", ".py", ".sh", ".js", ".ps1", ".ts", ".bash", ".zsh"}
SECURITY_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# --- Skill Packs (8) ---
SKILL_PACKS = {
    "office-power-pack": {
        "name": "办公全家桶",
        "description": "Word/PPT/Excel/PDF 办公文档全套技能",
        "skills": ["docx", "pptx", "xlsx", "pdf"],
    },
    "content-creator-pack": {
        "name": "内容创作包",
        "description": "AI图像、信息图、漫画、封面图、幻灯片创作",
        "skills": ["baoyu-article-illustrator", "baoyu-cover-image", "baoyu-infographic", "baoyu-slide-deck", "baoyu-comic"],
    },
    "social-publisher-pack": {
        "name": "社交发布包",
        "description": "一键发布到X/微信/微博/小红书等社交平台",
        "skills": ["baoyu-post-to-x", "baoyu-post-to-wechat", "baoyu-post-to-weibo", "baoyu-xhs-images", "twitter-algorithm-optimizer"],
    },
    "dev-workflow-pack": {
        "name": "开发工作流包",
        "description": "开发编排、测试、changelog等开发全流程",
        "skills": ["dev", "do", "sparv", "harness", "changelog-generator", "webapp-testing"],
    },
    "design-pack": {
        "name": "设计包",
        "description": "算法艺术、画布设计、品牌规范、前端设计、主题工厂",
        "skills": ["algorithmic-art", "canvas-design", "brand-guidelines", "frontend-design", "theme-factory"],
    },
    "content-processing-pack": {
        "name": "内容处理包",
        "description": "翻译、Markdown转换、格式化、图像压缩",
        "skills": ["baoyu-translate", "baoyu-url-to-markdown", "baoyu-format-markdown", "baoyu-markdown-to-html", "baoyu-compress-image"],
    },
    "ai-builder-pack": {
        "name": "AI构建包",
        "description": "Claude API、MCP构建、技能创建、代码Agent",
        "skills": ["claude-api", "mcp-builder", "skill-creator", "codeagent"],
    },
    "newcomer-onboarding-pack": {
        "name": "新手入门包",
        "description": "技能创建、文档协作、Web测试、changelog生成",
        "skills": ["skill-creator", "doc-coauthoring", "webapp-testing", "changelog-generator"],
    },
}
