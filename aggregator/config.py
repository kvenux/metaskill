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

# --- Categories (20, redesigned to match SkillHub) ---
CATEGORIES = {
    "development": {"name": "开发", "name_en": "Development", "description": "代码审查、调试、重构、changelog、lint、开发工作流"},
    "frontend": {"name": "前端", "name_en": "Frontend", "description": "前端框架、组件开发、CSS、响应式设计"},
    "backend": {"name": "后端", "name_en": "Backend", "description": "API开发、服务端逻辑、数据库交互、微服务"},
    "testing": {"name": "测试", "name_en": "Testing", "description": "单元测试、E2E测试、Playwright、QA自动化"},
    "devops": {"name": "DevOps", "name_en": "DevOps", "description": "CI/CD、Docker、Kubernetes、部署、监控"},
    "cloud": {"name": "云服务", "name_en": "Cloud", "description": "AWS、Vercel、云函数、基础设施即代码"},
    "security": {"name": "安全", "name_en": "Security", "description": "安全审计、漏洞扫描、权限管理、加密"},
    "data": {"name": "数据", "name_en": "Data", "description": "数据库、数据分析、BI、数据管道、ETL"},
    "ai-ml": {"name": "AI/ML", "name_en": "AI/ML", "description": "AI Agent、机器学习、LLM编排、模型训练"},
    "mobile": {"name": "移动端", "name_en": "Mobile", "description": "iOS、Android、React Native、Flutter开发"},
    "design": {"name": "设计", "name_en": "Design", "description": "UI/UX设计、品牌规范、算法艺术、视觉创意"},
    "documentation": {"name": "文档", "name_en": "Documentation", "description": "技术文档、API文档、README、知识库"},
    "writing": {"name": "写作", "name_en": "Writing", "description": "文章撰写、内容创作、翻译、Newsletter"},
    "productivity": {"name": "效率", "name_en": "Productivity", "description": "办公文档、文件管理、自动化工具、效率提升"},
    "media": {"name": "媒体", "name_en": "Media", "description": "图像生成、视频处理、信息图、漫画、幻灯片"},
    "social": {"name": "社交", "name_en": "Social", "description": "社交媒体发布、推文优化、小红书、微信"},
    "communication": {"name": "通讯", "name_en": "Communication", "description": "Slack、邮件、会议、团队协作"},
    "business": {"name": "商业", "name_en": "Business", "description": "CRM、财务、营销、SEO、竞品分析"},
    "meta": {"name": "元技能", "name_en": "Meta", "description": "技能创建、技能管理、Agent编排、元编程"},
    "integration": {"name": "集成", "name_en": "Integration", "description": "API集成、格式转换、数据导入导出、Webhook"},
}

# --- Keyword-based fallback categorization rules ---
CATEGORY_KEYWORDS = {
    "development": ["code-review", "debug", "refactor", "changelog", "lint", "dev", "workflow", "orchestrat", "harness", "sparv", "feature-develop"],
    "frontend": ["frontend", "react", "vue", "angular", "css", "html", "ui-component", "responsive", "frontend-design"],
    "backend": ["api", "server", "backend", "rest", "graphql", "microservice", "express", "fastapi", "django"],
    "testing": ["test", "playwright", "qa", "webapp-testing", "e2e", "unit-test", "jest", "cypress"],
    "devops": ["ci-cd", "docker", "kubernetes", "deploy", "terraform", "jenkins", "github-action", "pipeline"],
    "cloud": ["aws", "vercel", "azure", "gcp", "cloud", "serverless", "lambda", "s3"],
    "security": ["security", "audit", "vulnerab", "encrypt", "auth", "permission", "firewall", "pentest"],
    "data": ["snowflake", "databricks", "analytics", "database", "data-pipeline", "bi", "warehouse", "sql", "etl"],
    "ai-ml": ["codeagent", "multi-agent", "autonomous", "agent", "orchestration", "llm", "ml", "model", "ai"],
    "mobile": ["ios", "android", "react-native", "flutter", "mobile", "swift", "kotlin"],
    "design": ["brand", "theme", "prototype", "ui-ux", "ui", "ux", "design-system", "algorithmic-art", "canvas-design", "gif", "generative", "visual-art", "p5js"],
    "documentation": ["doc", "readme", "api-doc", "knowledge-base", "technical-writ", "documentation"],
    "writing": ["article", "writing", "coauthor", "research-writ", "newsletter", "blog", "content-writ"],
    "productivity": ["docx", "pptx", "xlsx", "pdf", "word", "excel", "powerpoint", "office", "file-organizer", "domain-name", "browser", "lottery", "organiz", "utility"],
    "media": ["image-gen", "infographic", "comic", "cover-image", "slide-deck", "illustration", "xhs-image", "compress-image", "video-download", "image-enhance", "format-convert", "media"],
    "social": ["post-to-", "twitter", "wechat", "weibo", "xiaohongshu", "social-publish", "social-media"],
    "communication": ["slack", "discord", "gmail", "email", "meeting", "teams", "chat", "messaging", "internal-comms"],
    "business": ["salesforce", "hubspot", "apollo", "crm", "invoice", "customer", "lead", "quickbooks", "stripe", "xero", "accounting", "payment", "billing", "payroll", "expense", "mailchimp", "facebook", "ads", "seo", "email-campaign", "marketing", "lead-research", "competitive", "asana", "jira", "trello", "notion", "project", "task-manage", "kanban", "agile"],
    "meta": ["skill-creator", "skill-install", "mcp-builder", "claude-api", "meta-skill"],
    "integration": ["translat", "markdown", "url-to-", "format-markdown", "html-convert", "content-capture", "api-integration", "webhook", "import", "export", "convert"],
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

# --- Skill Packs (13) ---
SKILL_PACKS = {
    "office-power-pack": {
        "name": "办公全家桶",
        "description": "Word/PPT/Excel/PDF 办公文档全套技能",
        "emoji": "📄",
        "featured": True,
        "skills": ["docx", "pptx", "xlsx", "pdf"],
    },
    "content-creator-pack": {
        "name": "内容创作包",
        "description": "AI图像、信息图、漫画、封面图、幻灯片创作",
        "emoji": "🎨",
        "featured": True,
        "skills": ["baoyu-article-illustrator", "baoyu-cover-image", "baoyu-infographic", "baoyu-slide-deck", "baoyu-comic"],
    },
    "social-publisher-pack": {
        "name": "社交发布包",
        "description": "一键发布到X/微信/微博/小红书等社交平台",
        "emoji": "📱",
        "featured": False,
        "skills": ["baoyu-post-to-x", "baoyu-post-to-wechat", "baoyu-post-to-weibo", "baoyu-xhs-images", "twitter-algorithm-optimizer"],
    },
    "dev-workflow-pack": {
        "name": "开发工作流包",
        "description": "开发编排、测试、changelog等开发全流程",
        "emoji": "⚡",
        "featured": True,
        "skills": ["dev", "do", "sparv", "harness", "changelog-generator", "webapp-testing"],
    },
    "design-pack": {
        "name": "设计包",
        "description": "算法艺术、画布设计、品牌规范、前端设计、主题工厂",
        "emoji": "🎯",
        "featured": False,
        "skills": ["algorithmic-art", "canvas-design", "brand-guidelines", "frontend-design", "theme-factory"],
    },
    "content-processing-pack": {
        "name": "内容处理包",
        "description": "翻译、Markdown转换、格式化、图像压缩",
        "emoji": "🔄",
        "featured": False,
        "skills": ["baoyu-translate", "baoyu-url-to-markdown", "baoyu-format-markdown", "baoyu-markdown-to-html", "baoyu-compress-image"],
    },
    "ai-builder-pack": {
        "name": "AI构建包",
        "description": "Claude API、MCP构建、技能创建、代码Agent",
        "emoji": "🤖",
        "featured": True,
        "skills": ["claude-api", "mcp-builder", "skill-creator", "codeagent"],
    },
    "newcomer-onboarding-pack": {
        "name": "新手入门包",
        "description": "技能创建、文档协作、Web测试、changelog生成",
        "emoji": "🌱",
        "featured": False,
        "skills": ["skill-creator", "doc-coauthoring", "webapp-testing", "changelog-generator"],
    },
    "solopreneur-toolkit": {
        "name": "独立开发者工具箱",
        "description": "从原型到部署，独立开发者的全栈技能包",
        "emoji": "🚀",
        "featured": True,
        "skills": ["dev", "frontend-design", "webapp-testing", "changelog-generator", "brand-guidelines"],
    },
    "api-development-pack": {
        "name": "API开发包",
        "description": "API设计、文档、测试、集成全流程",
        "emoji": "🔌",
        "featured": False,
        "skills": ["claude-api", "mcp-builder", "api-integration", "doc-coauthoring"],
    },
    "security-audit-pack": {
        "name": "安全审计包",
        "description": "代码安全审计、漏洞扫描、权限检查",
        "emoji": "🛡️",
        "featured": False,
        "skills": ["code-review", "webapp-testing"],
    },
    "mobile-dev-pack": {
        "name": "移动开发包",
        "description": "移动端UI设计、跨平台开发、测试",
        "emoji": "📱",
        "featured": False,
        "skills": ["frontend-design", "webapp-testing", "theme-factory"],
    },
    "ai-ml-workflow-pack": {
        "name": "AI/ML工作流",
        "description": "AI Agent编排、模型集成、智能自动化",
        "emoji": "🧠",
        "featured": True,
        "skills": ["codeagent", "claude-api", "mcp-builder", "skill-creator"],
    },
}

# --- Search Synonyms (for frontend fuzzy search) ---
SEARCH_SYNONYMS = {
    "ppt": ["powerpoint", "pptx", "slide", "presentation"],
    "doc": ["word", "docx", "document"],
    "xls": ["excel", "xlsx", "spreadsheet"],
    "test": ["testing", "qa", "e2e", "unit-test", "playwright"],
    "deploy": ["deployment", "ci-cd", "devops", "release"],
    "ai": ["artificial-intelligence", "ml", "machine-learning", "llm", "agent"],
    "api": ["rest", "graphql", "endpoint", "integration"],
    "css": ["style", "stylesheet", "design", "frontend"],
    "db": ["database", "sql", "postgres", "mysql", "mongo"],
    "img": ["image", "picture", "photo", "illustration"],
    "auth": ["authentication", "authorization", "login", "oauth"],
    "k8s": ["kubernetes"],
    "ts": ["typescript"],
    "js": ["javascript"],
    "py": ["python"],
}
