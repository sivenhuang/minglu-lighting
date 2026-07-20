# Minglu-Lighting 项目长期笔记

## 部署与托管架构（重要更正）
- **之前记录**：站点部署于 Cloudflare Pages。
- **实际架构**：源站托管在 **GitHub Pages**（A 记录指向 185.199.108.153，www CNAME 指向 sivenhuang.github.io）。
- **Cloudflare Pages 项目说明**：Cloudflare 后台 Workers & Pages 中有两个相关项目：
  - `minglu-lighting`（`minglu-lighting.pages.dev`）— **No Git connection**、34 天未更新。
  - `minglu-lighting-2`（`minglu-lighting-2.pages.dev`）— **No Git connection**、33 天未更新。
  - 两者**都不是当前线上站点**，也**没有与 GitHub 仓库关联**；请勿把代码部署或关联到这两个项目。minglulighting.com 的流量实际由 Cloudflare DNS 代理回源 GitHub Pages。
- **SSL/TLS 加密模式**：`Full`，由 Cloudflare 回源 GitHub Pages 的 HTTPS。

## Brotli 状态
- 2026-07-20 排查：DNS 记录原本为 DNS only，导致流量直接到 GitHub/Fastly，响应头无 `Content-Encoding`。
- 修复：将 `minglulighting.com` 的 A 记录和 `www.minglulighting.com` 的 CNAME 记录均改为 **Proxied**（橙色云）。
- 验证：Bash `curl -H "Accept-Encoding: br"` 返回 `Server: cloudflare` + `Content-Encoding: br`，Brotli 已生效。Cloudflare Free 套餐下 Brotli 默认开启，无需额外设置。
