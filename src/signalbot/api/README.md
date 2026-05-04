# API classes

The classes in the [generated folder](./generated/) were automatically generated from the [JSON Schema](https://json-schema.org/) files in the [json_schema folder](./json_schema/).
To convert from JSON Schema to pydantic dataclasses the [datamodel-code-generator tool](https://datamodel-code-generator.koxudaxi.dev/) is used.

Those files were copied over from the [signal-cli-rest-api repository](https://bbernhard.github.io/signal-cli-rest-api/).
From this [PR](https://github.com/AsamK/signal-cli/pull/1952).

TODO: simplify this via https://datamodel-code-generator.koxudaxi.dev/pyproject_toml/#named-profiles

To generate the files run this command at the root of the repository

```bash
uv run datamodel-codegen \
--input ./src/signalbot/api/json_schema/signal-cli-rest-api.json \
--input-file-type jsonschema \
--aliases src/signalbot/api/json_schema_receive_aliases.json \
--output-model-type pydantic_v2.BaseModel \
--formatters ruff-check ruff-format \
--snake-case-field \
--disable-timestamp \
--use-exact-imports \
--use-default-kwarg \
--module-split-mode=single \
--no-use-type-checking-imports \
--all-exports-scope recursive \
--all-exports-collision-strategy minimal-prefix \
--output ./src/signalbot/api/generated
```

## Manual modications

* Add a `serialization_alias` to the `text` field in `SendMessageV2` class in `src/signalbot/api/generated/api.py` by replacing
    ```python
    text: str | None = Field(
        default=None, validation_alias=AliasChoices("message", "text")
    )
    ```
    with
    ```python
    text: str | None = Field(
        default=None,
        validation_alias=AliasChoices("message", "text"),
        serialization_alias="message",
    )
    ```
