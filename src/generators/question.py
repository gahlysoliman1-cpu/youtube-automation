from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass
from typing import Any

from ..state import StateStore
from ..utils.text import clamp_list, normalize_text
from .llm import LLMOrchestrator

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ShortSpec:
    question: str
    answer: str
    category: str
    title: str
    description: str
    tags: list[str]
    hashtags: list[str]

    def voice_script(self) -> str:
        return (
            f"{self.question} "
            "You have 10 seconds. "
            "If you know the answer before time runs out, write it in the comments."
        )


_BANNED = [
    r"\blyrics\b",
    r"\bthis line\b",
    r"\bwhich song\b",
    r"\bwhat song\b",
    r"\bmovie quote\b",
    r"\bwho said\b",
    r"\bbrand slogan\b",
    r"\bpolitic\w*\b",
    r"\belection\b",
    r"\bterror\w*\b",
    r"\bviolence\b",
    r"\bsex\w*\b",
    r"\bnsfw\b",
    r"\bdrug\w*\b",
    r"\bweapon\w*\b",
]
_BANNED_RE = re.compile("|".join(_BANNED), re.IGNORECASE)


def _looks_safe(question: str, answer: str) -> bool:
    q = normalize_text(question)
    a = normalize_text(answer)
    if not q or not a:
        return False
    if len(q) < 8 or len(q) > 120:
        return False
    if len(a) < 1 or len(a) > 60:
        return False
    if "http" in q or "www" in q or "http" in a or "www" in a:
        return False
    if _BANNED_RE.search(q) or _BANNED_RE.search(a):
        return False
    if question.count("\n") > 4:
        return False
    return True


def _coerce_list(x: Any) -> list[str]:
    if isinstance(x, list):
        out = []
        for it in x:
            if isinstance(it, str) and it.strip():
                out.append(it.strip())
        return out
    if isinstance(x, str):
        return [s.strip() for s in x.split(",") if s.strip()]
    return []


def _ensure_hashtag_short(items: list[str]) -> list[str]:
    out = []
    for it in items:
        s = it.strip()
        if not s:
            continue
        if not s.startswith("#"):
            s = "#" + s.lstrip("#")
        out.append(s)
    if "#shorts" not in [x.lower() for x in out]:
        out.insert(0, "#shorts")
    return out


def _local_bank(rng: random.Random) -> ShortSpec:
    capitals = [
        ("Japan", "Tokyo"),
        ("France", "Paris"),
        ("Canada", "Ottawa"),
        ("Brazil", "Brasília"),
        ("Australia", "Canberra"),
        ("Egypt", "Cairo"),
        ("Turkey", "Ankara"),
        ("Mexico", "Mexico City"),
        ("Argentina", "Buenos Aires"),
        ("South Korea", "Seoul"),
        ("India", "New Delhi"),
        ("Spain", "Madrid"),
        ("Italy", "Rome"),
        ("Norway", "Oslo"),
        ("Sweden", "Stockholm"),
        ("Finland", "Helsinki"),
        ("Greece", "Athens"),
        ("Portugal", "Lisbon"),
        ("Poland", "Warsaw"),
        ("Netherlands", "Amsterdam"),
        ("Belgium", "Brussels"),
        ("Switzerland", "Bern"),
        ("Austria", "Vienna"),
        ("Ireland", "Dublin"),
        ("Denmark", "Copenhagen"),
        ("China", "Beijing"),
        ("Thailand", "Bangkok"),
        ("Vietnam", "Hanoi"),
        ("Indonesia", "Jakarta"),
        ("South Africa", "Pretoria"),
    ]

    elements = [
        ("Hydrogen", "H"),
        ("Helium", "He"),
        ("Carbon", "C"),
        ("Oxygen", "O"),
        ("Sodium", "Na"),
        ("Potassium", "K"),
        ("Iron", "Fe"),
        ("Gold", "Au"),
        ("Silver", "Ag"),
        ("Copper", "Cu"),
        ("Mercury", "Hg"),
        ("Tin", "Sn"),
        ("Lead", "Pb"),
    ]

    planets = [
        ("largest planet", "Jupiter"),
        ("closest planet to the Sun", "Mercury"),
        ("planet known as the Red Planet", "Mars"),
        ("planet with the most famous rings", "Saturn"),
    ]

    modes = ["capital", "element", "planet", "math"]
    mode = rng.choice(modes)

    if mode == "capital":
        country, capital = rng.choice(capitals)
        q = f"What is the capital of {country}?"
        a = capital
        cat = "Geography"
    elif mode == "element":
        element, symbol = rng.choice(elements)
        q = f"Which element has the chemical symbol '{symbol}'?"
        a = element
        cat = "Science"
    elif mode == "planet":
        prompt, ans = rng.choice(planets)
        q = f"Which planet is the {prompt}?"
        a = ans
        cat = "Space"
    else:
        x = rng.randint(12, 99)
        y = rng.randint(3, 9)
        op = rng.choice(["+", "-", "×"])
        if op == "+":
            q = f"Solve this in your head: {x} + {y} = ?"
            a = str(x + y)
        elif op == "-":
            q = f"Solve this in your head: {x} - {y} = ?"
            a = str(x - y)
        else:
            m1 = rng.randint(3, 12)
            m2 = rng.randint(3, 12)
            q = f"Solve this in your head: {m1} × {m2} = ?"
            a = str(m1 * m2)
        cat = "Brain Teaser"

    title = f"10-Second Trivia: {cat} Challenge #shorts"
    desc = "Can you answer in 10 seconds? Write your guess in the comments!\n\n#shorts #trivia #quiz"
    tags = ["shorts", "trivia", "quiz", "general knowledge", cat.lower()]
    hashtags = ["#shorts", "#trivia", "#quiz"]
    return ShortSpec(
        question=q,
        answer=a,
        category=cat,
        title=title,
        description=desc,
        tags=tags,
        hashtags=hashtags,
    )


def generate_unique_short_spec(llm: LLMOrchestrator, state: StateStore, rng: random.Random) -> ShortSpec:
    prompt_template = (
        "You generate SAFE, non-copyrighted, English-only trivia for a 12-second YouTube Short.\n"
        "Return ONLY valid JSON with these keys exactly:\n"
        "question, answer, category, title, description, tags, hashtags\n\n"
        "Rules:\n"
        "- Audience: international (English).\n"
        "- No song lyrics, no movie quotes, no copyrighted lines, no brand slogans.\n"
        "- No politics, hate, sex, violence, weapons, drugs.\n"
        "- The question must be answerable in 10 seconds.\n"
        "- The answer must be short (1-4 words or a number).\n"
        "- Add #shorts in hashtags.\n"
        "- Title <= 90 characters.\n"
        "- tags: 5-12 short tags.\n"
        "- hashtags: 3-7 hashtags.\n\n"
        "Avoid repeating any of these (do not reuse or paraphrase closely):\n"
        "{recent}\n"
    )

    used = state.data.get("used_questions", {})
    recent_qs = []
    if isinstance(used, dict):
        for v in list(used.values())[-30:]:
            if isinstance(v, dict) and isinstance(v.get("q"), str):
                recent_qs.append(v["q"])

    recent = "\n".join(f"- {q}" for q in recent_qs[-20:]) if recent_qs else "- (none)"
    prompt = prompt_template.format(recent=recent)

    for attempt in range(1, 7):
        try:
            obj = llm.generate_json(prompt, max_tokens=520)
            q = str(obj.get("question", "")).strip()
            a = str(obj.get("answer", "")).strip()
            cat = str(obj.get("category", "General Knowledge")).strip() or "General Knowledge"
            title = str(obj.get("title", "10-Second Trivia #shorts")).strip() or "10-Second Trivia #shorts"
            desc = str(obj.get("description", "Can you answer in 10 seconds?\n\n#shorts #trivia #quiz")).strip()
            tags = clamp_list(_coerce_list(obj.get("tags")), 450)
            hashtags = _ensure_hashtag_short(_coerce_list(obj.get("hashtags")))

            if len(title) > 90:
                title = title[:87].rstrip() + "..."

            if not _looks_safe(q, a):
                raise ValueError("unsafe/invalid question")
            if state.is_used(q):
                raise ValueError("duplicate question")
            if not tags:
                tags = ["trivia", "quiz", "shorts", "general knowledge"]
            if not hashtags:
                hashtags = ["#shorts", "#trivia", "#quiz"]

            return ShortSpec(question=q, answer=a, category=cat, title=title, description=desc, tags=tags, hashtags=hashtags)
        except Exception as e:
            log.warning("Question generation attempt %d failed: %s", attempt, str(e))

    for _ in range(1, 50):
        spec = _local_bank(rng)
        if _looks_safe(spec.question, spec.answer) and not state.is_used(spec.question):
            return spec
    return _local_bank(rng)
