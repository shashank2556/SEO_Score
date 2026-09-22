from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

CheckStatus = Literal["pass", "warn", "fail", "skipped", "error"]
CheckCategory = Literal[
    "on_page",
    "technical",
    "social",
    "performance",
    "accessibility",
    "ai_readability",
]
CheckScope = Literal["page", "site"]


@dataclass(frozen=True, slots=True)
class CheckDefinition:
    id: str
    name: str
    category: CheckCategory
    description: str
    default_weight: float
    scope: CheckScope = "page"


@dataclass(slots=True)
class CheckResult:
    id: str
    name: str
    category: CheckCategory
    status: CheckStatus
    description: str
    evidence: str
    fix: str
    weight: float
    score: float
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "description": self.description,
            "evidence": self.evidence,
            "fix": self.fix,
            "weight": self.weight,
            "score": self.score,
            "meta": self.meta,
        }


@dataclass(slots=True)
class RedirectHop:
    url: str
    status_code: int


@dataclass(slots=True)
class Heading:
    level: Literal[1, 2, 3, 4, 5, 6]
    text: str


@dataclass(slots=True)
class PageLink:
    href: str
    text: str
    rel: list[str]
    internal: bool


@dataclass(slots=True)
class PageImage:
    src: str
    alt: str | None
    width: int | None = None
    height: int | None = None


@dataclass(slots=True)
class PageSnapshot:
    requested_url: str
    final_url: str
    status_code: int
    redirect_chain: list[RedirectHop]
    headers: dict[str, str]
    html: str
    text: str
    title: str | None
    meta: dict[str, str]
    headings: list[Heading]
    links: list[PageLink]
    images: list[PageImage]
    scripts: list[str]
    stylesheets: list[str]
    json_ld: list[Any]
    canonical: str | None
    hreflang: list[dict[str, str]]
    word_count: int


@dataclass(slots=True)
class FetchedText:
    status_code: int
    body: str | None


@dataclass(slots=True)
class SiteContext:
    root_url: str
    pages: list[PageSnapshot]


@dataclass(slots=True)
class CheckContext:
    snapshot: PageSnapshot
    robots_txt: FetchedText | None = None
    sitemap_xml: FetchedText | None = None
    llms_txt: FetchedText | None = None
    pagespeed: dict[str, Any] | None = None
    axe: dict[str, Any] | None = None
    site: SiteContext | None = None


class CheckModule(Protocol):
    definition: CheckDefinition

    def run(self, ctx: CheckContext) -> CheckResult: ...
