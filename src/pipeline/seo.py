from dataclasses import dataclass


@dataclass(frozen=True)
class SeoPack:
    title: str
    description: str
    tags: list[str]


def build_seo(question: str, answer: str, category: str) -> SeoPack:
    title = f"{question} | Quick Quiz"
    tags = [
        "quiz",
        "shorts",
        "trivia",
        "guess",
        category,
        "viral",
        "challenge",
    ]
    hashtags = "#shorts #quiz #trivia #challenge"
    description = (
        f"{question}\nAnswer revealed at the end.\n{hashtags}\n"
        "Subscribe for daily quiz shorts!"
    )
    return SeoPack(title=title, description=description, tags=tags)
