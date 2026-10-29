# 快即是慢 官网

「快即是慢」（iOS / iPadOS 个人投资研究工具）的官网与 Universal Link 托管站点。
托管在 GitHub Pages，纯静态、无构建步骤、无第三方脚本。

## 页面

| 路径 | 内容 |
|---|---|
| `index.html` | 首页：应用介绍、核心功能、界面展示、使用流程、运行平台、重要声明、开发者与版权 |
| `features.html` | 产品展示：逐页说明首页 / 详情 / 研究 / 持仓 / 每日摘要 / 使用流程 / 能力边界 |
| `about.html` | 关于我们：产品理念、开发者信息、版权所有者、网站性质与备案说明 |
| `legal/privacy.html` | 隐私政策：处理的信息、用途、存储、第三方 SDK、共享、用户权利 |
| `legal/terms.html` | 用户协议：协议范围、应用定位、不构成投资建议、内容版权、使用规范、免责 |
| `legal/contact.html` | 联系方式：问题反馈、数据删除、版权投诉、开发者信息 |
| `app/index.html` | Universal Link 落地页（未安装应用时的兜底） |
| `.well-known/apple-app-site-association` | Apple 通用链接校验文件（微信 OpenSDK 回跳用） |
| `assets/style.css` | 共用样式（所有页面引用，无外部依赖） |

## 为什么是这个结构

> 任务跟踪：`feverbit/ValueInvestment-iOS#18`（官网整改，微信开放平台审核前置项）。

微信开放平台审核对官网有明确要求（2026-10 驳回意见原文）：

> 网站内容、排版等需符合常规网站要求，不支持只有几行文字，或者仅是一张或几张图片的，又或者是文档形式的网站内容。
> 网站内容需有但不限于首页、产品展示、相关应用名称字眼及其应用介绍、用户协议、版权所有者、网站备案信息、联系方式等基础服务信息。

因此站点按「多页面 + 每页有实质内容」组织，并逐项覆盖：

- ✅ 首页 `index.html`
- ✅ 产品展示 `features.html`（独立页面）
- ✅ 应用名称字眼：每页页头、`<title>`、正文首段都出现「快即是慢」
- ✅ 应用介绍：首页「应用介绍」段 + 产品展示各功能说明
- ✅ 用户协议 `legal/terms.html`
- ✅ 版权所有者：每页页脚 + `about.html` 版权段
- ✅ 网站备案信息：`about.html#site`（说明为境外静态托管、无 ICP 备案号及原因）
- ✅ 联系方式 `legal/contact.html` + 每页页脚

**改动这些页面时不要削减正文量**：每页 `<main>` 正文必须保持在 800 字符以上，
否则可能再次触发「只有几行文字」的驳回。`app/index.html`（Universal Link 落地页）
**不设例外**，同样要求 ≥ 800 字符——它可能被分享给未安装应用的人，是真实可见页面。

### 提交前自检

```bash
python3 tools/check-site.py
```

脚本仅用标准库，检查：每页 `<main>` 可见文本量（去空白）≥ 800、标题 / 页头 / 首段出现应用名、
版权与联系方式入口、站内链接与锚点是否可解析。任何一项不满足即以非零状态退出。

### 内容一致性（改文案前先核对客户端）

官网描述必须与 iOS 客户端实际能力一致，以下两处曾在复审中被指出：

- **持有建议**：客户端会展示持有建议标签、建议仓位区间与换仓参考金额（`Features/Advice/AdviceView.swift`）。
  文案应写「由使用者自建研究模型计算并原样呈现、不自动执行交易、不构成投资建议」，
  不要写成「应用完全不输出任何建议」。
- **每日提醒**：正式构建登记服务端推送，摘要生成完成后才经 APNs 发送
  （`Models/DigestNotifications.swift`）。文案不要写「固定时段收到通知」。

## 命名说明

微信开放平台登记的移动应用名称为 **快即是慢**，官网标题、正文、协议名称必须与之一致
（官方审核规范要求「应用名称与官网介绍一一对应」）。

## Universal Link

`.well-known/apple-app-site-association` 中的 App ID 为 `57J7J3738Y.com.valueinvestment.app`，
路径 `/app/*`。微信要求 Universal Link 支持 https、路径带通配符、不能带 query 参数。

> ⚠️ 截至 2026-10-30，通用链接尚未生效：iOS 只读取**域名根路径**的
> `https://feverbit.github.io/.well-known/apple-app-site-association`，该地址仍是 404
> （GitHub Pages 项目站无法在根路径托管文件）。因此现在点开分享链接都会打开
> `app/index.html` 落地页。启用方案与限制见 iOS 仓库 `docs/wechat-share.md` 第 2 节，
> 落地页文案也据此写成「尚未启用通用链接」，不要在未生效时宣称点链接能直接跳进应用。

若仓库名或分支名变更，Universal Link 需同步修改三处：本文件说明、iOS 工程
`ValueInvestment/project.yml` 的 `WECHAT_UNIVERSAL_LINK`、微信开放平台登记的 Universal Links。

## 注意

- **不要**把持仓、账户、内网地址等任何私有信息写进本仓库，这里是公开站点；
- 本站不引入第三方统计、广告或 Cookie。
