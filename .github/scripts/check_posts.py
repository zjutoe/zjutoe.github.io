#!/usr/bin/env python3
"""检查所有 `_posts/*.md` 文件的 frontmatter：

- `category` 必填，取值必须是 {research, notes, review} 之一；
- 同一 `translation_key` 下各版本 `category` 必须一致。

用法：python3 .github/scripts/check_posts.py
依赖：PyYAML（pip install pyyaml）。
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("error: PyYAML 缺失，请先执行 `pip install pyyaml`")


ALLOWED_CATEGORIES = {"research", "notes", "review"}
FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def load_posts(posts_dir):
    if not posts_dir.exists():
        raise SystemExit(f"error: 目录 {posts_dir} 不存在")
    posts = []
    for path in sorted(posts_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            raise SystemExit(f"error: {path.name}: 无 frontmatter 块")
        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            raise SystemExit(f"error: {path.name}: frontmatter YAML 解析失败: {exc}")
        if not isinstance(frontmatter, dict):
            raise SystemExit(f"error: {path.name}: frontmatter 不是 mapping")
        posts.append((path, frontmatter))
    return posts


def main():
    posts_dir = Path(__file__).resolve().parents[2] / "_posts"
    posts = load_posts(posts_dir)

    errors = []
    for path, frontmatter in posts:
        category = frontmatter.get("category")
        if not isinstance(category, str) or not category:
            errors.append(f"{path.name}: 缺少必填字段 `category`")
        elif category not in ALLOWED_CATEGORIES:
            errors.append(
                f"{path.name}: category {category!r} 非法，"
                f"允许的值为 {' '.join(sorted(ALLOWED_CATEGORIES))}"
            )

    by_key = {}
    for path, frontmatter in posts:
        key = frontmatter.get("translation_key")
        if key:
            by_key.setdefault(key, []).append((path.name, frontmatter.get("category")))
    for key, entries in sorted(by_key.items()):
        # 仅纳入通过类型校验（字符串且取值合法）的值做一致性比较，避免异常值（如列表）触发 TypeError
        categories = {c for _, c in entries if isinstance(c, str) and c in ALLOWED_CATEGORIES}
        if len(categories) > 1:
            errors.append(
                f"translation_key {key!r}: 同一篇文章不同版本的 "
                f"category 不一致: {sorted(categories)}"
            )

    if errors:
        for error in errors:
            print(f"x {error}", file=sys.stderr)
        print(f"已检查 {len(posts)} 篇 post，发现 {len(errors)} 个错误，退出码 1")
        raise SystemExit(1)
    print(f"ok: {posts_dir} 下 {len(posts)} 篇 post 全部通过检查")


if __name__ == "__main__":
    main()
