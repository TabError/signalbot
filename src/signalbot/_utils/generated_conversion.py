from typing import TypeVar, overload

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
G = TypeVar("G", bound=BaseModel)


@overload
def from_generated(wrapper_cls: type[T], generated: BaseModel) -> T: ...
@overload
def from_generated(wrapper_cls: type[T], generated: None) -> None: ...
def from_generated(wrapper_cls: type[T], generated: BaseModel | None) -> T | None:
    """Build a public wrapper instance from its generated counterpart."""
    if generated is None:
        return None
    return wrapper_cls.model_validate(generated.model_dump(by_alias=True))


@overload
def from_generated_list(wrapper_cls: type[T], generated: list[G]) -> list[T]: ...
@overload
def from_generated_list(wrapper_cls: type[T], generated: None) -> None: ...
def from_generated_list(
    wrapper_cls: type[T], generated: list[G] | None
) -> list[T] | None:
    """Build a list of public wrapper instances from their generated counterparts."""
    if generated is None:
        return None
    return [from_generated(wrapper_cls, item) for item in generated]
