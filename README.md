# Skills Auto-Dispatcher

自动识别任务匹配哪个 skill，路由、拆解、失败回退。跨平台通用。

## 用户一句话安装

对你的 AI 助手说：

> 帮我在 GitHub 上搜 YiYiii-Zhang/skills-auto-dispatcher，clone 到 `.agents/skills/`，然后跑一次 scan 和 build

AI 助手执行完就装好了。后续每次你说任务，dispatcher 自动匹配技能。

## 各平台能力

| 能力 | Claude Code | Codex CLI | Codex Web | OpenClaw | Copilot CLI |
|------|:-----------:|:---------:|:---------:|:--------:|:-----------:|
| 扫描技能 + 建索引 | Y | Y | Y | Y | Y |
| 路由匹配 | Y | Y | Y | Y | Y |
| 自动调用 Skill 工具 | Y | — | — | — | — |
| 输出匹配结果（手动跟进）| Y | Y | Y | Y | Y |
| 子任务拆解 | Y | Y | Y | Y | Y |

**唯一差异**：只有 Claude Code 的 `Skill` 工具能被 dispatcher 自动调用。其他平台 dispatcher 会告诉你"该用哪个 skill"，你需要自己跟一句"用 xx skill 处理"。

其他平台之所以不能自动调用，是因为没有原生的动态 skill 加载机制。Codex 和 OpenClaw 用户需要手动读取匹配到的 SKILL.md 然后按指示操作。

## 各平台安装

### Claude Code

```bash
git clone https://github.com/YiYiii-Zhang/skills-auto-dispatcher.git .agents/skills/skills-auto-dispatcher
bash .agents/skills/skills-auto-dispatcher/scripts/scan-skills.sh \
  | python3 .agents/skills/skills-auto-dispatcher/scripts/update-skills-index.py
```

Auto-trigger：在项目根目录 `CLAUDE.md` 加一行：

```markdown
收到任务时先跑 route-task.py，有 >= 0.3 的匹配就调 Skill。
```

### Codex CLI

```bash
git clone https://github.com/YiYiii-Zhang/skills-auto-dispatcher.git ~/.codex/skills-auto-dispatcher
bash ~/.codex/skills-auto-dispatcher/scripts/scan-skills.sh \
  | python3 ~/.codex/skills-auto-dispatcher/scripts/update-skills-index.py
```

Auto-trigger：在项目根目录 `AGENTS.md` 加一行：

```markdown
任务进来先跑 route-task.py，有匹配就告诉我该用哪个 skill，我来手动调。
```

### Codex Web

在线版不能跑 bash，按这个流程：

1. Clone 仓库到本地
2. 本地跑 `scan-skills.sh | update-skills-index.py` 生成 `skills-index.json`
3. 把整个 `skills-auto-dispatcher/` 文件夹上传到 Codex Web 的知识库
4. 告诉 Codex Web："遇到任务先读 skills-index.json 找匹配的 skill，找到就读对应的 SKILL.md 来执行"

### OpenClaw

```bash
git clone https://github.com/YiYiii-Zhang/skills-auto-dispatcher.git /path/to/openclaw/plugins/skills-auto-dispatcher
bash /path/to/openclaw/plugins/skills-auto-dispatcher/scripts/scan-skills.sh \
  | python3 /path/to/openclaw/plugins/skills-auto-dispatcher/scripts/update-skills-index.py
```

如果 OpenClaw 有自定义指令文件，加入类似 auto-trigger 的规则。

### Copilot CLI

```bash
git clone https://github.com/YiYiii-Zhang/skills-auto-dispatcher.git ~/.github/skills-auto-dispatcher
bash ~/.github/skills-auto-dispatcher/scripts/scan-skills.sh \
  | python3 ~/.github/skills-auto-dispatcher/scripts/update-skills-index.py
```

Auto-trigger：在 `.github/copilot-instructions.md` 加：

```markdown
收到任务时先跑 python3 ~/.github/skills-auto-dispatcher/scripts/route-task.py "<task>"，
有 >= 0.3 的匹配就把对应 SKILL.md 读出来按指示操作。
```

## 手动使用

```bash
# 1. 构建索引
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py

# 2. 路由任务
python3 scripts/route-task.py "做一个CSS动画"
```

输出：

```json
{
  "matches": [
    {"skill": "css-animations", "score": 0.85, "reason": "matched animation keywords"}
  ],
  "tie": false,
  "subtasks": [],
  "decompose": false
}
```

## 路由决策

| 分数 | 动作 |
|------|------|
| >= 0.3 | 自动调用 Skill（Claude Code）/ 推荐给用户（其他平台）|
| < 0.3 | 没有匹配的 skill，直接处理 |
| 平局 | 两个 skill 同分，让用户选 |
| 拆解 | split 成子任务，各自独立路由 |
| 空匹配 | 无任何匹配，走通用推理 |

## 扩展词库

Dispatcher 内置了 150+ 中文词到英文关键词的映射。如果你用的领域词没覆盖到，用自然语言说：

> "部署前" 和 "灰度发布" 这些词帮我加到词库里

AI 助手会自动编辑 `custom-cn-mappings.json` 追加映射。不需要你手动写 JSON。

## 依赖

- bash
- python3（纯 stdlib，无需 pip 安装）

## 文件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 入口，触发条件描述 |
| `dispatcher.md` | 完整决策流程 |
| `task-router.md` | 匹配算法和阈值说明 |
| `execution-policy.md` | 失败处理、回退链、超时 |
| `scripts/scan-skills.sh` | 发现所有 SKILL.md，输出 JSON |
| `scripts/update-skills-index.py` | 构建/更新 skills-index.json |
| `scripts/route-task.py` | 对任务评分，建议匹配 |
| `custom-cn-mappings.json` | 用户自定义中文映射词库 |

## 维护

```bash
# 安装新 skill 后重建索引
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py

# 验证
python3 scripts/route-task.py "debug my failing test"
```
