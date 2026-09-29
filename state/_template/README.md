# state branch layout

On the `state` branch, files live at:

```text
state/services/<service_id>.json
```

This `_template` on `main` documents the shape only. Bots must not write runtime state on `main`.
