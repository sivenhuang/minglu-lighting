# Google Ads + GA4 追踪配置指引

> 更新日期：2026-10-27
> 适用账号：Google Ads `527-797-8483`（AW-18267116692） / GA4 `G-543007082`

---

## 一、当前追踪结构

| 层 | 标识 | 位置 | 作用 |
|---|---|---|---|
| GA4 属性 | `G-543007082` | 全站 147 页 | 行为分析、关键事件、跨渠道归因 |
| Ads 标签 | `AW-18267116692` | 全站 147 页 | 广告点击归因（GCLID） |
| Ads 转化 ID | `AW-18267116692/ONaACOu2sswcEJSpuIZE` | `main.js` | 询盘转化上报目标 |
| 转化事件（GA4） | `generate_lead` | `main.js` 全局委托 + contact.html + thank-you.html | 询盘关键事件 |
| 转化事件（Ads） | `conversion` | 同上 | web 标签直发转化 |

### 询盘转化触发点
1. **任意 WhatsApp 链接点击**
   - `main.js` 全局事件委托（`a[href*="wa.me"]`）→ 覆盖 142 个加载 main.js 的页面，含动态生成的产品卡片按钮。
   - `lp/` 5 个落地页为独立模板（不加载 main.js），各自内联一份等价监听，监听其 3 个 WhatsApp 链接。
2. **contact.html 表单提交** → `generate_lead`（category=form, label=project_inquiry）。
3. **thank-you.html 到达** → `generate_lead` + `conversion`，sessionStorage 防止刷新重复计数。
4. **lp/ 5 个落地页表单提交** → `generate_lead`（含隐藏 campaign 字段区分投放来源）。

### 防重复机制
- `main.js` 与 `lp/` 页均用 `sessionStorage['minglu_lead_fired']` 保证**同一会话只记一次**。
- 同一元素用 `__mingluLeadTracked` 标记，防止一次点击命中多个监听器。
- 跨会话的新访问仍计为新转化（用 sessionStorage 而非 localStorage 的原因）。

---

## 二、关键操作：避免 Ads 重复计数

改造后，**一次 WhatsApp 点击会同时产生**：
- GA4 的 `generate_lead` 事件
- Ads 的 `conversion` 事件（web 标签直发）

如果你在 Ads 后台把 GA4 关键事件也导入为转化，则同一次询盘会被计两次。
Google 官方明确要求避免此情况（来源：support.google.com/analytics/answer/11053134，
"为避免重复计算转化，请务必先停止对 Universal Analytics 转化出价，再开始对 GA4 转化出价"）。

### 推荐方案 A（当前默认，暂不导入 GA4 转化）
- Ads 端只保留 web 标签的 `conversion` 动作。
- GA4 的 `generate_lead` 仅用于 GA4 内部分析与受众再营销。
- **优点**：GCLID 归因最直接，转化量不被稀释。
- **适用**：现在即可用，无需改 Ads 后台。

### 方案 B（导入 GA4 关键事件为「主要」）
若你希望用 GA4 的跨渠道归因（最终功劳模型）驱动 Smart Bidding：
1. Ads 后台 → 工具与设置 → 衡量 → 转化。
2. 找到 web 标签创建的 `conversion` 动作，**改为「次要」**（或移除）。
3. 新建转化操作 → 导入 → 选择 GA4 属性 `G-543007082` → 勾选 `generate_lead` → 导入。
4. 确认导入的 `generate_lead` 被标为「主要」。
5. **在同一个工作会话内完成上述两步**，官方建议如此以避免数据缺口。

> 官方同时说明：GA4 现在使用「最终功劳」导出模型，与旧版 UA 的「最终非直接点击」不同，
> 导入后转化次数可能与原 web 标签计数有差异，这是归因模型变化导致，非埋点错误。

---

## 三、待办清单

| # | 事项 | 责任方 | 状态 |
|---|---|---|---|
| 1 | GA4 中把 `generate_lead` 标记为「关键事件」 | 你（GA4 后台） | 待办 |
| 2 | Ads 后台确认 `conversion` 动作设为「主要」 | 你（Ads 后台） | 待办 |
| 3 | Ads 后台关联 GA4 属性作为转化来源 | 你（Ads 后台） | 待办 |
| 4 | 确认 Ads 自动标记已开启 | 你（Ads 后台） | 待办 |
| 5 | Search Console Service Account 凭证配置 | 你 + 我 | 待办（见 submit-to-google.py 头部说明） |

---

## 四、验证方法

### GA4 侧
GA4 → 报告 → 实时 → 访问网站并点击任意 WhatsApp 按钮，
应看到 `generate_lead` 事件（category=engagement, label=whatsapp_click, value=1）。

### Ads 侧
Ads → 工具与设置 → 衡量 → 转化 → 标签，检查 `AW-18267116692` 状态为「正在收集」。
用 Tag Assistant 扩展确认 gtag.js 正常加载、无报错。

### 代码侧自检命令
```bash
# 确认全站 main.js 版本一致（应为 142 处 v=5）
grep -rhoE 'main\.js\?v=[0-9]+' --include="*.html" . | sort | uniq -c

# 确认全站 Ads + GA4 标签齐备（应各 147）
grep -rl "AW-18267116692" --include="*.html" . | wc -l
grep -rl "G-543007082"  --include="*.html" . | wc -l

# 确认旧 GA4 属性已清零（应为 0）
grep -rl "G-94KWTC5HK4" --include="*.html" . | wc -l
```

---

## 五、来源

- Google Ads 转化追踪原理与前置条件：support.google.com/google-ads/answer/7521212
- 网站级代码排障（Cookie、GCLID、iframe 禁用等）：support.google.com/google-ads/answer/9148089
- GA4 转化导入 Ads 与重复计数防范：support.google.com/analytics/answer/11053134
- GA4 与 UA 转化差异原因（最终功劳模型）：support.google.com/analytics/answer/13672281
