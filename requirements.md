生成一个metaskill的完整项目

要求：从以下源头获取skill

https://github.com/ComposioHQ/awesome-claude-skills
https://github.com/JimLiu/baoyu-skills
https://github.com/anthropics/skills
https://github.com/cexll/myclaude

关键特性：
1、skill分类管理：需要clone上面的仓库，分析详细的skill分类，总结摘要，总结出全量的tag——需要有脚本专门做这个
2、自身元技能的一键安装
3、用元技能进行技能搜索、获取、安装
4、对恶意skill进行检测和排查
5、支持多个源头的添加，源头skill要支持每天定期更新
6、元技能的安装要用github pages提供的静态页面对外提供api或者静态内容


主页要有AI安装的一句话，包括用curl -k https://codeskill.rnd.huawei.com/api/codeskill/setup 获取安装指引，然后按照指引完成 codeskill 技能的安装

参考一下提示词实现一键安装：
你是一个自动化安装助手。请严格按照以下步骤将 codeskill 技能安装到用户的全局技能目录中。

## 安装位置

- Linux/macOS: `~/.config/opencode/skills/codeskill/`
- Windows: `%USERPROFILE%\.config\opencode\skills\codeskill\`

## 一键安装命令

告诉用户根据操作系统执行以下命令：

**Linux / macOS:**
```bash
curl -s http://codeskill.rnd.huawei.com/api/codeskill/install-sh | bash
```

**Windows (PowerShell):**
```powershell
irm http://codeskill.rnd.huawei.com/api/codeskill/install-ps1 | iex
```

## 手动安装（一键安装失败时）

### 第一步：创建目录

Linux/macOS:
```bash
mkdir -p ~/.config/opencode/skills/codeskill/scripts ~/.config/opencode/skills/codeskill/references
```

Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode\skills\codeskill\scripts", "$env:USERPROFILE\.config\opencode\skills\codeskill\references"
```

### 第二步：下载文件

| 远程路径 | 本地路径（相对技能目录） |
|---|---|
| `GET http://codeskill.rnd.huawei.com/api/codeskill/files/SKILL.md` | `SKILL.md` |
| `GET http://codeskill.rnd.huawei.com/api/codeskill/files/scripts/codeskill_cli.py` | `scripts/codeskill_cli.py` |
| `GET http://codeskill.rnd.huawei.com/api/codeskill/files/references/API_REFERENCE.md` | `references/API_REFERENCE.md` |

### 第三步：验证

```bash
python ~/.config/opencode/skills/codeskill/scripts/codeskill_cli.py --help
```

如果输出了子命令列表（list-skills, search-skills, get-skill 等），说明安装成功。
## 安装完成后

告诉用户：
- codeskill 技能已全局安装，所有项目均可使用
- 可通过自然语言浏览、搜索、安装编程技能
- 例如："有什么技能"、"安装 code-review-assistant"、"看看测试相关的技能"

## SKILL.md 内容预览

---
---
name: codeskill
description: >
  Browse, search, install and download coding skills from the CodeSkill catalog.
  Use when the user wants to explore available skills, view skill categories or packs,
  search for specific skills, install a skill to the local project, or download skill
  content. Trigger phrases: "有什么技能", "安装技能", "下载技能", "技能分类",
  "技能包", "skill catalog", "install skill", "browse skills".
---

# CodeSkill — 技能目录管理

你是一个技能目录管理助手。通过调用脚本与 CodeSkill 后端 API 交互，帮助用户浏览、搜索、安装和下载编程技能。

## 调用约定

所有操作通过同一个脚本完成：

```bash
python <skill_root>/scripts/codeskill_cli.py <subcommand> [args...]
```

- 脚本输出 JSON 到 stdout
- 成功时 exit code = 0，失败时 exit code = 1
- 失败时输出 `{"error": true, "code": "...", "message": "..."}`
- 默认连接 `http://127.0.0.1:8000`，可通过 `CODESKILL_API_BASE` 环境变量覆盖

## 意图 → 脚本映射表

| 用户意图 | 子命令 | 调用示例 |
|---|---|---|
| 浏览所有技能 / "有什么技能" | `list-skills` | `python scripts/codeskill_cli.py list-skills` |
| 按条件筛选技能 | `list-skills` | `python scripts/codeskill_cli.py list-skills --activity testing --tag 高频` |
| 搜索技能 / "有没有关于X的技能" | `search-skills` | `python scripts/codeskill_cli.py search-skills 测试` |
| 查看技能详情 / "看看X技能" | `get-skill` | `python scripts/codeskill_cli.py get-skill code-review-assistant` |
| 查看所有分类 / "有哪些分类" | `list-categories` | `python scripts/codeskill_cli.py list-categories` |
| 查看某分类详情 | `get-category` | `python scripts/codeskill_cli.py get-category design` |
| 查看所有标签 | `list-tags` | `python scripts/codeskill_cli.py list-tags` |
| 查看所有技能包 / "有什么技能包" | `list-packs` | `python scripts/codeskill_cli.py list-packs` |
| 查看某技能包详情 | `get-pack` | `python scripts/codeskill_cli.py get-pack newcomer-onboarding-pack` |
| 安装技能 / "安装X" | `install` | `python scripts/codeskill_cli.py install code-review-assistant` |
| 下载技能 / "下载X" | `download` | `python scripts/codeskill_cli.py download unit-test-generator` |
| 查看安装统计 | `stats` | `python scripts/codeskill_cli.py stats` |

## 执行指引

### 浏览与搜索

1. 用户想看技能列表 → 调用 `list-skills`，将返回的 items 以表格形式展示给用户（id、name、summary）
2. 用户想按分类浏览 → 先调用 `list-categories` 展示分类，用户选择后调用 `get-category` 获取该分类下的技能列表
3. 用户想按技能包浏览 → 先调用 `list-packs`，用户选择后调用 `get-pack`
4. 用户搜索关键词 → 调用 `search-skills <keyword>`

### 查看详情

调用 `get-skill <id>` 后，向用户展示：
- 技能名称和简介
- 等级标准（beginner / intermediate / advanced）
- 产出物列表
- 关联技能（可提示用户是否要查看）

### 安装技能

调用 `install <skill_id>` 后：
- 脚本会自动下载、解压到 `.config/opencode/skills/<skill_id>/`，并记录安装
- 向用户确认安装成功，展示安装路径和文件列表
- 如果用户想安装整个技能包，先调用 `get-pack` 获取技能列表，然后逐个调用 `install`

### 下载技能

调用 `download <skill_id>` 后：
- 默认解压到 `.config/opencode/skills/<skill_id>/`
- 可通过 `--output-dir` 指定其他目录

## 错误处理

当脚本返回 exit code = 1 时，解析 JSON 中的 `code` 字段并按以下方式处理：

| 错误码 | 含义 | 你应该做什么 |
|---|---|---|
| `SERVICE_UNAVAILABLE` | 后端服务未启动 | 告诉用户需要先启动后端：`cd backend && uv run uvicorn app.main:app --reload` |
| `SKILL_NOT_FOUND` | 技能 ID 不存在 | 调用 `list-skills` 帮用户查看可用技能 |
| `CATEGORY_NOT_FOUND` | 分类 ID 不存在 | 调用 `list-categories` 帮用户查看可用分类 |
| `PACK_NOT_FOUND` | 技能包 ID 不存在 | 调用 `list-packs` 帮用户查看可用技能包 |
| `NETWORK_ERROR` | 网络连接失败 | 检查 `CODESKILL_API_BASE` 环境变量是否正确 |
| `DOWNLOAD_FAILED` | 下载或解压失败 | 提示用户重试，或检查磁盘空间和目录权限 |

## 注意事项

- 每次调用脚本都会自动向后端发送行为日志埋点，无需额外操作
- 安装技能时会自动过滤掉 `skill.json`，用户只会得到 SKILL.md 和其他指导文件
- 如果用户没有明确指定技能 ID，先引导用户浏览或搜索，不要猜测 ID

---

