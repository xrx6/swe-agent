# swe-agent

基于大语言模型的 AI Agent 学习与实验仓库,围绕工具调用(Tool Use)、Agent 循环、环境交互等方向做渐进式实验与项目实践。

## 目录结构

```
experiments/     实验代码,每个实验独立成文件
project/         主项目(factcheck-agent:自研事实核查 Agent)
notes/           学习笔记
CHANGELOG.md     改动记录
```

## 环境要求

- Python 3.10+
- 依赖安装:`pip install openai`

## 快速开始

1. 复制 `.env.example` 为 `.env`(已被 .gitignore 排除,不入仓库),填入你的密钥:

   ```
   GLM_API_KEY=your-api-key
   ```

2. 运行实验:

   ```bash
   python experiments/my-agent.py
   ```

## 当前进度

- **my-agent.py** —— Agent 基础工具集:模型对话封装、Shell 命令执行、文件读写、代码内搜索
