# Question Patterns

Use these patterns to ask fewer, better questions as Linus Level rises.

## Principles

- Identify assumptions before writing the checkpoint required by `SKILL.md` for substantive final or user-gated responses. Keep routine progress updates lightweight.
- Treat approval as a derived gate: if the agent is waiting on the user before its next action, approval is needed. Never pair `No approval` or `No open questions` with unresolved user input.
- Ask only when the answer changes the work.
- Prefer one or two precise questions over a broad questionnaire.
- State why the question matters.
- Good questions usually come from a specific assumption: name the assumption internally, then ask only if being wrong would matter at the active level.
- Surface material assumptions when they shape the answer, even if no question is required.
- If local context answers it, use local context.
- Offer a default only when it is safe and reversible.
- At high Linus Levels, do not bury a material assumption in the final response after already acting.
- At Linus 8+, asking a narrow, source-of-truth question is forward progress when an unknown affects correctness, contracts, public claims, legal/commercial wording, operations, security, data, or production behavior.
- At Linus 8.5+, when the intended next step for a material action is unverified, approval should be `yes` until that assumption is surfaced and confirmed.
- When multiple viable material options are presented and the user must choose or approve one, treat that as an approval gate and open decision even if no sentence ends with a question mark.

## Good Questions

Business rule:

```text
Before I change this: should this ranking rule apply only to Session Finder, or is it a shared forecast-quality rule used elsewhere? That determines whether I update a local filter or the shared scoring source of truth.
```

Contract change:

```text
This would remove a response field the UI may depend on. Do you want an explicit contract migration, or should I preserve the key and change only the internal derivation?
```

Security:

```text
This endpoint can be called by admins today. Should the new action require the same admin role, or a narrower permission? I do not want to guess on authorization semantics.
```

Architecture:

```text
There are two viable fixes: centralize the rule in the shared service, or keep this screen-specific. Centralizing is safer for drift but touches more callers. Which direction do you want?
```

New pattern/dependency:

```text
This can be solved with the existing state model, or by introducing a new client-side store. The new store reduces local wiring but adds another source of truth. At this Linus Level, should I stay with the existing pattern?
```

External submission / commercial copy:

```text
I found the public site URL in the README, but I do not see the required third-party account URL in the repo or docs. What exact account URL should I use? I do not want to invent an external identifier in a submission.
```

Repo-rule conflict:

```text
You asked for Linus 2, but this repo requires docs with workflow/config changes. Should I keep that repo standard while moving quickly, or are you explicitly approving a temporary exception?
```

Unverified intended next step:

```text
You said the settings-page change is partially wrong. I can update the current implementation, undo only the settings-page edits, or step back and propose a different approach. Which direction do you want before I touch the worktree?
```

## Weak Questions To Avoid

- "What framework is this?" when the repo already shows it.
- "Should I add tests?" at Linus 7+ when behavior changed and repo rules expect tests.
- "Do you want clean code?" because the answer is not actionable.
- Long intake forms before reading local context.
- Asking for approval to follow explicit repo instructions.
- "Is this correct?" after drafting legal/commercial or external-submission copy that contains guessed URLs, account IDs, policy claims, volumes, or production details.

## Proceeding Under Assumptions

At Linus 1-2, take the lead. Proceed under creative assumptions, choose tastefully, and note only the assumptions that materially shape the result.

At Linus 3-4, proceed under reasonable assumptions, but ask when the answer changes the concept, product direction, data shape, or evolution path.

At Linus 5-7, proceed under assumptions only when local patterns strongly support them and the cost of being wrong is low.

At Linus 8+, preflight material facts before drafting or acting. Do not proceed under assumptions that affect correctness, contracts, business logic, public claims, legal/commercial wording, security, data, operations, architecture, or accepted debt.

For decimals, treat `.7-.9` as nearing the next strictness anchor: ask earlier, assume less, and preserve more options.

Even when proceeding under assumptions at low levels, still take stock of them and include the compact checkpoint in the substantive delivery.
