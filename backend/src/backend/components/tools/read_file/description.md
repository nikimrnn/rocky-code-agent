The ReadFile tool reads the contents of a known file path.

# MUST USE WHEN
- The exact file path is known

# MUST NOT USE WHEN
- The file path is unknown → use Bash for discovery first

# Rules
- Only reads content
- Does NOT modify anything

# Error Handling
- If file not found → THEN use Bash to locate it

# Anti-Patterns
- DO NOT use Bash to read files
- DO NOT assume file contents without reading
