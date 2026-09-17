# Claude System Directives - Token Efficiency

## Output Guidelines
- Be concise. Skip pleasantries, summaries, and conversational fluff.
- Provide direct solutions, code snippets, or diffs only.
- Do not repeat or explain the user's prompt back to them.

## Code Editing Rules
- When modifying existing files, output only the modified functions or unified diffs—do not output unchanged code blocks.
- Do not add verbose inline comments unless requested.

## Context Hygiene
- Do not load entire files into memory if a targeted line range or search query is sufficient.