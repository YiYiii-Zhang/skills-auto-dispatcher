#!/usr/bin/env python3
"""
Score a task description against the skills index and suggest matches.

Usage:
  python3 route-task.py "task description here"
  echo "task description" | python3 route-task.py

No pip dependencies -- stdlib only.
"""

import json
import sys
import os
import re

STOP_WORDS = {
    "the", "a", "an", "when", "use", "for", "this", "that", "with",
    "from", "your", "will", "have", "been", "can", "how", "what",
    "why", "who", "and", "or", "not", "but", "if", "then", "else",
    "in", "on", "at", "to", "of", "by", "is", "it", "its", "be",
    "as", "are", "was", "were", "has", "had", "do", "does", "did",
}

CN_STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
    "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
    "那", "哪", "吗", "吧", "呢", "啊", "哦", "为", "什么", "怎么",
    "这个", "那个", "可以", "需要", "应该", "已经", "还是", "或者",
    "然后", "所以", "因为", "但是", "如果", "虽然", "而且", "不过",
    "一下", "一些", "有点", "一下", "用", "给", "让", "把", "被",
    "从", "对", "请", "帮", "想", "做", "来", "去", "能",
}

# Chinese keyword -> English equivalents bridge
CN_EN_MAP = {
    # --- 视频/动画 ---
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
    # --- 网站 ---
    "网站": ["website", "url", "page"],
    "网址": ["url", "website", "capture"],
    "截图": ["screenshot", "capture"],
    "抓取": ["capture", "fetch"],
    "捕捉": ["capture"],
    "网页": ["website", "page", "html"],
    "链接": ["url", "link"],
    # --- 图片/图像 ---
    "图片": ["image", "picture", "photo"],
    "图像": ["image", "picture"],
    "照片": ["photo", "picture"],
    "压缩": ["compress", "optimize", "minify"],
    "裁剪": ["crop", "resize", "trim"],
    "缩放": ["scale", "resize", "zoom"],
    # --- 文件操作 ---
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
    # --- 数据库 ---
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
    # --- 文档/报告 ---
    "文档": ["document", "doc", "file"],
    "报告": ["report", "export", "generate"],
    "导出": ["export", "generate", "output"],
    "生成": ["generate", "create", "build"],
    "模板": ["template", "scaffold", "boilerplate"],
    "PDF": ["pdf", "document", "export"],
    "表格": ["table", "spreadsheet", "grid"],
    "图表": ["chart", "graph", "diagram"],
    # --- 代码/开发 ---
    "CSS": ["css", "style", "animation"],
    "代码": ["code", "script"],
    "接口": ["api"],
    "安装": ["install", "add"],
    "卸载": ["uninstall", "remove"],
    "调试": ["debug", "troubleshoot"],
    "检查": ["inspect", "lint", "validate"],
    "构建": ["build", "deploy"],
    "测试": ["test"],
    "修复": ["fix", "debug"],
    "审查": ["review", "audit"],
    "重构": ["refactor"],
    "脚本": ["script", "bash", "shell"],
    "命令": ["command", "cli", "cmd"],
    "编译": ["compile", "build"],
    # --- 网络/API ---
    "网络": ["network", "http", "request"],
    "请求": ["request", "fetch", "call"],
    "响应": ["response", "result"],
    "上传": ["upload", "send"],
    "下载": ["download", "fetch", "get"],
    "发送": ["send", "push", "post"],
    "接收": ["receive", "get", "fetch"],
    "API": ["api", "endpoint", "interface"],
    # --- 文本/搜索 ---
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
    # --- 邮件/通知 ---
    "邮件": ["email", "mail", "smtp"],
    "通知": ["notification", "notify", "alert"],
    "消息": ["message", "msg", "chat"],
    # --- 安全/认证 ---
    "加密": ["encrypt", "encryption", "crypto"],
    "解密": ["decrypt", "decode"],
    "安全": ["security", "secure", "auth"],
    "密钥": ["key", "secret", "token"],
    "登录": ["login", "auth", "signin"],
    "注册": ["register", "signup", "create"],
    "权限": ["permission"],
    # --- 系统/环境 ---
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
    # --- 通用操作 ---
    "创建": ["create", "new", "make"],
    "更新": ["update", "modify", "change"],
    "查看": ["view", "show", "display", "list"],
    "编辑": ["edit", "modify", "change"],
    "分析": ["analyze", "analysis", "inspect"],
    "监控": ["monitor", "watch", "observe"],
    "统计": ["stats", "statistics", "analytics"],
    "排版": ["layout", "composition"],
    "设计": ["design", "style"],
}

def load_custom_mappings():
    """Load user-defined CN→EN mappings from custom-cn-mappings.json.
    File should be next to this script, with format:
    {"中文词": ["english", "keywords"]}
    Returns a dict merged into CN_EN_MAP (user mappings override built-in).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    custom_path = os.path.join(script_dir, "..", "custom-cn-mappings.json")
    if not os.path.exists(custom_path):
        return {}
    try:
        with open(custom_path) as f:
            custom = json.load(f)
        if not isinstance(custom, dict):
            return {}
        return {k: v for k, v in custom.items() if isinstance(v, list)}
    except (json.JSONDecodeError, IOError):
        return {}

# Merge custom mappings on import
CN_EN_MAP = {**CN_EN_MAP, **load_custom_mappings()}

DECOMPOSE_SIGNALS = [
    r'\band\b', r'\bthen\b', r'\bafter\b', r'\balso\b',
    r'\bnext\b', r'\bfinally\b', r'\bfirst\b', r'\bsecond\b',
    r'\bthird\b', r'\d+\.', r'\bfollowed by\b',
]

CN_DECOMPOSE_SIGNALS = [
    r'然后', r'接着', r'之后', r'还有', r'另外',
    r'同时', r'并且', r'以及', r'\d+[\.、]',
    r'第一步', r'第二步', r'第三步',
]


def has_chinese(text):
    return bool(re.search(r'[一-鿿]', text))


def tokenize(text):
    text = text.lower()
    # For Chinese text, extract bigrams and unigrams
    if has_chinese(text):
        tokens = []
        for word, en_words in CN_EN_MAP.items():
            if word in text:
                tokens.extend(en_words)
        # Also extract English tokens from mixed text
        en_tokens = re.findall(r'[a-z0-9_-]+', text)
        tokens.extend(t for t in en_tokens if len(t) > 1 and t not in STOP_WORDS)
        return list(dict.fromkeys(tokens))
    else:
        tokens = re.findall(r'[a-z0-9_-]+', text)
        return [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]


def score_skill(task_tokens, skill):
    keywords = skill.get("trigger_keywords", [])
    if not keywords:
        return 0.0

    task_set = set(task_tokens)
    kw_set = set(k.lower() for k in keywords)

    matches = len(task_set & kw_set)
    # Score by task coverage: what fraction of the task's keywords does this skill cover?
    # This rewards focused tasks and avoids dilution from broad skill keyword lists.
    score = matches / max(len(task_set), 1)

    if skill["name"].lower() in " ".join(task_tokens):
        score += 0.2

    category = skill.get("category", "general")
    if category != "general" and category in task_tokens:
        score += 0.1

    cross_refs = skill.get("cross_refs", [])
    for ref in cross_refs:
        if ref.lower() in task_tokens:
            score -= 0.05

    return min(score, 1.0)


def detect_decomposition(task_text):
    signals_found = 0
    for pat in DECOMPOSE_SIGNALS:
        if re.search(pat, task_text, re.IGNORECASE):
            signals_found += 1
    for pat in CN_DECOMPOSE_SIGNALS:
        if re.search(pat, task_text):
            signals_found += 1
    return signals_found >= (1 if has_chinese(task_text) else 2)


def split_subtasks(task_text):
    if has_chinese(task_text):
        parts = re.split(r'[。；\n]', task_text)
        result = []
        for p in parts:
            sub = re.split(r'(?:然后|接着|之后|还有|另外|同时|并且|以及)', p)
            result.extend(s.strip() for s in sub if s.strip())
        deeper = []
        for r in result:
            sub2 = re.split(r'\s*\d+[\.、]\s*', r)
            deeper.extend(s.strip() for s in sub2 if s.strip())
        return [d for d in deeper if len(d) >= 6]
    else:
        subtasks = re.split(
            r'\s+(?:and|then|after that|also|next|finally|first|second|third)\s+',
            task_text, flags=re.IGNORECASE
        )
        result = []
        for st in subtasks:
            parts = re.split(r'\s*\d+\.\s*', st)
            result.extend(p.strip() for p in parts if p.strip())
        return [r for r in result if len(r.split()) >= 4]


def main():
    task = ""
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = sys.stdin.read().strip()

    if not task:
        print("Usage: route-task.py <task description>", file=sys.stderr)
        return 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "..", "skills-index.json")
    try:
        with open(index_path) as f:
            index = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print('{"error":"skills-index.json not found. Run scan-skills.sh | update-skills-index.py first"}')
        return 1

    task_tokens = tokenize(task)
    skills = index.get("skills", {})

    matches = []
    for name, skill in skills.items():
        if name == "skills-auto-dispatcher":
            continue
        if skill.get("stale"):
            continue
        s = score_skill(task_tokens, skill)
        if s > 0:
            matches.append({
                "skill": name,
                "score": round(s, 2),
                "reason": f"matched {skill.get('category', 'general')} keywords",
            })

    matches.sort(key=lambda x: x["score"], reverse=True)

    decompose = detect_decomposition(task)
    subtasks = []
    if decompose:
        raw_subtasks = split_subtasks(task)
        for st in raw_subtasks:
            st_tokens = tokenize(st)
            best_skill = None
            best_score = 0.0
            for name, skill in skills.items():
                if name == "skills-auto-dispatcher":
                    continue
                if skill.get("stale"):
                    continue
                s = score_skill(st_tokens, skill)
                if s > best_score:
                    best_score = s
                    best_skill = name
            subtasks.append({
                "text": st,
                "suggested_skill": best_skill,
                "score": round(best_score, 2),
            })

    output = {
        "matches": matches[:5],
        "subtasks": subtasks,
        "decompose": decompose,
        "language": "zh" if has_chinese(task) else "en",
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
