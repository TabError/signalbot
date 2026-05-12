# API classes

The classes in the [generated folder](./generated/) were automatically generated from the [JSON Schema](https://json-schema.org/) files in the [json_schema folder](./json_schema/).

The `signal-cli-rest-api.json` JSON Schema file was copied over from the [signal-cli-rest-api repository](https://bbernhard.github.io/signal-cli-rest-api/).
From it's documentation [url](https://bbernhard.github.io/signal-cli-rest-api/src/docs/swagger.json).

To generate the python files run this command at the root of the repository

```bash
uv run datamodel-codegen --profile signal-cli-rest-api
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
