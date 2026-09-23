# 测试用本地语言模型写代码效果
- 自Codex发布5.6、6模型以来，token消耗太快了
- QWen-3.8 27B模型效果还行
- PrimML Bonsai-2 27B模型的效果也还行
- codig任务：[KMesh](https://github.com/zjutoe/KMesh.git)

# 任务评测方法
- 用codex 6 (xhigh) 做任务规划，写好handoff文档
- 本地模型（QWen或Bonsai）根据handoff文档执行，并根据要求自行检验
- codex审核本地模型的执行结果，需要返工时给出提示
- 需要返工时把codex的审核结果贴给本地模型
- 直到codex审核任务通过
- 让codex评估整轮下来，本地模型的任务执行完整性、正确性

# QWen评测结果

![QWen评测结果](assets/images/qwen_estimage.png)

# Bonsai评测结果

![Bonsai评测结果](assets/images/bonsai_estimage.png)
