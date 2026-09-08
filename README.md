# Toe's blog

简洁的 Jekyll 技术博客，使用 GitHub Pages 构建，无需前端构建工具。

## 写文章

在 `_posts/` 下新建 `YYYY-MM-DD-slug.md`，例如 `_posts/2026-09-08-first-note.md`：

```markdown
---
title: 第一篇技术笔记
description: 文章的简短介绍。
---

正文使用 Markdown，支持标题、列表、代码块、图片和表格。
```

文章自动按日期倒序出现在首页，默认使用文章排版。文件名日期为发布日期，未来日期的文章默认不显示。

## 调整样式

- `_config.yml`：站点名称、简介和地址。
- `assets/css/style.css`：单栏宽度、字体、间距和代码样式。
- `_layouts/`：基础页面与文章模板。

## 本地预览

安装 Ruby 与 Jekyll 后，在项目目录运行 `jekyll serve`，打开 `http://localhost:4000`。
