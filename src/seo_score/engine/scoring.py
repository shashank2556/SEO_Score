from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from seo_score.engine.types import CheckCategory, CheckResult


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    categories: dict[str, float]
    checks: dict[str, float]


def default_config_path() -> Path:
    env = os.environ.get("SCORING_CONFIG")
    if env:
        return Path(env)
    for parent in [Path.cwd(), *Path(__file__).resolve().parents]:
        candidate = parent / "config" / "scoring.yaml"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("config/scoring.yaml not found")


def load_scoring_config(path: Path | None = None) -> ScoringConfig:
    data: dict[str, Any] = yaml.safe_load((path or default_config_path()).read_text()) or {}
    return ScoringConfig(
        categories={str(k): float(v) for k, v in (data.get("categories") or {}).items()},
        checks={str(k): float(v) for k, v in (data.get("checks") or {}).items()},
    )


@dataclass(slots=True)
class CategoryScore:
    category: CheckCategory
    score: float
    weight: float


@dataclass(slots=True)
class AggregatedScore:
    overall: int
    categories: dict[str, float]


def weight_for(result: CheckResult, config: ScoringConfig) -> float:
    return config.checks.get(result.id, result.weight)


def aggregate(results: list[CheckResult], config: ScoringConfig) -> AggregatedScore:
    """Category score = weighted average of its checks; overall = weighted categories.

    skipped/error checks are excluded from the denominator so a missing PSI
    key does not silently tank the whole audit.
    """
    by_cat: dict[str, list[CheckResult]] = {}
    for result in results:
        by_cat.setdefault(result.category, []).append(result)

    category_scores: dict[str, float] = {}
    for category, items in by_cat.items():
        scored = [r for r in items if r.status not in ("skipped", "error")]
        if not scored:
            continue
        total_w = sum(weight_for(r, config) for r in scored)
        if total_w <= 0:
            continue
        category_scores[category] = round(
            sum(r.score * weight_for(r, config) for r in scored) / total_w, 2
        )

    cat_weight_sum = 0.0
    overall_num = 0.0
    for category, score in category_scores.items():
        w = config.categories.get(category, 0.0)
        if w <= 0:
            continue
        cat_weight_sum += w
        overall_num += score * w

    overall = int(round(overall_num / cat_weight_sum)) if cat_weight_sum else 0
    return AggregatedScore(overall=max(0, min(100, overall)), categories=category_scores)
