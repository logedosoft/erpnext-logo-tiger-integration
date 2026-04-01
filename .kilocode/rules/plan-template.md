# Plan Format Rules

When creating plan.md files, follow this exact structure. No other sections allowed.

## Required Structure

```markdown
# [Feature/Fix Name]

## What & Why
One sentence: what's broken/needed and why it matters.

## Change
- **File:** `path/to/file.py`
- **Where:** Function name or line range
- **Before:** (code block, 3-5 lines max)
- **After:** (code block, 3-5 lines max)

## Validation
- [ ] Test case 1 (happy path)
- [ ] Test case 2 (failure case)
- [ ] Regression: what must NOT break
```

## Rules
- NO flow diagrams unless explicitly requested
- NO "Benefits" or "Overview" sections
- NO repeated explanations of the same change
- Code blocks: show ONLY the changed lines + 2 lines context
- Validation: max 3-5 checklist items, no prose
- Total length: under 30 lines for single-file changes