# Source notes

This skill was authored from current public documentation and examples, primarily:

- D2 documentation: https://d2lang.com/
- D2 tour introduction: https://d2lang.com/tour/intro/
- D2 install docs: https://d2lang.com/tour/install/
- D2 shapes: https://d2lang.com/tour/shapes/
- D2 connections: https://d2lang.com/tour/connections/
- D2 containers: https://d2lang.com/tour/containers/
- D2 text/code/LaTeX: https://d2lang.com/tour/text/
- D2 icons/images: https://d2lang.com/tour/icons/
- D2 SQL tables: https://d2lang.com/tour/sql-tables/
- D2 UML classes: https://d2lang.com/tour/uml-classes/
- D2 sequence diagrams: https://d2lang.com/tour/sequence-diagrams/
- D2 grid diagrams: https://d2lang.com/tour/grid-diagrams/
- D2 themes, styles, classes, positions, layouts, imports, composition, exports, variables: pages under https://d2lang.com/tour/
- D2 legends: https://d2lang.com/tour/legend/
- D2 fonts: https://d2lang.com/tour/fonts/
- D2 dimensions: https://d2lang.com/tour/dimensions/
- D2 sketch mode: https://d2lang.com/tour/sketch/
- D2 interactive (tooltips/links): https://d2lang.com/tour/interactive/
- D2 ELK layout: https://d2lang.com/tour/elk/
- D2 TALA layout: https://d2lang.com/tour/tala/
- D2 CLI manual: https://d2lang.com/tour/man/
- D2 0.7.0 release notes (`d2 validate`): https://d2lang.com/releases/0.7.0/
- D2 0.7.1 release notes (ASCII output, legend improvements): https://d2lang.com/releases/0.7.1/
- D2 repository, releases, and install notes: https://github.com/terrastruct/d2
- Agent Skills specification: https://agentskills.io/specification
- Claude Code Agent Skills docs: https://code.claude.com/docs/en/agent-sdk/skills
- OpenAI Codex Agent Skills docs: https://developers.openai.com/codex/skills
- Hermes Agent Skills docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Pi Skills docs: https://pi.dev/docs/latest/skills

Operational assumptions:

- The skill is intentionally portable and uses the `SKILL.md` frontmatter required by the Agent Skills standard.
- Helper scripts are optional. They assume the `d2` CLI is installed and available on `PATH`.
- Remote icon examples depend on network access at render time.
- Behaviour was verified against D2 **0.7.1**, which is what CI pins. Layout output changes between releases.

Behaviour established by testing against D2 0.7.1 rather than taken from the docs:

- `d2 validate` parses but does not compile: it succeeds on source with unresolved keys, nonexistent indexed edges, missing imports, and unbundlable local icons.
- A `**` recursive glob and a `vars` block cannot coexist in one file; the combination fails with `"style" needs a value`. Hence type sizes on classes rather than a global glob.
- `vars.d2-legend` has no title key (the heading is always "Legend"), and connection endpoints that are not already legend objects appear as extra swatches.
- Layered style-pack imports work: a pack can spread another pack and override `classes.<name>.style.<key>` afterwards, including keys the base already set.
- `style.fill: transparent` is the one fill value safe to set in a color-free pack; unlike a hex value it does not fight the active theme in either mode.
- The PNG/PDF/PPTX pipeline downloads a Playwright browser on first use and simply fails where that download is blocked; a local headless browser screenshotting the SVG is a working substitute.

Design guidance (visual hierarchy, typography scale, color semantics, edge hierarchy, density heuristics, the rubric) is general information-design practice applied to D2, not a restatement of the D2 documentation.
