<!--
关于
codex-lb 的社区分支，提供 ChatGPT 账户池、代理路由和用量追踪；独立验证仍在进行。

主题
python oauth sqlalchemy dashboard load-balancer openai rate-limit api-proxy codex fastapi usage-tracking chatgpt opencode
-->

# codex-lb

![codex-lb](docs/screenshots/banner.jpg)

[English](./README.md) | **简体中文**

> **本分支文档（英文）**: [docs/](docs/index.md)；[上游文档](https://soju06.github.io/codex-lb/)可能不包含本分支修改。本页可能滞后，安装请以本分支指南为准。

ChatGPT 账户负载均衡器。聚合多个账户、追踪用量、管理 API Key，所有内容在仪表盘中查看。

**分支指南: [Docker](docs/deployment/docker.md)** · [独立审计](issues-check.md)仍在进行，历史发布包不包含所有后续源码修复。

## 功能特性

<table>
<tr>
<td><b>账户池化</b><br>在多个 ChatGPT 账户之间负载均衡</td>
<td><b>用量追踪</b><br>按账户记录 token、成本及 28 天趋势</td>
<td><b>API Key</b><br>按 token、成本、时间窗口、模型限流</td>
</tr>
<tr>
<td><b>仪表盘鉴权</b><br>密码 + 可选 TOTP</td>
<td><b>OpenAI 兼容</b><br>支持 Codex CLI、OpenCode 及任意 OpenAI 客户端</td>
<td><b>模型自动同步</b><br>从上游拉取可用模型列表</td>
</tr>
</table>

| ![dashboard](docs/screenshots/dashboard.jpg) | ![accounts](docs/screenshots/accounts.jpg) |
|:---:|:---:|

## 快速开始

以下为 Bash 命令；Windows PowerShell 请参见 [Docker](docs/deployment/docker.md#basic-run) 或 [Python](docs/deployment/python.md#run-from-a-fork-checkout) 指南。选择一种安装方式。

```bash
# Docker（在 Frozen811/codex-lb 仓库目录中运行；参见 docs/deployment/docker.md）
docker build -t codex-lb:local .
docker network inspect codex-lb-net >/dev/null 2>&1 || docker network create codex-lb-net
docker run -d --name codex-lb \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local

# 或者安装历史 fork wheel（版本差异及源码安装见 docs/deployment/python.md）
uvx --from https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl codex-lb

# 或者在 fork checkout 中使用 Nix（见 docs/deployment/nix.md）
nix run .
```

打开 [localhost:2455](http://localhost:2455) → 添加账户 → 完成。

首次远程访问仪表盘？需要一次性的 bootstrap token ——
参见 [快速上手](docs/getting-started.md)。

## 客户端配置

将任意 OpenAI 兼容客户端指向 codex-lb 即可。以 Codex CLI 为例，`~/.codex/config.toml`：

```toml
model = "gpt-6-astra"
model_reasoning_effort = "xhigh"
model_provider = "codex-lb"

[model_providers.codex-lb]
name = "openai"  # 必填 —— 启用远程 /responses/compact。自 Codex 2026-05-23 起须为小写；旧写法 "OpenAI" 无法解析 gpt-5.5
base_url = "http://127.0.0.1:2455/backend-api/codex"
wire_api = "responses"
supports_websockets = true
supports_standalone_web_search = true # 需要 codex-lb >= 1.22.0
requires_openai_auth = true # codex 应用需要
```

| Logo | 客户端 | 端点 | 指南 |
|---|--------|----------|-------|
| <img src="https://avatars.githubusercontent.com/u/14957082?s=200" width="32" alt="OpenAI"> | **Codex CLI / IDE** | `http://127.0.0.1:2455/backend-api/codex` | [客户端配置 → Codex CLI](docs/client-setup.md#codex-cli-ide-extension) |
| <img src="https://avatars.githubusercontent.com/u/66570915?s=200" width="32" alt="OpenCode (Anomaly)"> | **OpenCode** | `http://127.0.0.1:2455/v1` | [客户端配置 → OpenCode](docs/client-setup.md#opencode) |
| <img src="https://avatars.githubusercontent.com/u/252820863?s=200" width="32" alt="OpenClaw"> | **OpenClaw** | `http://127.0.0.1:2455/v1` | [客户端配置 → OpenClaw](docs/client-setup.md#openclaw) |
| <img src="https://avatars.githubusercontent.com/u/134168893?s=200" width="32" alt="Hermes Agent (Nous Research)"> | **Hermes Agent** | `http://127.0.0.1:2455/v1` | [客户端配置 → Hermes Agent](docs/client-setup.md#hermes-agent) |
| <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="32" alt="Python"> | **OpenAI Python SDK** | `http://127.0.0.1:2455/v1` | [客户端配置 → Python SDK](docs/client-setup.md#openai-python-sdk) |

远程客户端需要在仪表盘中创建的 [API Key](docs/api-keys.md)。

## 配置

通过 `CODEX_LB_` 前缀的环境变量或 `.env.local` 配置 —— 详见 [`.env.example`](.env.example) 与
[配置指南](docs/configuration.md)。默认数据库后端是 SQLite；
可选通过 `CODEX_LB_DATABASE_URL` 切换到 PostgreSQL。

## 数据

| 环境 | 路径 |
|-------------|------|
| 本地 / uvx | `~/.codex-lb/` |
| Docker | `/var/lib/codex-lb/` |

请备份此目录以保留你的数据。

## 文档

本分支英文文档位于 **[docs/](docs/index.md)**（包含 OpenSpec 链接）：

- [快速上手](docs/getting-started.md) —— 快速开始、远程访问 bootstrap token
- [客户端配置](docs/client-setup.md) —— Codex CLI、OpenCode、OpenClaw、Python SDK
- [配置](docs/configuration.md) —— 真正重要的少数设置项
- [鉴权](docs/authentication.md) —— 仪表盘鉴权模式
- [API Key](docs/api-keys.md) —— 保护代理路由
- [路由](docs/routing.md) —— 策略指南
- [数据库](docs/database.md) —— SQLite / PostgreSQL、Postgres 16 → 18 升级
- [部署](docs/deployment/docker.md) —— [Docker](docs/deployment/docker.md)、[Kubernetes](docs/deployment/kubernetes.md)、[远程访问](docs/deployment/remote.md)
- [故障排查](docs/troubleshooting.md)

### 社区伴生项目

由社区独立维护、消费仪表盘 API 的项目，不属于 codex-lb 本体
（访问指引见 [文档中的列表](docs/index.md#community-companions)）：

- [Codex LB Status Bar](https://github.com/sm1ee/codex-lb-statusbar) —— 原生 macOS 应用：账户状态、配额详情、账户控制
- [codex-lb SwiftBar](https://github.com/joschi655/codex-lb-swiftbar) —— 只读的 SwiftBar/Bun 监控器，显示账户池状态与配额余量

## 开发

```bash
# Docker
docker compose watch

# 本地
uv sync && cd frontend && bun install && cd ..
uv run codex-lb                              # 后端 :2455
cd frontend && bun run dev                   # 前端 :5173

# Nix
nix run .
nix develop # 进入开发环境
```

## 贡献者 ✨

完整的贡献者名单请参见英文 [README](./README.md#contributors-) 中由 [all-contributors](https://github.com/all-contributors/all-contributors) 自动生成的列表（该列表由机器人维护，仅写入 `README.md`）。该项目欢迎任何形式的贡献！
