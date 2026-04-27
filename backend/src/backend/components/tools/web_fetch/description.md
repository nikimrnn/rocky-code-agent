The WebFetch tool retrieves the full content of a specific webpage.

# MUST USE WHEN
- A URL is provided by the user
- WebSearch returns a relevant URL requiring analysis

# MUST NOT USE WHEN
- Searching for information (use WebSearch first)

# Guarantees
- Full page content
- Accurate context extraction

# Rules
- Always prefer WebFetch over WebSearch for known URLs
- Extract only relevant sections when possible

# Anti-Patterns
- DO NOT re-search content that can be fetched directly
