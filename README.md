# 夜猫子论文工作台 · owlwrite-paper

> 面向 AI Agent 的论文全流程技能包：**找文献 → 写初稿 → 跑检测 → 核引文**，全程在对话里完成，产物落到用户自己的电脑。

- 版本：**1.1.0**
- 官网与实时价目：https://paper.skillsutra.cn （价目页 `/price`，一切报价以接口实时返回为准）
- 服务端点：https://owl.skillsutra.cn （MCP / HTTP 网关）

## 能力

| 类别 | 工具 | 说明 |
|---|---|---|
| 文献 | `owl_search` `owl_article` `owl_fulltext` `owl_oa` `owl_citations` | 中外文检索、详情、中文授权全文、外文 OA 免费全文、引文追溯 |
| 写作 | `owl_quote` `owl_run` `owl_run_status` `owl_run_content` | 一次性连续成文，按实际成文字数结算 |
| 配图 | `owl_figure` | TikZ 矢量示意 / 数据图表 / AI 配图，按实际交付张数结算 |
| 检测 | `owl_products` `owl_quote` `owl_run` `owl_run_report` | 查重、AIGC、格式、智评、图像可信度、文献质量、斟校对（21 个商品，检测经 `owl_quote`(check) 下单） |
| 核验 | `owl_quote`(verify) `owl_run` `owl_run_report` | 逐条核对引文元数据，附撤稿徽标 |
| 账户 | `owl_wallet` `owl_recharge` `owl_recharge_status` `owl_campaign` `owl_meta` | 余额、充值、券码、版本公告 |

共 **17 个 MCP 工具**。

## 安装

1. 把本仓库内容放到你的 Agent 的技能目录（保留 `SKILL.md`、`references/`、`scripts/` 结构）。
2. 在 MCP 客户端配置里指向 `scripts/mcp_server.py`，并填自己的 API Key：

```json
{
  "mcpServers": {
    "owlwrite": {
      "command": "python",
      "args": ["<本仓库路径>/scripts/mcp_server.py"],
      "env": { "OWL_BASE": "https://owl.skillsutra.cn", "OWL_API_KEY": "owl_sk_你的key" }
    }
  }
}
```

3. API Key 在 https://paper.skillsutra.cn 注册后获取（只显示一次）。

详细步骤见 [`references/mcp-setup.md`](references/mcp-setup.md)，商品与能力边界见 [`references/product-matrix.md`](references/product-matrix.md) 与 [`references/coverage.md`](references/coverage.md)。

## 计费原则

- 1 积分 = 0.01 元；**先报价、用户确认、再执行**，不静默扣费。
- 检索按命中三态计费（命中 / 缓存 / 无结果），写作按实际成文字数结算（超出预估以冻结上限为限，不加收），配图按实际交付张数结算（未出图不收费）。
- 具体单价一律以 `owl_products` / 官网 `/price` 实时返回为准，本仓库不写死价格。

## 合规

- 产出内容按《人工智能生成合成内容标识办法》携带 AI 标识与 AIGC 元数据。
- 拒绝代写代考等违反学术诚信的请求；检测类工具用于作者自查与修正。
- 本服务通过 API 调用第三方大模型服务，该提供方已按国家规定履行生成式人工智能服务备案义务。

## 许可与反馈

使用问题与商务合作：vipsmart@vipslib.com
