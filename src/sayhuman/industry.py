"""Opt-in, explicitly hypothetical industry-specific applications.

These examples are NOT statements about an organization's real implementation.
"""
from __future__ import annotations

INDUSTRIES = {
    "ai": ("AI / SaaS", "模型问答与客服工单", "model-assisted customer support", "答案采纳率、人工转接率与单次成本", "accepted-answer rate, escalation rate and cost per resolved ticket"),
    "finance": ("Banking / Fintech", "交易对账与反欺诈复核", "reconciliation and fraud-review queues", "错误警报、漏报率及人工复核时间", "false alerts, missed cases and review time"),
    "healthcare": ("Healthcare / Hospital", "预约指引与院内知识查询", "appointment guidance and internal knowledge lookup", "引用准确率、错误建议率及人工复核", "citation accuracy, unsafe suggestions and human review"),
    "manufacturing": ("Manufacturing / Factory", "设备维护与质量巡检", "equipment maintenance and quality checks", "停机时长、误报与人工复核成本", "downtime, false alarms and manual-review effort"),
    "ecommerce": ("E-commerce / Marketplace", "商品检索与售后咨询", "product search and after-sales support", "检索准确率、退款错误率与响应时长", "search relevance, refund errors and response time"),
    "education": ("Education / EdTech", "课程资料检索与学习答疑", "course-material lookup and tutoring", "答题准确率、引用覆盖与教师复核", "answer accuracy, source coverage and teacher review"),
    "logistics": ("Logistics / Supply Chain", "包裹状态查询与异常派单", "parcel tracking and exception dispatch", "错派率、处理时间与通知准确率", "misroutes, handling time and notification accuracy"),
    "hr": ("HR / Recruiting", "招聘政策问答与候选人沟通", "recruitment policy Q&A and candidate communication", "错误建议率、人工复核与公平性检查", "error rate, manual review and fairness checks"),
    "government": ("Government / Public Service", "政务事项指引与工单分流", "public-service guidance and case routing", "错误指引率、可追溯性与申诉路径", "misguidance, traceability and appeal path"),
    "retail": ("Retail / Restaurants", "门店库存查询与客服支持", "store inventory and customer support", "库存准确率、误导回答与处理时间", "stock accuracy, misleading replies and handling time"),
    "media": ("Media / Publishing", "内容归档与版权信息查询", "editorial archive and rights lookup", "检索准确率、版权核验与人工编辑时间", "search relevance, rights checks and editorial time"),
    "security": ("Cybersecurity / IT", "告警归类与事件排查", "alert triage and incident response", "漏报率、误报率与人工审批", "false negatives, false positives and approvals"),
    "gaming": ("Gaming / Entertainment", "游戏客服与玩家反馈归类", "player support and feedback routing", "误分流率、答复质量与延迟", "misroutes, reply quality and latency"),
    "energy": ("Energy / Utilities", "巡检知识查询与设备告警", "inspection knowledge lookup and equipment alerts", "漏报率、安全审查与响应时间", "missed alerts, safety review and response time"),
    "realestate": ("Real Estate / Construction", "施工文档检索与报修派单", "construction documentation and repair dispatch", "工单准确率、现场复核与错误成本", "routing accuracy, on-site verification and error cost"),
}
ALIASES = {
    "saas":"ai", "ai / saas":"ai", "banking":"finance", "fintech":"finance", "banking / fintech":"finance",
    "healthcare / hospital":"healthcare", "hospital":"healthcare", "manufacturing / factory":"manufacturing",
    "factory":"manufacturing", "e-commerce / marketplace":"ecommerce", "commerce":"ecommerce", "e-commerce":"ecommerce",
    "education / edtech":"education", "edtech":"education", "logistics / supply chain":"logistics", "hr / recruiting":"hr",
    "government / public service":"government", "retail / restaurants":"retail", "media / publishing":"media", "publishing":"media",
    "cybersecurity / it":"security", "cybersecurity":"security", "gaming / entertainment":"gaming",
    "energy / utilities":"energy", "real estate / construction":"realestate", "real estate":"realestate",
    "医疗":"healthcare", "金融":"finance", "制造":"manufacturing", "电商":"ecommerce", "教育":"education",
    "物流":"logistics", "人力资源":"hr", "政务":"government", "零售":"retail", "出版":"media", "网络安全":"security", "游戏":"gaming", "能源":"energy", "房地产":"realestate",
}

APPLICATION = {
    "Prompt": ("为处理任务写清输入、标准与输出格式", "specify the request, constraints and response format"),
    "Agent": ("在人工授权范围内执行多步任务并处理异常", "execute bounded multi-step tasks with human approval"),
    "Context Window": ("处理长记录时监测遗漏、截断与费用", "check truncation, missed details and costs in long records"),
    "API": ("连接业务系统并追踪调用失败、权限与费用", "connect systems while tracking failures, access and cost"),
    "Function Calling": ("经权限校验后调用外部工具，避免误操作", "invoke tools only after permission checks"),
    "RAG": ("先检索经授权的资料、附上出处，再给答复", "retrieve authorized sources and cite them before answering"),
    "Multimodal": ("结合文字与图像等输入，并保护隐私", "combine text and images while protecting privacy"),
    "Tokens": ("测量输入与输出用量，核算单位任务成本", "measure input/output usage per completed task"),
    "Hallucination": ("抽检无依据的结论并设置人工复核", "audit unsupported claims and require human review"),
    "Vector Embeddings": ("检索语义相近的历史记录，复核误匹配", "retrieve semantically similar records and inspect false matches"),
    "Fine-tuning": ("以已授权样本训练，再对比基线效果", "train on authorized examples and compare against a baseline"),
    "Agentic Workflows": ("协调检索、审批、执行与异常回退", "coordinate retrieval, approval, actions and exception handling"),
    "LoRA": ("用较少的可训练参数做领域适配并验证性能", "adapt a model with fewer trainable parameters and verify quality"),
    "Quantization": ("在低精度部署下验证速度、成本和质量", "evaluate latency, cost and quality under lower precision"),
    "Caching": ("复用可复用的结果并严格检查时效", "reuse responses with explicit freshness safeguards"),
    "Guardrails": ("拦截高风险请求并追踪误拦与漏拦", "block risky actions and audit both false blocks and misses"),
}


def industry_example(term: str, industry: str, lang: str = "en") -> tuple[str, str]:
    key = industry.strip().casefold()
    key = ALIASES.get(key, key)
    if key not in INDUSTRIES:
        raise ValueError(f"Unknown industry '{industry}'. Available: {', '.join(INDUSTRIES)}")
    name, scene_zh, scene_en, metric_zh, metric_en = INDUSTRIES[key]
    application = APPLICATION[term][0 if lang == "zh" else 1]
    if lang == "zh":
        return (f"【假设案例·{name}】在“{scene_zh}”中，可以{application}。这只是应用示意，不代表某机构已部署。",
                f"优先验证：{metric_zh}；同时比较上线前基线，不预设节省金额。")
    return (f"Hypothetical {name} example: for {scene_en}, a team could {application}. This does not imply a live deployment.",
            f"Measure {metric_en} against a baseline; do not assume cost savings.")


def industry_followup(industry: str, lang: str) -> str:
    key = ALIASES.get(industry.strip().casefold(), industry.strip().casefold())
    if key not in INDUSTRIES:
        raise ValueError(f"Unknown industry '{industry}'. Available: {', '.join(INDUSTRIES)}")
    metrics = INDUSTRIES[key][3 if lang == "zh" else 4]
    return f"如何核验{metrics}？" if lang == "zh" else f"How will we validate {metrics}?"
