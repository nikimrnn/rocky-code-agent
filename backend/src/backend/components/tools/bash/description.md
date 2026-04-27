The Bash tool executes shell commands in a persistent session.

# MUST USE WHEN
- File discovery (unknown paths)
- Running programs, builds, installs
- Tasks impossible with other tools

# MUST NOT USE WHEN
- Reading files → use ReadFile
- Writing files → use WriteFile

# Allowed Use Cases
- find, ls (discovery)
- running scripts
- installing dependencies

# Forbidden Without Confirmation
- rm, chmod, chown
- destructive operations
- overwriting critical files

# Rules
- Prefer minimal, safe commands
- Chain commands only when necessary

# Anti-Patterns
- DO NOT replace other tools with Bash
- DO NOT perform unnecessary system operations
