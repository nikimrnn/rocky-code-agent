The WebSearch tool retrieves relevant URLs and high-level summaries from the internet.

# Purpose
- Discover sources, not extract full content

# MUST USE WHEN
- The user asks for current or unknown external information
- No URL is provided

# MUST NOT USE WHEN
- A URL is already provided
- Full content is required (use WebFetch)

# Output Expectation
- URLs
- Titles
- Brief summaries

# Rules
- Max 1–2 queries per task
- After finding relevant URLs → MUST use WebFetch if deeper analysis is needed

# Anti-Patterns
- DO NOT answer solely from search results if precision is required
- DO NOT loop WebSearch repeatedly
