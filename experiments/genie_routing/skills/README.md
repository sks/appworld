# AppWorld routing skills (essay playbooks)

These skills teach Genie plan-mode (and solo) agents how a careful person would
finish common AppWorld errands. Each skill is a short **essay** in plain English.

Loaded by Genie when `APPWORLD_SRC` points at this checkout and
`skills_roots` includes `experiments/genie_routing/skills`.

## How agents use them

1. Call `discover_skills` (and/or `search_skill`) with keywords from the instruction.
2. Call `load_skill` on the best match before spawning workers (`create_agent`).
3. Put essay substance in the worker goal or context.

## Essay convention

- Narrative first: how you would think through the errand in this simulated world.
- Softly name apps and signing in with the password vault.
- Exact MCP tool names only in an optional short “Tools you will need” footnote.
- Frontmatter `description` paraphrases the user instruction so discovery can match.
