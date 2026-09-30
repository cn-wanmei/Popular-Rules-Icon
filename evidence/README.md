# Evidence Layer (R8)

Per-service optional evidence packs:

```text
evidence/<service_id>/
  source.json      # url, retrieved_at, source_class, sha256
  notes.md         # human review notes
```

Machine fields also live in `config/remote_provenance.yaml` (freeze provenance).
