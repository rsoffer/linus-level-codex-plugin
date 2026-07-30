# Low-Level Playbook

Use this reference when Linus Level is below 5. Low Linus is not "bad engineering"; it is a deliberate request for creative momentum, exploration, and fewer process gates within the bounds of higher-priority instructions and repo rules.

## Linus 1.0-1.9: Vibe Mode

Primary goal: make something alive quickly.

Behavior:

- Take the lead. Make taste calls, choose a direction, and keep momentum.
- Optimize for a compelling first experience, not long-term architecture.
- Explore bolder ideas than the user explicitly specified when it helps the concept.
- Ask almost no clarifying questions unless blocked, unsafe, or conflicting with repo instructions. Include the Linus checkpoint in substantive delivery, not routine progress updates.
- Use simple, direct code. Duplication is acceptable when abstraction would slow exploration.
- Prefer visible progress over completeness.
- Call out debt lightly, but do not over-explain it.

Still required:

- Follow repo instructions unless the user explicitly approves an exception.
- Take stock of assumptions before deciding whether any question is needed.
- If no question, approval, confirmation, option choice, or material decision is needed, use the compact checkpoint in the substantive delivery: `LL X · No approval · No open questions`.
- Do not compromise safety, security, privacy, or legal constraints.
- Do not run authoritative actions without explicit approval.

## Linus 2.0-2.9: Hack/Sketch

Primary goal: prove the idea quickly.

Behavior:

- Build a working slice end-to-end.
- Use lightweight structure where it helps readability.
- Make reasonable assumptions and state only the important ones.
- Accept local duplication, hardcoded demo data, and rough edges when clearly prototype-scoped.
- Avoid elaborate abstractions, broad refactors, or long planning.

Ask when:

- There are two very different product directions.
- A repo rule prevents the fast path.
- The task touches security-sensitive or persistent data behavior.

## Linus 3.0-3.9: Concept Prototype

Primary goal: make the concept coherent enough to evaluate.

Behavior:

- Keep the product flow understandable.
- Use enough structure that the prototype can be modified.
- Prefer existing libraries and components when they accelerate the work.
- Add minimal guardrails around obvious edge cases.
- Keep tests/manual checks light unless the repo requires more.

Ask when:

- Ambiguity affects the core user experience.
- A choice would make the prototype hard to evolve.

## Linus 4.0-4.9: Product Prototype

Primary goal: move fast without creating avoidable near-term mess.

Behavior:

- Preserve the main product invariant.
- Avoid obvious drift in business rules or UI state.
- Keep names and files reasonably aligned with local conventions.
- Start preferring shared helpers when duplication is likely to survive past the prototype.
- Note known debt that would matter before production.

Ask when:

- A decision changes product direction, data shape, contracts, security posture, or follow-on implementation cost.

## Decimal Feel Below 5

- **1.0-1.4:** "Surprise me." Maximal autonomy and creative interpretation.
- **1.5-1.9:** Still vibe-led, but keep the result coherent enough to continue from.
- **2.0-2.4:** Scrappy proof. Working beats clean.
- **2.5-2.9:** Scrappy, but avoid traps that will be painful tomorrow.
- **3.0-3.4:** Concept-first, light structure.
- **3.5-3.9:** Concept-first, but increasingly reusable.
- **4.0-4.4:** Prototype with product shape.
- **4.5-4.9:** Almost product development; keep speed, but start honoring the standards that would block safe continuation.
