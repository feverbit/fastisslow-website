# 快即是慢 官网

「快即是慢」（iOS / iPadOS 个人投资研究工具）的官网与 Universal Link 托管站点。

> 命名说明：微信开放平台登记的移动应用名称为 **快即是慢**，官网标题、简介、协议名称必须与之一致
> （官方审核规范要求「应用名称与官网介绍一一对应」）。
发布在 GitHub Pages 上，纯静态、无构建步骤。

## 目录

```
index.html                              应用介绍（功能、平台、免责声明）
legal/privacy.html                      隐私政策
legal/terms.html                        用户协议
legal/contact.html                      联系方式
app/index.html                          Universal Link 落地页（/app/* 未安装时的兜底）
.well-known/apple-app-site-association  Apple 通用链接校验文件（微信 OpenSDK 回跳用）
```

## 发布方式

仓库 → Settings → Pages → Build and deployment：

- Source: **Deploy from a branch**
- Branch: **main** / **/ (root)**

发布后地址：

- 官网：`https://feverbit.github.io/fastisslow-website/`
- Universal Link：`https://feverbit.github.io/fastisslow-website/app/`

## Universal Link 说明

`.well-known/apple-app-site-association` 里的 App ID 是
`57J7J3738Y.com.valueinvestment.app`（Team ID + Bundle ID），路径为 `/app/*`。
微信要求 Universal Link 支持 https、路径带通配符、不能带 query 参数。

**如果仓库名或分支名改了**，Universal Link 也要跟着改：

1. 本文件里的说明；
2. iOS 工程 `ValueInvestment/project.yml` 的 `WECHAT_UNIVERSAL_LINK`；
3. 微信开放平台里登记的 Universal Links。

## 注意

- 不要把持仓、账户、内网地址等任何私有信息写进本仓库，这里是公开站点。
- 更新内容后直接提交到 `main`，Pages 会自动重新发布（约 1 分钟）。
