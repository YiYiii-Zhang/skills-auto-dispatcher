#!/usr/bin/env python3
"""
Build or update skills-index.json from scan output.

Usage:
  bash scan-skills.sh | python3 update-skills-index.py [--force]
  python3 update-skills-index.py --help

No pip dependencies -- stdlib only.
"""

import json
import sys
import os
import re
from datetime import datetime, timezone, timedelta

STOP_WORDS = {
    "the", "a", "an", "when", "use", "for", "this", "that", "with",
    "from", "your", "will", "have", "been", "can", "how", "what",
    "why", "who", "and", "or", "not", "but", "if", "then", "else",
    "in", "on", "at", "to", "of", "by", "is", "it", "its", "be",
    "as", "are", "was", "were", "has", "had", "do", "does", "did",
    "should", "would", "could", "may", "might", "shall", "must",
    "you", "we", "he", "she", "they", "me", "us", "him", "her",
    "them", "my", "our", "his", "their", "all", "any", "each",
    "every", "both", "few", "more", "most", "other", "some",
    "such", "no", "only", "own", "same", "so", "than", "too",
    "very", "just", "about", "also", "into", "over", "after",
    "before", "between", "under", "again", "further", "once",
    "here", "there", "which", "these", "those",
}

CATEGORY_KEYWORDS = {
    "video": ["video", "composition", "scene", "transition", "render",
              "caption", "subtitle", "voiceover", "audio", "tts", "transcribe",
              "overlay", "narration", "footage", "clip"],
    "animation": ["animation", "anime", "gsap", "lottie", "css-animation",
                  "waapi", "keyframe", "timeline", "easing", "motion", "tween"],
    "web": ["website", "url", "capture", "screenshot", "page", "browser",
            "fetch", "html", "css", "dom", "http"],
    "dev": ["build", "deploy", "test", "debug", "review", "refactor",
            "commit", "branch", "merge", "code", "api", "function"],
    "data": ["database", "sql", "query", "schema", "migrate", "data"],
    "config": ["config", "settings", "install", "uninstall", "permission",
               "hook", "env", "environment"],
}


def has_chinese(text):
    return bool(re.search(r'[一-鿿]', text))


CN_STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
    "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
    "那", "哪", "吗", "吧", "呢", "啊", "哦", "为", "什么", "怎么",
    "这个", "那个", "可以", "需要", "应该", "已经", "还是", "或者",
    "然后", "所以", "因为", "但是", "如果", "虽然", "而且", "不过",
    "一下", "一些", "有点", "用", "给", "让", "把", "被",
    "从", "对", "请", "帮", "想", "做", "来", "去", "能",
}

CN_EN_MAP = {
    "视频": ["video", "composition", "render"],
    "动画": ["animation", "animate", "motion"],
    "字幕": ["caption", "subtitle"],
    "语音": ["voiceover", "tts", "speech"],
    "旁白": ["narration", "voiceover"],
    "音频": ["audio", "music"],
    "转录": ["transcribe", "transcription"],
    "背景": ["background", "overlay"],
    "去背景": ["remove-background"],
    "过渡": ["transition"],
    "转场": ["transition", "scene"],
    "场景": ["scene"],
    "渲染": ["render", "preview"],
    "网站": ["website", "url", "page"],
    "网址": ["url", "website", "capture"],
    "截图": ["screenshot", "capture"],
    "抓取": ["capture", "fetch"],
    "捕捉": ["capture"],
    "网页": ["website", "page", "html"],
    "链接": ["url", "link"],
    "图片": ["image", "picture", "photo"],
    "图像": ["image", "picture"],
    "照片": ["photo", "picture"],
    "压缩": ["compress", "optimize", "minify"],
    "裁剪": ["crop", "resize", "trim"],
    "缩放": ["scale", "resize", "zoom"],
    "文件": ["file", "document"],
    "保存": ["save", "export", "write"],
    "读取": ["read", "load", "open"],
    "写入": ["write", "save"],
    "删除": ["delete", "remove"],
    "复制": ["copy", "clone", "duplicate"],
    "移动": ["move", "rename", "transfer"],
    "重命名": ["rename"],
    "目录": ["directory", "folder"],
    "文件夹": ["folder", "directory"],
    "路径": ["path", "route"],
    "格式": ["format", "convert"],
    "数据库": ["database", "sql"],
    "查询": ["query", "search"],
    "优化": ["optimize", "tune"],
    "表": ["table", "schema"],
    "字段": ["column", "field"],
    "索引": ["index"],
    "数据": ["data", "dataset"],
    "迁移": ["migrate", "migration"],
    "备份": ["backup", "dump", "restore"],
    "恢复": ["restore", "recover"],
    "文档": ["document", "doc", "file"],
    "报告": ["report", "export", "generate"],
    "导出": ["export", "generate", "output"],
    "生成": ["generate", "create", "build"],
    "模板": ["template", "scaffold", "boilerplate"],
    "PDF": ["pdf", "document", "export"],
    "表格": ["table", "spreadsheet", "grid"],
    "图表": ["chart", "graph", "diagram"],
    "CSS": ["css", "style", "animation"],
    "代码": ["code", "script"],
    "接口": ["api"],
    "安装": ["install", "add"],
    "卸载": ["uninstall", "remove"],
    "调试": ["debug", "troubleshoot"],
    "检查": ["inspect", "lint", "validate"],
    "构建": ["build", "deploy"],
    "部署": ["deploy", "deployment", "release", "ship"],
    "发布": ["release", "deploy", "publish", "launch"],
    "测试": ["test"],
    "修复": ["fix", "debug"],
    "审查": ["review", "audit"],
    "重构": ["refactor"],
    "脚本": ["script", "bash", "shell"],
    "命令": ["command", "cli", "cmd"],
    "编译": ["compile", "build"],
    "网络": ["network", "http", "request"],
    "请求": ["request", "fetch", "call"],
    "响应": ["response", "result"],
    "上传": ["upload", "send"],
    "下载": ["download", "fetch", "get"],
    "发送": ["send", "push", "post"],
    "接收": ["receive", "get", "fetch"],
    "API": ["api", "endpoint", "interface"],
    "文字": ["text", "caption"],
    "文本": ["text", "content", "string"],
    "搜索": ["search", "find", "query"],
    "替换": ["replace", "substitute"],
    "翻译": ["translate", "translation", "i18n"],
    "正则": ["regex", "pattern"],
    "匹配": ["match", "pattern", "filter"],
    "格式化": ["format", "prettify", "beautify"],
    "解析": ["parse", "decode", "extract"],
    "标题": ["title", "heading"],
    "高亮": ["highlight", "marker"],
    "标注": ["annotation", "marker"],
    "邮件": ["email", "mail", "smtp"],
    "通知": ["notification", "notify", "alert"],
    "消息": ["message", "msg", "chat"],
    "加密": ["encrypt", "encryption", "crypto"],
    "解密": ["decrypt", "decode"],
    "安全": ["security", "secure", "auth"],
    "密钥": ["key", "secret", "token"],
    "登录": ["login", "auth", "signin"],
    "注册": ["register", "signup", "create"],
    "权限": ["permission"],
    "配置": ["config", "settings"],
    "设置": ["settings", "config"],
    "环境": ["environment", "env"],
    "变量": ["variable", "var", "env"],
    "日志": ["log", "logging", "trace"],
    "错误": ["error", "exception", "bug"],
    "性能": ["performance", "optimize", "speed"],
    "缓存": ["cache"],
    "进程": ["process", "task", "job"],
    "定时": ["cron", "schedule", "timer"],
    "钩子": ["hook"],
    "创建": ["create", "new", "make"],
    "更新": ["update", "modify", "change"],
    "查看": ["view", "show", "display", "list"],
    "编辑": ["edit", "modify", "change"],
    "分析": ["analyze", "analysis", "inspect"],
    "监控": ["monitor", "watch", "observe"],
    "统计": ["stats", "statistics", "analytics"],
    "排版": ["layout", "composition"],
    "设计": ["design", "style"],
    "调度": ["dispatch", "route", "schedule"],
    "验证": ["validate", "verify", "check"],
    "技能": ["skill", "capability"],
    "长图": ["image", "screenshot", "capture"],
    "图文": ["image", "text", "document"],
    "资料": ["data", "source", "reference"],
    "日报": ["report", "daily", "generate"],
    "映射": ["mapping", "map", "transform"],
    "页面": ["page", "website", "web"],
    "前端": ["frontend", "web", "ui"],
    "后端": ["backend", "server", "api"],
    "界面": ["ui", "interface", "page"],
}


def extract_keywords(text):
    """Extract meaningful keywords from description text."""
    text_lower = text.lower()
    tokens = re.findall(r'[a-z0-9_-]+', text_lower)
    tokens = [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]

    if has_chinese(text):
        for word, en_words in CN_EN_MAP.items():
            if word in text:
                tokens.extend(en_words)

    return list(dict.fromkeys(tokens))


def detect_category(keywords):
    """Detect category by keyword overlap."""
    scores = {}
    kwset = set(keywords)
    for cat, ckw in CATEGORY_KEYWORDS.items():
        hits = len(kwset & set(ckw))
        if hits > 0:
            scores[cat] = hits
    if scores:
        return max(scores, key=scores.get)
    return "general"


def detect_cross_refs(description):
    """Detect cross-references to other skills."""
    refs = []
    patterns = [
        r'see the (\S+) skill',
        r'use (\S+) instead',
        r'requires (\S+)',
        r'load the (\S+) skill',
        r'references?:?\s*(\S+)',
        r'related:?\s*(\S+)',
    ]
    for pat in patterns:
        for m in re.findall(pat, description, re.IGNORECASE):
            name = m.strip().rstrip('.')
            if name not in refs and len(name) > 1:
                refs.append(name)
    return refs


def detect_platforms(description):
    """Detect if skill is Claude-specific or portable."""
    claude_tools = ["Skill", "TaskCreate", "TaskUpdate", "TodoWrite",
                    "Bash", "Write", "Edit", "Read", "Glob", "Grep"]
    if any(tool in description for tool in claude_tools):
        return ["claude-code"]
    return ["any"]


def build_index(skills_data, existing_index=None):
    """Build the full index from scan data."""
    existing_skills = {}
    overrides = {}
    if existing_index:
        existing_skills = existing_index.get("skills", {})
        overrides = existing_index.get("_overrides", {})

    skills = {}
    for entry in skills_data:
        name = entry["name"]
        desc = entry.get("description", "")
        keywords = extract_keywords(desc)

        # Apply manual overrides if present
        if name in overrides:
            ov = overrides[name]
            if "trigger_keywords" in ov:
                keywords = ov["trigger_keywords"]

        prev = existing_skills.get(name, {})

        skills[name] = {
            "name": name,
            "path": entry["path"],
            "description": desc[:200],
            "trigger_keywords": keywords,
            "category": detect_category(keywords),
            "cross_refs": detect_cross_refs(desc),
            "platforms": detect_platforms(desc),
            "hash": entry.get("hash", ""),
            "stale": False,
        }

    # Mark removed skills as stale
    if existing_skills:
        for name, data in existing_skills.items():
            if name not in skills and data.get("stale"):
                # Was stale last cycle -- remove it now
                pass
            elif name not in skills:
                # First time missing -- mark stale
                data["stale"] = True
                skills[name] = data

    # Derive scan paths from raw data (before dedup) so all sources appear
    scan_paths = sorted(set(
        os.path.dirname(os.path.dirname(e["path"]))
        for e in skills_data
    ))

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "scan_paths": scan_paths,
        "total_skills": len([s for s in skills.values() if not s.get("stale")]),
        "_overrides": overrides,
        "skills": skills,
    }


def main():
    force = "--force" in sys.argv
    output_path = os.path.join(os.path.dirname(__file__), "..", "skills-index.json")

    # Always rebuild to detect stale/removed skills

    # Read scan data from stdin
    try:
        scan_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON from scan: {e}", file=sys.stderr)
        return 1

    # Load existing index for merging
    existing = None
    if os.path.exists(output_path):
        try:
            with open(output_path) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    index = build_index(scan_data, existing)

    with open(output_path, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    active = sum(1 for s in index["skills"].values() if not s.get("stale"))
    stale = sum(1 for s in index["skills"].values() if s.get("stale"))
    print(f"Index written: {active} active, {stale} stale", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
