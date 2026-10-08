# After production promote — sync Collection pins

When `config/release-pointers.yaml` **production** or **rollback** changes:

1. Open Collection PR (or direct commit) updating:
   - `config/icon_v6.yaml` (`v6.release_id`, `manifest_path`, `rollback.*`)
   - `config/icon_docs.yaml` (`production_release_id`)
2. Collection gate: `python scripts/check_icon_pointers.py` (in validate.yml)
3. See Collection [`docs/ICON_POINTER_SYNC.md`](https://github.com/cn-wanmei/Popular-Rules-Collection/blob/main/docs/ICON_POINTER_SYNC.md)

SSOT for release IDs remains **this file's** `release-pointers.yaml`.
