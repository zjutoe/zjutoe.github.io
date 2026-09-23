# Toe's blog

简洁的 Jekyll 技术博客，使用 GitHub Pages 构建，无需前端构建工具。

## 写文章

每篇文章的中英文版本分别保存为 `.md`，通过相同的 `translation_key` 关联。例如：

```text
_posts/
  2026-09-17-first-note-zh.md
  2026-09-17-first-note-en.md
```

中文版：

```markdown
---
title: 第一篇技术笔记
description: 文章的简短介绍。
lang: zh-CN
translation_key: first-note
category: notes
permalink: /posts/first-note/
---

正文使用 Markdown，支持标题、列表、代码块、图片和表格。
```

英文版：

```markdown
---
title: My First Technical Note
description: A short description of the article.
lang: en
translation_key: first-note
category: notes
permalink: /en/posts/first-note/
---

Write the English article here.
```

- 每个版本都必须填写 `title`、`lang`、`translation_key`、`category` 和 `permalink`；`description` 可选。
- `translation_key` 是文章的稳定标识，同一篇文章的两个版本必须一致，不同文章不能复用。同一标识下，每种语言只能有一个版本。
- 目前支持 `zh-CN` 和 `en`。两个版本使用相同的文件名日期（原文发布日期），翻译或修订时保留该日期，避免改变首页排序。
- 中文 URL 使用 `/posts/<slug>/`，英文使用 `/en/posts/<slug>/`。URL 必须唯一；已有文章保留原文件名和 URL，不需要添加 `-zh` 后缀。
- 首页按日期倒序排列，每篇文章只出现一次，优先显示中文标题，并列出已有版本的语言入口。只有一个版本时只显示该版本，不生成空的翻译链接。
- 文章页可直接切换到另一语言版本；页面自动设置语言、自身的 canonical URL 和现有版本之间的 `hreflang` 关联。

正文默认使用文章排版，未来日期的文章默认不显示。以中文为主要写作版本，英文保存为完整译文；修改论点、代码、公式或研究状态时同步更新两个版本。图片共用 `assets/` 下的资源，使用站点根路径；指向其他代码库文档的链接使用完整的 GitHub URL。

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
- `_includes/post-languages.html`：首页和文章页共用的语言入口。
- `_data/languages.yml`：语言名称和导航文案。

## 文章留言

文章模板使用 [giscus](https://giscus.app/zh-CN)，留言存储在 GitHub Discussions 中。读者登录 GitHub 并授权 giscus 后可以评论、回复和添加表情回应。

首次启用：

1. 在[仓库设置](https://github.com/zjutoe/zjutoe.github.io/settings)的 Features 中启用 Discussions。
2. 安装 [giscus GitHub App](https://github.com/apps/giscus)，授权 `zjutoe.github.io` 仓库。
3. 在 [giscus 配置页](https://giscus.app/zh-CN)填写 `zjutoe/zjutoe.github.io`，选择 `Announcements`（公告类型）分类。
4. 将生成代码中的 `data-repo-id`、`data-category` 和 `data-category-id` 对应填入 `_config.yml` 的 `giscus.repo_id`、`giscus.category` 和 `giscus.category_id`，再将 `giscus.enabled` 设为 `true`。这些 ID 是公开配置，无需填写 token 或密钥。
5. 构建并发布网站后，打开文章页检查留言区。第一条评论或回应会自动创建对应的 discussion。

留言区位于文章正文下方，使用与博客一致的浅色主题并延迟加载，界面语言随文章切换。页面以 `translation_key` 作为讨论标识，并启用严格匹配，因此中英文版本共享留言，修改标题或 URL 不会新建讨论。发布后保持 `translation_key` 稳定且每篇文章唯一。

可在 [Discussions](https://github.com/zjutoe/zjutoe.github.io/discussions) 中管理留言。将 `giscus.enabled` 设为 `false` 可隐藏全站留言区，已有讨论仍保留在 GitHub。

## 专栏分类

每篇 `category` 只能填一个值，归入一个专栏：

| 值 | 专栏 | 栏目页 URL |
|---|---|---|
| `research` | 研究探索 | /research/ |
| `notes` | 学习笔记 | /notes/ |
| `review` | 技术评论 | /review/ |

同一 `translation_key` 的两个版本必须填同一个 `category`。检查脚本（校验 `category` 必填、取值合法、同 `translation_key` 一致）：

```bash
python3 .github/scripts/check_posts.py
```

依赖 PyYAML（`pip install pyyaml`）。

## 本地预览

安装 Ruby 与 Jekyll 后，在项目目录运行 `jekyll serve`，打开 `http://localhost:4000`。
