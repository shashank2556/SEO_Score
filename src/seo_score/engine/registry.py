from __future__ import annotations

from seo_score.engine.types import CheckCategory, CheckModule

_REGISTRY: dict[str, CheckModule] = {}


def register_check(module: CheckModule) -> CheckModule:
    """Register a check module. Import the module once at process start."""
    check_id = module.definition.id
    if check_id in _REGISTRY:
        raise ValueError(f"Duplicate check id: {check_id}")
    _REGISTRY[check_id] = module
    return module


def get_checks(
    *,
    category: CheckCategory | None = None,
    ids: list[str] | None = None,
) -> list[CheckModule]:
    modules = list(_REGISTRY.values())
    if category is not None:
        modules = [m for m in modules if m.definition.category == category]
    if ids is not None:
        allowed = set(ids)
        modules = [m for m in modules if m.definition.id in allowed]
    return modules


def clear_registry() -> None:
    """Test helper."""
    _REGISTRY.clear()
