---
name: repo-diagrams
description: Create or update source-backed architecture, execution flow, dependency, sequence, or state diagrams for a code repository. Use for README diagrams, engineering onboarding, and interactive repository walkthroughs.
---

# Repository diagrams

## Choose the view and format

- Use Mermaid by default for README files, engineering docs, pull requests, and ordinary repository diagram requests. Use a fenced `mermaid` block in Markdown or a standalone `.mmd` file when requested.
- Use a flowchart for system boundaries and processes, a sequence diagram for ordered calls and replies, and a state diagram for state transitions. Give an overview and a representative flow separate diagrams when readers need both.
- Use Archify when the user requests it or needs interactive HTML with clickable nodes, dependencies, or code evidence. Read [the Archify workflow](references/archify.md) for this mode.
- Respect an explicit output format. A text-only summary stays in prose.

## Trace the code

1. Start from the actual entry point, registration, or deployment configuration. Follow the requested path through callers, handlers, and I/O. Use the current checkout for documentation and use a pinned revision when the output asserts revision-specific evidence.
2. Show the units that help the intended reader explain the system. Give arrows a direction and a meaningful operation. For dependency diagrams, establish actual imports or configured dependencies. For execution flows, follow actual calls and include an error or retry when it affects the outcome.
3. Record repository-relative `path:line` or `path:start-end` references for key components, edges, and branch conditions. Put them near the diagram in Markdown or in Mermaid comments for a standalone source file. Label unresolved connections as unverified where they appear.

## Verify and deliver

- Use an available Mermaid renderer to parse and inspect the target output. Check arrow direction, labels, and whether readers can see the critical branch at the intended width. If a renderer is unavailable, state that the source was reviewed.
- Report the artifact path, rendering or interaction checks actually run, and any unresolved source claims.
