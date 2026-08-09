"""Guardrail: no `signalbot._generated` type should leak through the public API.

`signalbot._generated` is regenerated wholesale from the signal-cli-rest-api JSON
schema and is an implementation detail. Every public class should be a domain type
(or a deliberately-allowlisted enum), never the generated class itself and never a
generated class nested inside one of its fields.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import get_args, get_origin

from pydantic import BaseModel

import signalbot
from signalbot._generated import (
    AddMembers,
    EditGroup,
    GroupLink,
    ReceiptType,
    SendMessages,
    TextMode,
)

# Enums are structurally exempt from the wrapper pattern used everywhere else in
# this file: Python cannot subclass an Enum that already has members, so "wrap it"
# would mean duplicating every value by hand. A closed value set also has no
# structural-drift risk from codegen regeneration, so re-exporting them as-is is
# fine.
_ENUM_ALLOWLIST = {
    TextMode,
    ReceiptType,
    GroupLink,
    AddMembers,
    EditGroup,
    SendMessages,
}


def _is_underscore_prefixed(module_name: str) -> bool:
    return any(part.startswith("_") for part in module_name.split("."))


def _public_modules() -> list[tuple[str, object]]:
    modules: list[tuple[str, object]] = [("signalbot", signalbot)]
    for module_info in pkgutil.walk_packages(signalbot.__path__, prefix="signalbot."):
        if _is_underscore_prefixed(module_info.name):
            continue
        module = importlib.import_module(module_info.name)
        modules.append((module_info.name, module))
    return modules


def _collect_public_classes() -> dict[str, type]:
    classes: dict[str, type] = {}
    for module_name, module in _public_modules():
        for name in getattr(module, "__all__", []):
            obj = getattr(module, name)
            if isinstance(obj, type):
                classes[f"{module_name}.{name}"] = obj
    return classes


def _leaf_types(annotation: object) -> list[type]:
    """Unwrap Optional/list/dict/union annotations down to their leaf types."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is None or not args:
        return [annotation] if isinstance(annotation, type) else []

    leaves = []
    for arg in args:
        if arg is type(None):
            continue
        leaves.extend(_leaf_types(arg))
    return leaves


def _qualname(leaf: type) -> str:
    return f"{leaf.__module__}.{leaf.__qualname__}"


def _is_generated_leak(leaf: type) -> bool:
    return leaf.__module__.startswith("signalbot._generated") and (
        leaf not in _ENUM_ALLOWLIST
    )


def _walk_model_fields(
    cls: type[BaseModel], path: str, visited: set[type], errors: list[str]
) -> None:
    if cls in visited:
        return
    visited.add(cls)

    for field_name, field_info in cls.model_fields.items():
        field_path = f"{path}.{field_name}"
        for leaf in _leaf_types(field_info.annotation):
            if _is_generated_leak(leaf):
                errors.append(f"{field_path} -> {_qualname(leaf)}")
            if issubclass(leaf, BaseModel):
                _walk_model_fields(
                    leaf, f"{field_path}->{leaf.__name__}", visited, errors
                )


def test_no_generated_types_leak_through_public_api():
    classes = _collect_public_classes()
    errors: list[str] = []

    for full_name, cls in classes.items():
        if _is_generated_leak(cls):
            errors.append(f"{full_name} is {_qualname(cls)}")

    visited: set[type] = set()
    for full_name, cls in classes.items():
        if isinstance(cls, type) and issubclass(cls, BaseModel):
            _walk_model_fields(cls, full_name, visited, errors)

    assert not errors, (
        "signalbot._generated types leak through the public API:\n"
        + "\n".join(sorted(errors))
    )


def test_no_generated_required_field_weakened_to_optional():
    """A domain class may narrow a `_generated` base's field to point at another
    wrapped type (e.g. `GroupEntry.permissions`) - pydantic validates that on
    every construction, so it's sound even though it's an override. What it must
    never do is turn a field that's required on the generated base into an
    optional one on the subclass: that breaks substitutability wherever the
    subclass is handed to code that trusts the generated base's contract (e.g. a
    `_client` method typed on the generated request), and pydantic can't catch it
    for you. `ty` (what actually runs in CI) has no equivalent static check, so
    this is the only enforcement.
    """
    classes = _collect_public_classes()
    errors: list[str] = []

    for full_name, cls in classes.items():
        if not (isinstance(cls, type) and issubclass(cls, BaseModel)):
            continue
        for base in cls.__bases__:
            if not (
                issubclass(base, BaseModel)
                and base.__module__.startswith("signalbot._generated")
            ):
                continue
            for field_name, field_info in cls.model_fields.items():
                base_field = base.model_fields.get(field_name)
                if (
                    base_field is not None
                    and base_field.is_required()
                    and not field_info.is_required()
                ):
                    errors.append(f"{full_name}.{field_name}")

    assert not errors, (
        "Field(s) required on a signalbot._generated base class were weakened to "
        "optional on the public subclass, breaking substitutability wherever the "
        "subclass stands in for its generated base - use a standalone model with "
        "a to_generated() conversion instead (see SendMessage/UpdateGroup):\n"
        + "\n".join(sorted(errors))
    )
