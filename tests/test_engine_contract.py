from seo_score.engine.registry import clear_registry, get_checks, register_check
from seo_score.engine.scoring import ScoringConfig, aggregate
from seo_score.engine.types import CheckDefinition, CheckResult


class DummyCheck:
    def __init__(self, check_id: str, category: str = "on_page") -> None:
        self.definition = CheckDefinition(
            id=check_id,
            name=check_id,
            category=category,  # type: ignore[arg-type]
            description="test",
            default_weight=1,
        )

    def run(self, ctx):  # pragma: no cover
        raise NotImplementedError


def test_register_and_filter_checks():
    clear_registry()
    register_check(DummyCheck("on_page.title_length"))
    register_check(DummyCheck("technical.https", "technical"))
    assert len(get_checks()) == 2
    assert len(get_checks(category="on_page")) == 1
    assert [m.definition.id for m in get_checks(ids=["technical.https"])] == ["technical.https"]
    clear_registry()


def test_aggregate_weighted_categories():
    config = ScoringConfig(
        categories={"on_page": 50, "technical": 50},
        checks={"on_page.title_length": 8, "technical.https": 10},
    )
    results = [
        CheckResult(
            id="on_page.title_length",
            name="Title",
            category="on_page",
            status="pass",
            description="",
            evidence="",
            fix="",
            weight=8,
            score=100,
        ),
        CheckResult(
            id="technical.https",
            name="HTTPS",
            category="technical",
            status="fail",
            description="",
            evidence="",
            fix="",
            weight=10,
            score=0,
        ),
    ]
    scored = aggregate(results, config)
    assert scored.categories["on_page"] == 100
    assert scored.categories["technical"] == 0
    assert scored.overall == 50
