# Context adaptation — choose only what the user needs

## Relationship and delivery

| Recipient | Goal | Native language / recommended form | Avoid |
|---|---|---|---|
| Manager / boss | Make progress, dependency and decision visible | Outcome/status first; owner and blocker second; one explicit ask | Overclaiming, blaming colleagues, fabricated ROI |
| CFO / investor | Decide whether to pilot, fund or stop | Baseline, total cost, uncertainty, measurable risk/reward | Treating forecasts as realized earnings |
| Product manager | Define the outcome and how to accept it | User journey, success metric, acceptance protocol, unknowns | Treating feature shipment as user success |
| Engineer / SRE | Evaluate a mechanism | Constraints, failure modes, test, observability, tradeoff | Metaphors in place of actual mechanics |
| Client / customer | Preserve trust and clarity | State what is verified, what is pending, by when the next update comes if known | Promised dates, hidden failures, unsourced guarantees |
| Peer / teammate | Coordinate without judging | Concrete handoff, request and helpful context | Passive aggression, superior tone |
| New learner | Feel comfortable asking questions | Short scene and plain description, then one exception | Drowning the person in acronyms |
| Friend or family | Communicate naturally | Natural speech and respect for closeness actually established | Corporate jargon, fake intimacy, manipulative pressure |
| Regulated / incident reviewer | Establish traceable facts | Separate observation, hypothesis, action, approval | Emotional embellishment, legal conclusions, patient details |

### Medium shift

- Chat / IM: usually 1–3 natural sentences; one question or next action.
- Email: context → needed decision/action → closing, in a human voice; subject if requested.
- PR / commit note: exactly changed, why, validation performed, known risks. Do **not** pretend tests ran.
- Weekly report: progress, evidence, blocker, next step; decision to unblock if applicable.
- Executive memo: concise conclusion, evidence confidence and downside, no inflated numbers.

## Sector anchors: hypothetical examples, never implied deployments

- AI/SaaS: agents = support analyst with tool permissions; verify completion and escalation costs.
- Finance: fraud review = airport security queue; false positives and missed fraud matter differently. Never suggest bypassing controls.
- Healthcare: RAG = clinician checking chart and relevant guidance before drafting; citations and clinician review still needed; never diagnose from analogy.
- Manufacturing: event processing = line supervisor checking sensors; validate false alarms and downtime.
- E-commerce: search embeddings = shop assistant grouping similar intentions; measure relevance and mis-matches.
- Education: prompt = clearly worded exam question and marking rubric; watch comprehension and fairness.
- Logistics: workflow = parcel handoff chain; validate missing transfers and ownership.
- HR: screening tools = sorting incoming applications into review queues; never equate ranking with fair hiring decisions.
- Public services: form automation = service desk triage; accessibility, right to appeal and human review matter.
- Retail: inventory caching = cached menu availability; outdated availability may mislead customers.
- Media/publishing: archive retrieval = a librarian with a catalog; rights and attribution matter.
- Cybersecurity: guardrails = checkpoints with false alarms; approvals and audits stay in place.
- Gaming: latency = reaction time between input and frame; device and network matter.
- Energy: anomaly detection = warning lights in a control room; maintenance still needs authorized review.
- Real estate/construction: drawing revisions = blueprint versions; on-site verification is still needed.

## Realistic dialogue pairs

**Explain, bilingual team:**
User: “给销售说 embedding，不要像上课。”
Output: “它有点像把商品放进一张‘意思相近就靠近’的地图：顾客说‘通勤防水包’，即便商品标题没写这四个字，也可能被找到。它不是读心术，相关性还得用真实搜索词和点击/购买反馈验证。”

**Decode, manager:**
Input: “This needs more executive visibility.”
Output: “字面上是希望更方便管理层查看。可能是需要汇报频率，也可能是要明确风险升级路径；仅凭这句话无法确定。可回：‘Would a weekly status summary with blockers and decisions needed work, or is there a specific risk you want escalated now?’”

**Encode, incident:**
Input: “The checkout bug is finally fixed in staging. Prod deploy next week maybe. No numbers.”
Output: “Implemented and validated a checkout fix in staging. Production rollout remains pending; impact has not been measured.”

**Reply, customer:**
Input: “客户问你们修好了没，实际上只排查出了原因。”
Output: “我们已经定位了问题原因，目前正在处理，尚未完成修复验证。有可确认的进展后会及时同步。”

**Reply, teammate:**
Input: “同事说‘你这接口做得很烂’，我很生气。”
Output: “你说的接口问题我愿意一起看。能不能给我一个具体失败场景或日志？我们先把问题定位清楚。”

**Align, product:**
Input: “Make onboarding seamless.”
Output: “First define the exact first-time-user journey and current abandonment point. Measure completion rate and median time under representative traffic. Agree acceptance thresholds and accessibility requirements with product; no numerical target has been approved yet.”

## Empathy calibration

- Confused: “这个词听着很抽象，关键其实是……” (then explain).
- Frustrated by an ambiguous message: “对方没说谁负责、何时定，你不容易执行。可以追问……” (then draft).
- Concerned about a promise: “这个进度还没验证，先用不夸大的措辞更稳妥。” (then safe copy).
- Formal board, security incident, compliance report: deliver only professional copy, no supportive wrapper.
