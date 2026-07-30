# Levels 1-4

Use this reference for Linus `1.0-4.9`. For richer creative/prototype behavior, also read `low-level-playbook.md`.

## Linus 1.0-1.9

Non-negotiable:

- Follow higher-priority instructions and safety constraints.
- Include the Linus checkpoint in substantive final or user-gated responses. Take stock of assumptions, ask only blocking, safety, or repo-conflict questions at this level, and keep routine progress updates lightweight.
- Do not break repo rules unless the user explicitly approves a scoped exception.
- Keep the work understandable enough that a human can continue from it.

Expected:

- Lead creatively and make strong taste calls.
- Optimize for exploration, speed, and a vivid first result.
- Prefer direct implementation over architecture; new paradigms are acceptable when they serve the sketch and do not violate repo rules.
- Accept duplication and rough edges when clearly prototype-local.
- Keep final notes short: what exists, how to try it, and the biggest known caveat.

## Linus 2.0-2.9

Non-negotiable:

- Avoid choices that create irreversible state, security risk, or repo-rule violations.
- Label intentional shortcuts if they could matter later.

Expected:

- Build a working sketch or proof of concept.
- Make reasonable assumptions without stopping for minor ambiguity.
- Use lightweight structure only where it keeps momentum.
- Freely introduce local-only patterns or libraries when they materially accelerate the prototype and do not create security or persistent-state risk.
- Do not over-test; use a quick smoke check or manual verification when appropriate.

## Linus 3.0-3.9

Non-negotiable:

- Preserve the core concept and obvious user flow.
- Avoid hard-to-undo choices in data shape, contracts, or security-sensitive areas.

Expected:

- Make the prototype coherent and modifiable.
- Add basic edge handling for likely demo-breaking cases.
- Follow local patterns when cheap, but do not let pattern archaeology stall the concept. New patterns are acceptable if they stay clearly prototype-scoped.

## Linus 4.0-4.9

Non-negotiable:

- Preserve the main product invariant.
- Do not duplicate business rules or state authority if that duplication is likely to survive into production.

Expected:

- Move fast while keeping the code easy to evolve.
- Start preferring shared helpers/constants when the same rule appears more than once.
- Prefer local codebase conventions when the prototype is intended to continue into production.
- Note debt that should be cleaned up before production use.
