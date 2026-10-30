# owlwrite MCP 接入说明（给 Agent 终端用户）

## 0. 装技能（只有两个官方入口）

| 渠道 | 地址 |
|---|---|
| SkillHub | https://skillhub.cn/skills/user_164f4c1f/owlwrite-paper |
| ClawHub | https://clawhub.ai/j-levee/skills/owlwrite-paper |

别从其他站点、镜像或第三方脚本装同名技能。装完先做下面三步自检，再往下配 Key：

1. `curl -s https://owl.skillsutra.cn/v1/meta` → `skill.latest_version` 不低于 `1.1.2`；
2. 同一响应里 `channels.weipu_ready` 决定能不能做检测（`false` 读 `weipu_detail` 转告用户）；
3. 配好 Key 后调 `owl_wallet`，能返回余额即连通。

## 1. 拿到 API Key（对话内即可完成）

注册需要邮箱验证码（15 分钟有效），两步：

```bash
# 1) 发验证码到你邮箱
curl -s -X POST https://owl.skillsutra.cn/v1/auth/send-code \
  -H "Content-Type: application/json" -d '{"email":"你的邮箱"}'

# 2) 把邮件里的 6 位码填进去，换 API Key
curl -s -X POST https://owl.skillsutra.cn/v1/auth/register \
  -H "Content-Type: application/json" -d '{"email":"你的邮箱","code":"123456"}'
```

返回里的 `api_key`（`owl_sk_` 开头）**只显示这一次**，立刻存好。
也可在官网 https://paper.skillsutra.cn 右上角「开始使用」注册，二选一。

> 体验额度以注册返回的 `wallet.balance_avail` 为准，不要预设金额。
> 退信/收不到：先查垃圾邮件箱；同邮箱 60 秒内只能发一次，同一网络 10 分钟最多 10 次。

## 2. MCP 客户端配置

### WorkBuddy / Claude Desktop（claude_desktop_config.json）

```json
{
  "mcpServers": {
    "owlwrite": {
      "command": "python",
      "args": ["<技能目录>/owlwrite-paper/scripts/mcp_server.py"],
      "env": {
        "OWL_BASE": "https://owl.skillsutra.cn",
        "OWL_API_KEY": "owl_sk_你的key"
      }
    }
  }
}
```

- `<技能目录>` 换成你本机技能包实际路径（`scripts/mcp_server.py` 就在技能包里，无需另下文件）。
- `OWL_BASE` 固定填 **`https://owl.skillsutra.cn`**（接口地址）。官网是 `paper.skillsutra.cn`，
  两者不同域，填错会连不上。
- Python ≥ 3.11，需 `pip install mcp httpx`。
- **上传大文件把客户端超时放宽**：`owl_upload` 传 30MB 论文在上行慢的网络可能超过 30 秒，
  远程接入时把 `timeout` 设到 `120000`（毫秒），否则会在本地先超时而服务端其实已收下。

### 配好后验证与冷启动注意

对话里说「查一下肠道菌群和代谢的文献」，能返回带 DOI 的文献列表即接入成功。

- **冷启动陷阱**：MCP 客户端启动后第一次调工具可能报连接错误——是客户端在拉起本地进程，
  等几秒重试即可，不要改配置重装；连续失败才检查 `OWL_BASE`（服务端是 owl.skillsutra.cn，
  官网是 paper.skillsutra.cn，两者不同域，填错连不上）。
- **开工先调 `owl_meta`**：返回 `notices` 是平台公告（如检测服务状态、活动上线），
  有新公告要按相关度转告用户；`channels.weipu_ready=false` 时检测类能力暂不可用，别白跑报价。
  该字段是检测服务的**真实连通性**（`queryBalance`）检查结果，不是「凭据填没填」；原因看同级
  `channels.weipu_state`（`unconfigured` / `auth_failed` / `ip_blocked` / `account_issue` /
  `unverified`）与 `channels.weipu_detail`，对用户只转述 `weipu_detail` 这句人话。
- **版本判定**：`owl_meta` 的 `required_update=true` 且本地版本低于 `min_supported_version`
  时必须先让用户更新技能再继续付费动作。

## 3. 工具一览（19 个）

| 工具 | 作用 | 计费 |
|---|---|---|
| `owl_search` | 文献检索（相关性重排 + 核心刊标记 + 关键词扩展） | 命中 2 积分 / 缓存 1 积分 / 0 结果 0 积分 |
| `owl_article` | 文献详情（DOI / 年卷期等完整元数据） | 4 积分/次；72 小时缓存 1 积分 |
| `owl_fulltext` | 中文期刊全文 PDF 直链（约 1 小时有效，立即下载） | 200 积分/篇；72 小时内同篇重取 1 积分 |
| `owl_oa` | 外文 OA 免费全文（arXiv / OpenAlex / Unpaywall / Europe PMC） | **0 积分，免费** |
| `owl_citations` | 引文追溯（它引用了谁 / 谁引用了它） | 2 积分/次；72 小时缓存 1 积分 |
| `owl_figure` | 科研配图（TikZ 示意 / 数据图表 / AI 配图） | 25 积分/张，按实际交付张数；未出图 0 积分 |
| `owl_products` | 全平台实时价目（价格唯一可信来源） | 免费 |
| `owl_meta` | 技能最新版本 + 平台公告（开工校准；含 `channels.weipu_ready` 检测服务状态） | 免费 |
| `owl_disciplines` | 斟知智评学科码表（class_id 用，逐级筛给用户选） | 免费 |
| `owl_campaign` | 活动券码兑换 / 我的邀请码与战绩 | 免费 |
| `owl_upload` | 上传本机文件换 `file_id`（检测 / 图像 / 格式检测必用；≤30MB） | 免费 |
| `owl_quote` | 写作 / 检测 / 核验报价（返回预估区间；检测需给 `hanzi`） | 免费（不扣积分） |
| `owl_run` | 执行已报价任务 | 写作/检测按**实际量**结算（无冻结、无封顶），其余按报价 |
| `owl_run_status` | 轮询任务状态（含 `pending_upstream`＝报告仍在生成，不是失败） | 免费 |
| `owl_run_report` | 核验逐条判定；检测报告四份（`part=main` 综合 / `compare` 逐句比对 / `simple` 简洁 PDF / `fulltext` 原文对照 PDF） | 免费 |
| `owl_run_content` | 写作完整正文与参考文献 | 免费 |
| `owl_wallet` | 查余额（含 30 天内到期积分、赠送积分余额） | 免费 |
| `owl_recharge` | 发起充值（10/30/50/100/500 元） | 免费 |
| `owl_recharge_status` | 查充值单 / 核实到账 | 免费 |

1 积分 = 0.01 元；充值购买积分有效期 1 年，活动/赠送积分有效期 90 天，均先到期先扣；
全平台缓存命中统一 1 积分，**缓存窗口统一 72 小时**。
价格可能调整，一切以 `owl_products` / `owl_quote` 实时返回与官网 /price 页为准。
任务失败自动退款；检索无结果不收费；OA 探测不收费。

## 4. 官网能补什么（可选，不是必经）

- 个人中心 https://paper.skillsutra.cn/account.html：余额与流水、任务记录、报告与全文下载、API Key 管理与吊销。
- 报告验真：维普 https://vpcs.fanyu.com/systemVerify 、斟知 https://www.zhenzhi.com/verify 。
- 发票 / 企业采购 / 多账号 / API 对接：**vipsmart@vipslib.com**。
