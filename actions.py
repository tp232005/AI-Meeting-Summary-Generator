import re


# Phrases that typically precede action items
ACTION_TRIGGERS = [
    r'\bwill\b', r'\bneed to\b', r'\bshould\b', r'\bmust\b',
    r'\baction item\b', r'\bfollow.?up\b', r'\bassign\b', r'\btask\b',
    r'\bresponsible\b', r'\bdeadline\b', r'\bby (monday|tuesday|wednesday|thursday|friday|next week|end of day|eod)\b',
    r'\bschedule\b', r'\bset up\b', r'\bsend\b', r'\bshare\b',
    r'\bcreate\b', r'\bbuild\b', r'\bimplement\b', r'\bprepare\b',
    r'\breview\b', r'\bapprove\b', r'\bfinalize\b', r'\blaunch\b',
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in ACTION_TRIGGERS]


def extract_action_items(sentences: list[str]) -> list[dict]:
    """Identify sentences that likely contain action items."""
    actions = []
    for sentence in sentences:
        hit_count = sum(1 for pattern in COMPILED if pattern.search(sentence))
        if hit_count >= 1:
            # Try to extract owner name (capitalized word before/after trigger)
            owner_match = re.search(r'\b([A-Z][a-z]+)\b', sentence)
            owner = owner_match.group(1) if owner_match else 'Team'
            # Try to extract deadline
            deadline_match = re.search(
                r'\b(by|before|on)\s+(monday|tuesday|wednesday|thursday|friday|next week|end of day|eod|\d{1,2}/\d{1,2})\b',
                sentence, re.IGNORECASE
            )
            deadline = deadline_match.group(0).strip() if deadline_match else None
            actions.append({
                'action': sentence,
                'owner': owner,
                'deadline': deadline,
                'confidence': min(hit_count / 3.0, 1.0),
            })
    # Sort by confidence descending
    return sorted(actions, key=lambda x: x['confidence'], reverse=True)


def extract_decisions(sentences: list[str]) -> list[str]:
    """Identify sentences that likely contain decisions made."""
    decision_triggers = [
        r'\bdecided\b', r'\bagreed\b', r'\bapproved\b', r'\bconfirmed\b',
        r'\bvoted\b', r'\bresolved\b', r'\bconcluded\b', r'\bfinaliz\b',
        r'\bgoing with\b', r'\bchose\b', r'\bselected\b',
    ]
    compiled = [re.compile(p, re.IGNORECASE) for p in decision_triggers]
    decisions = []
    for sentence in sentences:
        if any(p.search(sentence) for p in compiled):
            decisions.append(sentence)
    return decisions
