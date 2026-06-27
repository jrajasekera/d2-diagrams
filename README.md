# d2-diagrams Agent Skill

A portable Agent Skills package for creating, editing, converting, validating, and rendering [D2](https://d2lang.com/) diagrams.

This skill is designed for Claude Code, OpenAI Codex, Hermes Agent, Pi, and other agents that implement the Agent Skills / `SKILL.md` convention.

## What's included

```text
d2-diagrams/
├── SKILL.md                         # Main skill instructions and trigger metadata
├── AGENTS.md                        # Repo-level guidance for agents that read AGENTS.md
├── MANIFEST.md                      # File-by-file inventory of the package
├── LICENSE                          # MIT license
├── references/                      # On-demand deep reference files
├── templates/                       # Starter D2 templates
├── scripts/                         # Optional helper scripts for validation/rendering/scaffolding
├── tests/                           # Smoke-test D2 source
└── agents/openai.yaml               # Optional Codex plugin metadata
```

## Install

Copy or unzip the `d2-diagrams` folder into one of your agent's skill directories.

### Claude Code

User-level:

```bash
mkdir -p ~/.claude/skills
cp -R d2-diagrams ~/.claude/skills/
```

Project-level:

```bash
mkdir -p .claude/skills
cp -R d2-diagrams .claude/skills/
```

### OpenAI Codex

User-level:

```bash
mkdir -p ~/.agents/skills
cp -R d2-diagrams ~/.agents/skills/
```

Project-level:

```bash
mkdir -p .agents/skills
cp -R d2-diagrams .agents/skills/
```

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills
cp -R d2-diagrams ~/.hermes/skills/
```

### Pi

User-level Pi directory:

```bash
mkdir -p ~/.pi/agent/skills
cp -R d2-diagrams ~/.pi/agent/skills/
```

Project-level Pi directory:

```bash
mkdir -p .pi/skills
cp -R d2-diagrams .pi/skills/
```

Pi also scans compatible `.agents/skills` directories, so the Codex locations can work for Pi as well.

## Optional D2 CLI

The skill can produce D2 source without the CLI. Install the D2 CLI when you want local validation or rendered outputs:

```bash
# Recommended install script from D2 docs
curl -fsSL https://d2lang.com/install.sh | sh -s --

d2 version
```

Other common options include Homebrew (`brew install d2`), Go (`go install oss.terrastruct.com/d2@latest`), release binaries, Windows installers, and Docker.

## Helper scripts

From the skill root:

```bash
# Validate one or more diagrams by rendering each to a temporary SVG
scripts/check_d2.sh templates/system-architecture.d2 tests/smoke.d2

# Render a diagram. Output format is inferred from extension.
scripts/render_d2.sh templates/sequence-diagram.d2 /tmp/sequence.svg

# Use layout/theme environment overrides
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh templates/system-architecture.d2 /tmp/system.svg

# List and copy starter templates
scripts/scaffold_d2.py list
scripts/scaffold_d2.py create sequence-diagram ./login-flow.d2
```

## Smoke test

```bash
scripts/check_d2.sh tests/smoke.d2
```

If `d2` is not installed, the helper script reports that clearly. The skill itself remains usable for authoring source-only diagrams.

## Validate the skill

This package follows the [Agent Skills specification](https://agentskills.io/specification). To confirm the `SKILL.md` frontmatter and naming conventions are valid, run the reference validator from the parent directory:

```bash
skills-ref validate ./d2-diagrams
```

## License

MIT. See `LICENSE`.
