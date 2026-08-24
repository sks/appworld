# Genie routing skills and probes

Essay playbooks and AppWorld SDK probes used by the Genie
`examples/appworld-routing` harness (see stackgenhq/genie).

## Skills

Each subdirectory under `skills/` is a Genie skill (`SKILL.md` with YAML
frontmatter). Genie loads them via:

```toml
[skill_load]
skills_roots = ["${APPWORLD_SRC}/experiments/genie_routing/skills"]
```

Set `APPWORLD_SRC` to this AppWorld checkout when running Genie.

## Probes

`probes/` contains one-off AppWorld API probes (import `from appworld import
AppWorld`) for debugging task worlds. They are not part of Genie.
