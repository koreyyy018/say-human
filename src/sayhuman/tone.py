"""Small opt-in, situation-linked notes, separated from work artifacts.

This deterministic fallback is intentionally modest; a text classifier cannot
infer private emotions, true intent, or the relationship between two people.
"""
from __future__ import annotations
import re

ZH = re.compile(r'[\u4e00-\u9fff]')
FEELINGS = {
    'unclear': re.compile(r'搞不懂|看不懂|听不懂|困惑|有点懵|不明白|confus|lost|don.t understand', re.I),
    'uncertain': re.compile(r'不确定|怕说错|不敢|担心|焦虑|没把握|nervous|embarrass|unsure|worried', re.I),
    'frustrated': re.compile(r'烦|郁闷|崩溃|压力|头大|很累|frustrat|overwhelm|stuck|struggl', re.I),
}

CONTEXTS = [
    (re.compile(r'RAG|embedding|token|prompt|LoRA|quantization|agent|术语|模型|接口|API', re.I),
     ('技术术语容易把简单的动作说复杂，我们先抓住它具体做什么。',
      'Technical jargon can hide a simple mechanism; start with what it actually does.')),
    (re.compile(r'没上线|未上线|还没正式上线|未正式上线|生产|部署|staging|deploy|rollout', re.I),
     ('还没正式上线就先把进度说清楚，比硬写成绩更可靠。',
      'It is better to state the rollout stage clearly than overstate the result.')),
    (re.compile(r'闭环|对齐|赋能|拉通|抓手|协同|touch base|circle back|synergy', re.I),
     ('这句黑话没交代下一步怎么做，问清负责人和时间更有用。',
      'That phrase leaves the next action unclear; asking for ownership helps.')),
]
FALLBACK = {
    'unclear': ('这个说法有点绕，我们先把关键部分拆开。', 'The wording is hard to parse; here is the central point.'),
    'uncertain': ('你担心表述不准确，我们先把已确认和待确认的部分分开。', 'The safest wording separates confirmed facts from open questions.'),
    'frustrated': ('这件事卡住了，我们先找出一个能推进的下一步。', 'This has been frustrating; let us identify one concrete next step.'),
}
PLAYFUL = {
    'explain': ('先把黑科技翻译成生活话，不用立刻背下整本术语词典。', 'Think of this as removing the jargon wrapper, not adding another manual.'),
    'decode': ('先给黑话开个灯：下一步由谁做、什么时候做？', 'Let’s turn the buzzword fog into an owner and a deadline.'),
    'encode': ('真正的成果不靠 PPT 里的魔法百分比撑场面。', 'No need for magical percentages to make real engineering work shine.'),
    'align': ('先给“做好一点”装上可验证的尺子。', 'Let’s give “make it better” a measurable ruler.'),
    'report': ('把“已完成”和“待验证”分开，周报就不会偷偷长出超能力。', 'Separating done from pending keeps a status update from growing superpowers.'),
    'audit': ('别让没有来历的 KPI 在汇报里凭空登场。', 'Keep surprise KPIs from appearing out of thin air.'),
}


def connection_note(text: str, mode: str, tone: str, formal: bool = False) -> str | None:
    if formal or tone == 'neutral':
        return None
    lang = 0 if ZH.search(text) else 1
    if tone == 'playful':
        return PLAYFUL.get(mode, PLAYFUL['explain'])[lang]
    if tone != 'warm':
        return None
    kind = next((key for key, regex in FEELINGS.items() if regex.search(text)), None)
    if not kind:
        return None
    # Situation is more useful than generic praise or unsupported emotional inference.
    for pattern, copy in CONTEXTS:
        if pattern.search(text):
            return copy[lang]
    return FALLBACK[kind][lang]
