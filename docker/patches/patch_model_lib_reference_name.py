#!/usr/bin/env python3
"""Patch installed AppWorld model_lib for MusicPlayer.queue_songs evaluation.

1) Field(reference_name=...) must survive on sa_column.info (Pydantic v2 drops schema_extra).
2) field_mapping must include *_ids JSON FK lists (endswith('_id') is False for '_ids').

Without both, evaluate_task raises on music_player.queue_songs and marks queue asserts
no_op_fail even after a correct play_music.
"""

from __future__ import annotations

from pathlib import Path

PATH = Path("/usr/local/lib/python3.12/site-packages/appworld/apps/model_lib.py")


def _patch_field(text: str) -> str:
    if 'sa_column.info["reference_name"]' in text or "sa_column.info['reference_name']" in text:
        return text
    needle = '''    if json:
        kwargs["sa_column"] = Column(JSON)
    schema_extra = kwargs.get("schema_extra", {})
    if round_to is not None:
        schema_extra["round_to"] = round_to
        kwargs["schema_extra"] = schema_extra
    if reference_name is not None:
        schema_extra["reference_name"] = reference_name
        kwargs["schema_extra"] = schema_extra
    if "foreign_key" in kwargs:'''
    repl = '''    if json:
        kwargs["sa_column"] = Column(JSON)
    schema_extra = kwargs.get("schema_extra", {})
    if not isinstance(schema_extra, dict):
        schema_extra = {}
    if round_to is not None:
        schema_extra["round_to"] = round_to
        kwargs["schema_extra"] = schema_extra
    if reference_name is not None:
        schema_extra["reference_name"] = reference_name
        kwargs["schema_extra"] = schema_extra
        sa_column = kwargs.get("sa_column")
        if sa_column is not None:
            sa_column.info["reference_name"] = reference_name
    if "foreign_key" in kwargs:'''
    if needle not in text:
        raise SystemExit("Field() block not found")
    return text.replace(needle, repl, 1)


def _patch_field_reference_name(text: str) -> str:
    if "sa_column.info" in text and "def field_reference_name" in text:
        # already has sa_column lookup if we inserted it
        start = text.find("def field_reference_name")
        chunk = text[start : start + 900]
        if "sa_column.info" in chunk:
            return text
    needle = '''        if field_info is not None:
            schema_extra = getattr(field_info, "json_schema_extra", None)
            if isinstance(schema_extra, dict) and "reference_name" in schema_extra:
                return str(schema_extra["reference_name"])
        props = cls.schema()["properties"].get(field_name, {})
'''
    repl = '''        if field_info is not None:
            schema_extra = getattr(field_info, "json_schema_extra", None)
            if isinstance(schema_extra, dict) and "reference_name" in schema_extra:
                return str(schema_extra["reference_name"])
            sa_column = getattr(field_info, "sa_column", None)
            if sa_column is None:
                for meta in getattr(field_info, "metadata", ()) or ():
                    cand = getattr(meta, "sa_column", None)
                    if cand is not None:
                        sa_column = cand
                        break
            if sa_column is not None and isinstance(getattr(sa_column, "info", None), dict):
                if "reference_name" in sa_column.info:
                    return str(sa_column.info["reference_name"])
        props = cls.schema()["properties"].get(field_name, {})
'''
    if needle not in text:
        raise SystemExit("field_reference_name block not found")
    return text.replace(needle, repl, 1)


def _patch_field_mapping(text: str) -> str:
    if 'endswith(("_id", "_ids"))' in text:
        return text
    needle = 'if field_name.endswith("_id")\n            and cls.field_reference_name(field_name) != field_name'
    repl = 'if field_name.endswith(("_id", "_ids"))\n            and cls.field_reference_name(field_name) != field_name'
    if needle not in text:
        raise SystemExit("field_mapping endswith filter not found")
    return text.replace(needle, repl, 1)


def main() -> None:
    text = PATH.read_text()
    original = text
    text = _patch_field(text)
    text = _patch_field_reference_name(text)
    text = _patch_field_mapping(text)
    if text == original:
        print("model_lib already patched")
        return
    PATH.write_text(text)
    print(f"patched {PATH}")


if __name__ == "__main__":
    main()
