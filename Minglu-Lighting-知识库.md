# Minglu Lighting — 项目知识库

> 创建：2026-06-14 | 更新：2026-06-14

---

## 📋 一、核心账号信息

| 项目 | 信息 |
|------|------|
| 🌐 域名 | **minglulighting.com**（Cloudflare 注册） |
| ☁️ Cloudflare | 账户国家设印尼（支付用印尼 Mastercard） |
| 📧 邮箱 | **minglulighting@gmail.com** |
| 📱 WhatsApp | **+86 18098910947** |
| 🏠 地址 | No.12, Xichong East Road, Henglan Town, Zhongshan City, Guangdong, China |
| 🐙 GitHub | https://github.com/sivenhuang/minglu-lighting |
| 🔑 GitHub 用户 | sivenhuang |

---

## 🌍 二、网站概览

**Minglu Lighting B2B 外贸网站** — 专业太阳能 & LED 户外照明

- **类型**：纯静态 HTML/CSS/JS（无需后端）
- **页面**：首页、产品列表、产品详情、关于我们、联系我们
- **产品数**：**136 个产品**，12 个分类
- **产品来源**：https://www.xiuben-donta.com（通过 Playwright 完整抓取）
- **图片**：热链自 `usimg.bjyyb.net/sites/63500/63544/`（无防盗链）
- **风格**：深色主题 + 绿色点缀(#22c55e) + 太阳能黄色高亮(#facc15)
- **语言**：英文（面向海外客户）
- **认证**：ISO 9001 · CE · RoHS

---

## 📂 三、产品分类（12类 / 136产品）

| 分类 | 数量 |
|------|------|
| Solar Street Light（太阳能路灯） | 54 |
| Solar Garden Light（太阳能庭院灯） | 22 |
| LED Flood Light（LED泛光灯） | 16 |
| Solar Lawn Light（太阳能草坪灯） | 9 |
| Solar Pillar Light（太阳能柱灯） | 9 |
| LED Street Light（LED路灯） | 9 |
| Solar Energy System（太阳能系统） | 6 |
| LED High Bay Light（LED工矿灯） | 4 |
| LED Fishing Light（LED捕鱼灯） | 3 |
| Solar Strip Light（太阳能灯带） | 2 |
| Solar Flood Light（太阳能泛光灯） | 1 |
| Solar Light Tower（太阳能灯塔） | 1 |

---

## 🛠️ 四、技术架构

### 文件结构
```
minglu-lighting/
├── index.html              # 首页（动画 hero + 分类卡片 + 精选产品）
├── products.html           # 产品列表（分类筛选 + 网格展示）
├── product.html            # 产品详情（图片轮播 + 参数 + WhatsApp 询价）
├── about.html              # 关于我们
├── contact.html            # 联系我们
├── assets/
│   ├── css/style.css       # 完整样式
│   ├── js/
│   │   ├── products-data.js  # 136 产品数据（核心数据文件）
│   │   └── main.js           # 所有 JS 逻辑
│   └── images/
│       ├── logo.jpg          # 公司 Logo（ML + 太阳光线）
│       └── hero-product.jpg  # 首页产品图
└── scrape-data-raw.json    # 原始抓取数据备份
```

### 产品数据结构（每个产品）
```javascript
{
  id: 'p1',                    // 唯一标识
  name: '产品名称',
  category: 'Solar Street Light',
  categorySlug: 'solar-street-light',
  description: '产品描述',
  image: '主图URL',             // galleryImages[0]
  galleryImages: [...],        // 轮播图数组
  detailImages: [...],         // 详情图数组
  sourceUrl: '源站URL',
  featured: true/false,        // 是否精选
  features: [...],             // 特性列表
  specs: {...},                // 规格参数
  powerOptions: [...],         // 可选功率
  applications: [...]          // 适用场景
}
```

---

## ⚠️ 五、重要经验和注意事项

### 图片抓取
- ❌ **不要用 WebFetch/urllib** 抓取 xiuben-donta.com 图片——网站使用 grey.png 懒加载
- ✅ **必须用 Playwright 无头浏览器**渲染页面后提取真实图片 URL
- 🚫 **必须过滤**：源站每个产品页都嵌入 LOGO 图（`20220909093134388.webp`）和认证标志图（`1764238157852610389645443072.webp`），需从 galleryImages 中排除

### 数据维护
- 源站产品数 > 本地产品数时，用 sitemap.xml 获取完整 URL 列表
- 产品名需去除 "Xiuben Lighting" 前缀
- 所有页面文字 "Xiuben" → "Minglu"（sourceUrl 中的域名除外）

### 部署
- Cloudflare Pages 连接 GitHub 仓库，自动部署
- 自定义域名在 Cloudflare 直接绑定，自动 SSL + CDN
- 推送到 GitHub main 分支即自动触发部署

---

## 🚀 六、部署步骤

1. 打开 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. **Workers & Pages** → 创建 → Pages → 连接 Git
3. 选择 `sivenhuang/minglu-lighting` 仓库
4. 构建命令：留空（纯静态） | 输出目录：留空
5. 部署完成后 → 自定义域 → 绑定 `minglulighting.com`
6. 等待 1-2 分钟全球生效

---

## 📝 七、WhatsApp 预设消息

- 产品卡片按钮：`Hi Minglu Lighting, I have a project and need a quote for: [产品名]`
- 产品详情按钮：同上
- 联系表单提交：生成结构化询价消息
- WhatsApp 号码：`+86 18098910947`（在所有页面中配置）

---

## 📊 八、产品视图

### 产品列表页（products.html）
- 12 个分类筛选按钮（All Products + 各分类）
- 产品卡片网格（响应式：≥900px 3列，≥600px 2列，<600px 1列）
- 每张卡片：图片 + 分类标签 + 名称 + 描述 + 参数 + View Details + WhatsApp

### 产品详情页（product.html?id=pN）
- 左侧：图片轮播（主图 + 缩略图 + 左右箭头）
- 右侧：分类标签 + 名称 + 描述 + 特性 + 规格表 + 功率选项 + 应用场景 + WhatsApp大按钮
- 底部：详情图片全宽展示
- 底部：相关产品推荐（同分类 3 个）

---

*此知识库由 WorkBuddy AI 自动生成，基于 2026-06-14 会话内容*
