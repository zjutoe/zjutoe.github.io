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

## 数学公式

文章模板已加载 MathJax，所有文章默认支持 LaTeX 数学公式，无需额外的 front matter 配置或 Jekyll 插件。

本项目使用 kramdown：**行内公式和独立公式都用 `$$` 包围**，由所在位置区分。行内公式写在段落中：

```markdown
质能方程为 $$E = mc^2$$，其中 $$m$$ 表示质量。
```

独立公式的起止 `$$` 各占一行，整个公式块前后留空行：

```markdown
下面是一个求和公式：

$$
S_n = \sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

多行对齐可使用 aligned 环境：

$$
\begin{aligned}
y &= xW + b \\
\mathcal{L} &= \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2
\end{aligned}
$$
```

直接在正文中写公式，不要包在反引号或代码块里；上面的代码块仅用于展示源码。不要用单个 `$...$` 或直接写 `\(...\)`、`\[...\]` 替代此处的写法，后两者的反斜杠会被 Markdown 转义处理。行内公式中的绝对值或范数请用 `\lvert x\rvert`、`\lVert x\rVert`，避免 `|` 被当成表格分隔符。

公式在浏览器中由 MathJax 渲染，需要启用 JavaScript 并能访问 jsDelivr CDN。请以本地 Jekyll 预览或发布后的博客页面为准，GitHub 仓库的 Markdown 预览使用不同的渲染规则。

参考：[kramdown 公式语法](https://kramdown.gettalong.org/syntax.html#math-blocks)、[MathJax 加载方式](https://docs.mathjax.org/en/latest/web/start.html)。

## 调整样式

- `_config.yml`：站点名称、简介和地址。
- `assets/css/style.css`：单栏宽度、字体、间距和代码样式。
- `_layouts/`：基础页面与文章模板。

## 本地预览

安装 Ruby 与 Jekyll 后，在项目目录运行 `jekyll serve`，打开 `http://localhost:4000`。
