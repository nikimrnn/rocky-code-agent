The WriteFile tool creates or overwrites files with full content.

# MUST USE WHEN
- Creating new files
- Fully replacing file contents

# MUST NOT USE WHEN
- Appending or partial edits → use Bash

# Safety Rules
- Overwriting is DESTRUCTIVE
- Requires explicit user intent

# Guarantees
- Atomic full write

# Anti-Patterns
- DO NOT use for partial modifications
- DO NOT overwrite files silently
