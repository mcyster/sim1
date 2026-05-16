# Coding Standards

These standards apply to all code in this repository.

## Naming

- Use full words. Do not abbreviate.
- Do not use single-letter variable names (except trivial loop indices like `i` only when clearly local and short-lived).
- Prefer descriptive names that communicate intent.

## Types

- Use strong typing wherever possible.
- Add type annotations to function signatures and key variables.
- Prefer explicit types over implicit/duck typing when it improves clarity.

## Enums

- Use enums instead of string constants for states, roles, and commands.
- Do not compare against raw strings when an enum exists.

## Structure

- Keep responsibilities clear:
  - `Person` handles decisions.
  - `Firm` handles production and constraints.
  - `Economy` coordinates interactions.
- Avoid cross-layer logic leakage.

## General

- Prefer simple, readable code over cleverness.
- Minimize hidden side effects.
- Keep functions small and focused.
- Keep responses concise: do not exceed 15 lines unless explicitly requested.

## Context

- The current system state is summarized in `docs/context.md`.
- Always read `docs/context.md` before making changes.
- When making significant changes, update `docs/context.md` to keep it accurate.
