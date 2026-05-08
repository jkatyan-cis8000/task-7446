# AGENTS.md

Repository knowledge map. Read this first; follow the pointers.

## Layout

```
ARCHITECTURE.md     — domain map and package structure

docs/
└── design-docs/         — architectural decisions and design notes
```

## Conventions

- Commits identify the author: `git -c user.name=<name> commit -m "..."`
- `ARCHITECTURE.md` is updated by team-lead only
- Send design decisions and discovered debt to team-lead via `send_message`; team-lead records them
- Stale docs are worse than no docs; update when code changes
