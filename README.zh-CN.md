# WiseTalk — 职场沟通教练工作台

*[English](README.md) · [系统指标](METRICS.md) · [运行证据](RUN_EVIDENCE.md) · [Skill 契约](docs/skill-contract.md) · [贡献指南](CONTRIBUTING.md)*

WiseTalk 是一套 AI 原生的职场沟通教练系统，采用 **「1+8+X+安全网关」** 多 Agent 架构：

- **1 个路由 Agent** — 入口守门人（意图识别、上下文记忆）
- **8 个专家 Agent** — 每个对应一种沟通模型（STAR、SCRTV、MECE、PREP、SCQA、RIDE、FFC、Funnel）
- **X 个共享 Skill** — 逻辑检测、情绪分析、模拟对战、成长追踪
- **双向安全网关** — 入口拦截器（注入过滤）+ 输出前校验闸门（幻觉检测：PASS / WARN / BLOCK 三档裁决）

系统依据 **WiseTalk 主规格书 v2.0**（[`_wisetalk_extracted.md`](_wisetalk_extracted.md)）构建。

---

## 这是一套学习系统，不是代写服务

这个区别就是整个设计的核心。普通聊天机器人收到「帮我谈加薪」会直接把稿子写出来——用户什么也没学到，
下个季度还是同样不会。WiseTalk 拒绝绕过空白卡片作答：

| 教学法 | 在系统中的位置 |
|---|---|
| **课程体系** — 8 种可迁移框架、32 个场景 | 模型目录。学习者学一次 STAR，可复用于面试、绩效面谈、项目复盘、简历 |
| **脚手架** — 内容必须由学习者提供 | Skill-3 强制填空卡片。卡片为空则不生成。卡片本身就是教学内容：*一个好答案由哪些部分构成* |
| **示范样例** — 让结构可见 | Skill-7 只依据学习者填写的内容生成，让学习者看见**自己的**素材如何被组织成结构化表达 |
| **形成性反馈** — 批判而非代改 | Skill-13 返回恰好 3 条可执行意见并询问「接受还是修改」；迭代上限 3 轮，由学习者决定何时够好 |
| **能力评估** — 压力下的实战演练 | Skill-8 模拟对战竞技场以敌意角色拷问学习者的稿件；Skill-9 从逻辑、情商、临场反应、说服力四维打分 |
| **学习分析** — 纵向进步追踪 | Skill-10 将历史分数聚合为成长曲线，并指出最薄弱维度 |
| **学术诚信** — 成果始终属于学习者 | Skill-12 在内容抵达学习者之前，拦截一切其未提供的数字、引用与言论 |

**面向教学辅助：** 教师只需在 [`reference/wisetalk-model-catalog.md`](reference/wisetalk-model-catalog.md)
中增加一个框架小节，并在路由表中加一行，新模型即出现在路由器、命令行与浏览器填空卡片中——
**零代码文件改动**（见 [METRICS.md](METRICS.md#extensibility)）。课程即文档，因此课程的主人可以真正拥有它。

---

## 快速开始 — 30 秒跑通，无需安装

唯一依赖是 Python 3.9+。**没有任何需要 `pip install` 的东西**——本仓库的可执行层完全基于 Python 标准库。

```
git clone https://github.com/ay4322-a11y/WiseTalk_GOAI.git && cd WiseTalk_GOAI
python demo.py                      # 全部 5 个场景，走完 Stage 0-4
python demo.py --list               # 列出场景
python demo.py --scenario 03        # 「编造数据 → BLOCK → 重新生成」闭环
python demo_server.py               # 浏览器演示 http://localhost:8000
python -m unittest discover tests   # 28 个确定性测试
```

`demo.py` 调用 **与专家 Agent 完全相同的 Skill 脚本**（注入过滤器、幻觉闸门、成长趋势聚合器）
走完主规格书 §5 的 Stage 0–4。

两处边界在输出中**明确标注**，而非隐藏：Stage 1 的路由器是确定性关键词分类器，
作为 Skill-1 大模型分类器的替身；Stage 3b 默认回放录制稿件，除非设置 `ANTHROPIC_API_KEY`
并传入 `--api`。**无论哪条路径，裁决稿件的闸门都是真实的生产脚本**——这才是值得演示的部分。

每个阶段都会向 `runs/<时间戳>.jsonl` 追加一条记录：阶段、Skill、裁决、退出码、耗时、重试次数。
该文件即审计链路。

---

## 8 个专家沟通 Agent

| Agent | 专家 | 模型 | 使用场景（由 Skill-1 路由） |
|-------|------|------|------------------------------|
| Agent 1 | STAR 面试官 | STAR | `Job_Interview` · `Performance_Review` · `Project_Debrief` · `Resume_Writing` |
| Agent 2 | SCRTV 汇报者 | SCRTV | `Project_Status_Report` · `Strategy_Proposal` · `Budget_Request` · `Issue_Escalation` |
| Agent 3 | MECE 架构师 | MECE / 金字塔原理 | `Logical_Analysis` · `Report_Outlining` · `Meeting_Minutes` · `Brainstorming_Structure` |
| Agent 4 | PREP 演讲者 | PREP | `Elevator_Pitch` · `Quick_Meeting_Speech` · `Daily_Standup` · `Public_Comment` |
| Agent 5 | SCQA 分析师 | SCQA | `Crisis_Management` · `Problem_Solving` · `Conflict_Resolution` · `Urgent_Incident` |
| Agent 6 | RIDE 谈判者 | RIDE | `Salary_Negotiation` · `Client_Deal` · `Vendor_Management` · `Resource_Allocation` |
| Agent 7 | FFC 赞赏大师 | FFC | `Team_Recognition` · `Relationship_Building` · `Peer_Feedback` · `Ice_Breaking` |
| Agent 8 | Funnel 提炼器 | 沟通漏斗 | `Task_Delegation` · `Complex_Instruction` · `Information_Compression` · `Executive_Summary` |

**Agent 8 说明：** Funnel 提炼器是「反向器」——它压缩长文本（Skill-5），不运行教练循环
（无 Skill-7 / Skill-13）。其停止条件是机械的（压缩至原文 20% 以内），而非判断性的。

---

## 端到端流程（主规格书 §5）

```
Stage 0   Skill-11  注入拦截        DFA + 正则，失败即拦截（fail-closed）→ 403
Stage 1   Skill-1   意图路由        三档置信度：≥0.6 直达 · 0.4–0.6 反问澄清 · <0.4 兜底
Stage 2   Skill-3   强制填空卡片    界面是卡片而非聊天框；卡片为空则拒绝生成
Stage 3a  Skill-12  输入闸门        生成之前先校验卡片数据（占位符、伪造声明）
Stage 3b  Skill-7   生成 + 输出闸门  BLOCK 触发自动重写（最多 2 次），用户永远看不到被拦截的稿件
          Skill-13  迭代批判        恰好 3 条意见，3 轮后强制退出
Stage 4   Skill-8/9 对战与评分      敌意角色拷问 + 四维打分
Stage 5   Skill-12  合规封装        免责声明恰好追加一次
Stage 6   Skill-10  成长曲线        历史分数聚合为趋势
```

---

## 核心指标（由 `python tools/metrics.py` 计算，非估算）

| 指标 | 数值 |
|---|---:|
| 沟通模型 / 可路由场景 | 8 / 32 |
| 第三方运行时依赖 | **0** |
| 注入攻击语料拦截率 | **28 / 28（100%）** |
| 正常职场语料误报率 | **0 / 24（0%）** |
| 幻觉闸门裁决与标注一致率 | **6 / 6（100%）** |
| 自动化测试 | **28 项全部通过** |
| 场景表现与声明一致 | **5 / 5** |
| 新增一个模型需改动的代码文件 | **0** |

误报率与拦截率同等重要：一个会拦截「请忽略我上一封邮件」的过滤器，是为了显得安全而弄坏了产品。
这两句话都在语料库中，都能通过。

完整口径与诚实说明见 [METRICS.md](METRICS.md)；这些是**系统度量，不是用户成效**——
本项目未做用户对照研究，因此不作任何学习成效的声明。

---

## 开源与依赖边界

**许可协议：** [Apache-2.0](LICENSE)（相较 MIT 增加了明确的专利授权条款）。

**第三方运行时依赖：0 个。** 全部脚本仅引用 Python 标准库
（`argparse`、`json`、`re`、`os`、`subprocess`、`pathlib`、`http.server`、`urllib`、`unittest`），
因此没有 `requirements.txt`，也没有需要审计的传递依赖树。

**知识产权边界：** 主规格书、模型目录、9 个 Agent 定义、11 个 Skill、全部脚本与演示程序均为自研，
以 Apache-2.0 开放；8 种沟通模型为公共领域框架，目录中逐一标注了出处，本项目不主张权利；
**Claude 模型 API 与 Claude Code 运行时为 Anthropic 的商业产品，属外部依赖，不在开源范围内**。

商业边界仅限于模型 API 及其运行时。构成 WiseTalk 的一切——路由表、填空卡片契约、双向安全网关、
批判循环、Skill 生命周期工具——都是本仓库中的文本与标准库 Python，可运行于任何具备足够指令遵循能力的模型之上。
`demo.py` 证明了确定性安全层**完全不需要模型调用**即可运行。

---

## 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [docs/skill-contract.md](docs/skill-contract.md)。

本项目坚持两条标准：

1. **不留无法验证的声明。** README、`METRICS.md`、`RUN_EVIDENCE.md` 中的每个数字都由读者可复现的命令产生。
2. **闸门必须是确定性的。** 任何决定文本能否抵达用户的环节，都是带退出码的脚本，而非提示词。
   以提示词实现的安全控制只是一个建议，本项目不把建议当作控制来交付。
