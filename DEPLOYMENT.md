# Deployment

This repository supports four distribution shapes:

- Hosted skill upload for OpenAI and Claude
- Filesystem installs for Codex, Claude Code, and other `SKILL.md`-aware agent workflows
- Hook-enabled Codex and Claude Code plugin installs
- GitHub release distribution

The canonical prose lives under `skills/linus-level/` and works in every
distribution. The shared runtime under `hooks/` is an optional plugin guardrail;
hosted and filesystem skill-only installs do not execute it.
The hook runtime requires Python 3.8+ and has no third-party dependencies.
Claude Code on Windows requires `python3` on `PATH` for the optional hook
runtime; Codex uses the plugin's `py -3` Windows command override.

## Marketplace Inventory

Superpowers currently points users at several agent marketplaces and install surfaces:

| Surface | Superpowers path | Linus Level implication |
|---|---|---|
| Claude Code official marketplace | `/plugin install superpowers@claude-plugins-official` | Requires Anthropic marketplace submission after validating `.claude-plugin/`. |
| Superpowers Claude marketplace | `/plugin marketplace add obra/superpowers-marketplace` | Same Claude marketplace format; Linus Level already has `.claude-plugin/marketplace.json`. |
| Codex official marketplace | Codex CLI/App plugin search | Requires Codex plugin publication or inclusion in a marketplace/index. |
| Factory Droid | `droid plugin marketplace add https://github.com/obra/superpowers` | Requires Factory-compatible plugin metadata or a compatible marketplace repo. |
| Gemini CLI | `gemini extensions install https://github.com/obra/superpowers` | Requires `gemini-extension.json` at the repo or release archive root to publish as a Gemini extension. |
| OpenCode | `opencode.json` plugin entry with `git+https://...` | Can use OpenCode's plugin package style or direct `SKILL.md` discovery paths. |
| Cursor | `/add-plugin superpowers` | Requires Cursor plugin marketplace submission/availability; details appear marketplace-managed rather than repo-only. |
| GitHub Copilot CLI | `copilot plugin marketplace add ...` then `copilot plugin install ...` | Requires Copilot CLI plugin metadata and marketplace catalog support. |

Additional relevant marketplaces and indexes found during research:

| Surface | Publishing signal | Notes |
|---|---|---|
| Claude Code plugin marketplaces | Create `.claude-plugin/marketplace.json`, host on GitHub, test with `/plugin marketplace add`, then users install `plugin@marketplace`. | Anthropic docs recommend GitHub hosting and say plugin versions only update for users when the manifest version changes, unless omitted and commit SHA versioning is used. |
| Codex / OpenAI plugins | OpenAI's `openai/plugins` repo documents curated plugin examples under `plugins/<name>/` with `.codex-plugin/plugin.json`. | Current public third-party distribution is still mostly GitHub/local marketplace driven; keep `.codex-plugin/plugin.json` valid and scanner-ready. |
| Codex Marketplace (`codex-marketplace.com`) | Submit or index GitHub plugin/skill repos, with install commands such as `npx codex-marketplace add owner/repo/skills/name --skill`. | Community marketplace, not OpenAI official. Useful for discoverability without a release bump if metadata is already valid. |
| Awesome Codex Plugins | Generated curated marketplace/list; recommends lint/verify with `codex-plugin-scanner`. | Good discovery target once this repo is scanner-clean. |
| Factory Droid plugins | Factory docs support marketplace add from GitHub, other git hosts, or local paths; team installs can be seeded through `.factory/settings.json`. | Factory uses `.factory-plugin/plugin.json` for native plugins, so this repo would need an adapter if we want first-class Droid install. |
| Gemini CLI extension gallery | Public GitHub repo, `gemini-cli-extension` topic, and root `gemini-extension.json`; release archives must contain `gemini-extension.json` at archive root. | This repo now has a root `gemini-extension.json`; publish by pushing a tag and keeping the GitHub topic. |
| OpenCode skills | OpenCode discovers `SKILL.md` files from `.opencode/skill/<name>/`, `.claude/skills/<name>/`, and global equivalents. | No marketplace wrapper is required for skill discovery; plugin-package publishing is separate. |
| GitHub Copilot CLI marketplaces | `marketplace.json` under `.github/plugin/`; Copilot also looks for `.claude-plugin/marketplace.json`. | This repo now has `.github/plugin/marketplace.json`; publish by pushing to GitHub. |

## Publishing Checklist

Use this checklist when publishing or submitting Linus Level somewhere new:

1. Keep the canonical source at `skills/linus-level/`.
2. Verify `SKILL.md` frontmatter has the right `name`, `description`, and compatible file layout.
3. Validate the target wrapper:
   - Claude Code: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
   - Codex: `.codex-plugin/plugin.json` and `hooks/hooks.json`
   - Gemini: `gemini-extension.json`
   - Factory Droid: `.factory-plugin/plugin.json` and `.factory-plugin/marketplace.json`
   - GitHub Copilot CLI: `.github/plugin/marketplace.json`
4. Run `bash scripts/validate.sh`.
5. Test a local install before advertising the path. For Codex and Claude Code
   plugins, inspect `/hooks` and exercise activation, resume, subagent inheritance,
   Claude-shaped payloads without Codex-only fields, checkpoint validation,
   explicit clear/logout cleanup, and stale-state expiry.
6. Update docs when the install path changes.
7. Bump version only when the target marketplace requires version-based updates or the skill behavior changes.

References:

- Codex hooks: `https://developers.openai.com/codex/config-advanced#hooks`
- Claude Code hooks: `https://code.claude.com/docs/en/hooks`
- Claude Code marketplace docs: `https://code.claude.com/docs/en/plugin-marketplaces`
- Claude Code install docs: `https://code.claude.com/docs/en/discover-plugins`
- OpenAI plugin examples: `https://github.com/openai/plugins`
- Codex Marketplace docs: `https://www.codex-marketplace.com/docs`
- Gemini extension docs: `https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md`
- Factory Droid plugin docs: `https://docs.factory.ai/cli/configuration/plugins`
- OpenCode skills docs: `https://opencode.ai/docs/skills/`
- GitHub Copilot CLI plugin reference: `https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference`

## Programmatic Marketplace Publishing

These surfaces can be published by changing files in this repository and pushing/tagging from the CLI:

| Surface | Files | Publish command |
|---|---|---|
| Gemini CLI extension gallery | `gemini-extension.json`, `skills/linus-level/` | Add the `gemini-cli-extension` GitHub topic, then push a release tag. Gemini crawls tagged public repositories daily. |
| Factory Droid marketplace | `.factory-plugin/plugin.json`, `.factory-plugin/marketplace.json`, `skills/linus-level/` | Push to GitHub. Users install with `droid plugin marketplace add https://github.com/rsoffer/linus-level-skill` and `droid plugin install linus-level@linus-level-skills`. |
| GitHub Copilot CLI marketplace | `.github/plugin/marketplace.json`, `.claude-plugin/plugin.json`, `skills/linus-level/` | Push to GitHub. Users install with `copilot plugin marketplace add https://github.com/rsoffer/linus-level-skill` and `copilot plugin install linus-level@linus-level-skills`. |
| OpenCode native skills | `skills/linus-level/SKILL.md` | No central publish step. Users symlink or copy `skills/linus-level` into `.opencode/skill/linus-level` or `~/.config/opencode/skill/linus-level`. |

OpenAI hosted skill upload and Claude Code marketplace distribution are documented below and are not repeated in this section.

## Hosted OpenAI Skill Upload

OpenAI's Skills API uploads the skill bundle itself, not the whole Codex compatibility wrapper. For this repo, the upload target is:

```text
skills/linus-level/
```

That folder contains the required `SKILL.md` frontmatter plus the reference files.
The hosted bundle excludes `hooks/`; hooks are a Codex and Claude Code plugin
capability, while the skill prose remains fully functional without them.

Existing hosted OpenAI skill:

```text
Name: linus-level
Skill id: skill_69f8f9253da881908e33a43e466cecbc04529bfc6931fcd8
```

Use this `skill_id` when publishing new hosted versions. Do not create a duplicate hosted skill unless intentionally changing the public skill identity.

Build a hosted-skill zip:

```bash
bash scripts/package-skill.sh
```

This creates:

```text
dist/linus-level.zip
```

The zip contains one top-level folder:

```text
linus-level/
  SKILL.md
  agents/openai.yaml
  references/
```

For a first-time upload, create the hosted skill with the OpenAI API:

```bash
curl -X POST 'https://api.openai.com/v1/skills' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F 'files=@./dist/linus-level.zip;type=application/zip'
```

The response includes the hosted `skill_id`. Use that id from a hosted shell environment:

```json
{
  "type": "skill_reference",
  "skill_id": "<skill_id>"
}
```

To publish a new hosted version later:

```bash
curl -X POST 'https://api.openai.com/v1/skills/<skill_id>/versions' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F 'files=@./dist/linus-level.zip;type=application/zip'
```

Set that version as the default:

```bash
curl -X POST 'https://api.openai.com/v1/skills/<skill_id>' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{ "default_version": "<version_number>" }'
```

`default_version` must be a string. For example, use `"4"` rather than `4`.

See OpenAI's Skills guide for the latest API details:

```text
https://developers.openai.com/api/docs/guides/tools-skills
```

## Claude Skill Distribution

Claude Skills use the same core shape: a directory containing `SKILL.md`, with optional `references/`, `scripts/`, and `assets/`.

### Claude Code Plugin Marketplace

Claude Code distributes community skills through plugins and plugin marketplaces. This repository is both:

- a Claude Code plugin, via `.claude-plugin/plugin.json`
- a Claude Code marketplace, via `.claude-plugin/marketplace.json`

Validate the plugin and marketplace:

```bash
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .
```

Test a local install without publishing:

```bash
claude plugin marketplace add "$(pwd)" --scope local
claude plugin install linus-level@linus-level-skills --scope local
```

Then run `/reload-plugins` inside Claude Code.

Users can install from GitHub after the marketplace files are pushed:

```text
/plugin marketplace add rsoffer/linus-level-skill
/plugin install linus-level@linus-level-skills
/reload-plugins
```

The skill is namespaced by the plugin:

```text
/linus-level:linus-level
```

For official Anthropic marketplace submission, use one of the in-app forms:

```text
https://claude.ai/settings/plugins/submit
https://platform.claude.com/plugins/submit
```

Suggested submission fields:

```text
Name: Linus Level
Plugin id: linus-level
Repository: https://github.com/rsoffer/linus-level-skill
Marketplace install source: rsoffer/linus-level-skill
Category: Productivity
License: MIT
Description: Tune Claude Code with a 1.0-10.0 engineering working-mode dial and lightweight lifecycle guardrails.
```

Before submission, confirm:

- the repository is public
- `.claude-plugin/plugin.json` validates
- `.claude-plugin/marketplace.json` validates
- local marketplace install works
- the release tag contains the Claude plugin files
- the plugin version changed since the previous release
- `/hooks` shows the shared plugin runtime events
- `bash scripts/validate.sh` passes

### Claude.ai Custom Skill Upload

For Claude Code user install:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/linus-level" ~/.claude/skills/linus-level
```

For Claude Code project install:

```text
<project>/.claude/skills/linus-level/
  SKILL.md
  references/
```

For Claude.ai upload, package the canonical skill directory:

```bash
bash scripts/package-skill.sh
```

Upload `dist/linus-level.zip` through the current Claude skill upload flow. Claude's docs require the zip to contain one top-level directory whose name matches the `name` field in `SKILL.md`.

For Claude API upload, Anthropic's Skills API uses multipart `files[]` entries rather than the OpenAI-style zip upload. Each uploaded file must be named under the same top-level directory, with `SKILL.md` at that directory root. Example pattern:

```bash
curl -X POST "https://api.anthropic.com/v1/skills" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "display_title=Linus Level" \
  -F "files[]=@skills/linus-level/SKILL.md;filename=linus-level/SKILL.md" \
  -F "files[]=@skills/linus-level/references/standards-core.md;filename=linus-level/references/standards-core.md"
```

Include the remaining `references/` files the same way. Keep all `filename=` paths inside the `linus-level/` top-level directory.

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. For repos that already use `AGENTS.md`, create a `CLAUDE.md` that imports it:

```md
@AGENTS.md
```

Docs:

```text
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
https://claude.com/docs/skills/how-to
https://code.claude.com/docs/en/agent-sdk/skills
https://code.claude.com/docs/en/memory
https://code.claude.com/docs/en/plugins
https://code.claude.com/docs/en/plugin-marketplaces
```

Claude.ai custom skill upload and Claude Code plugin marketplace distribution are separate flows. The zip upload flow is for custom skills in Claude.ai. The plugin marketplace flow is for discoverable Claude Code distribution.

## GitHub Publishing

Recommended repository name: `linus-level-skill`.

This repository keeps portable behavior in the canonical skill and adds shared
Codex/Claude Code guardrails through the plugin-level `hooks/` directory. To
publish a GitHub release:

1. Commit the skill files.
2. Push to `git@github.com:rsoffer/linus-level-skill.git`.
3. Tag a semantic version, starting from `v0.1.0`.
4. Attach `dist/linus-level.zip` as the hosted-skill upload artifact.
5. Share the repository as the source for Codex, Claude Code, and other `SKILL.md`-aware agent workflows.
