# Git Instructions for Cursor

## Commit Message Guidelines

### Format Requirements
- Use `git commit -m "MESSAGE"` with multi-line messages in double quotes
- NO temporary .txt files for commit messages
- Keep messages comprehensive but use simple formatting
- Use newlines within the quoted message for structure

### Message Structure
```
git commit -m "TITLE: Brief description of changes

Detailed explanation of what was changed and why.

Key changes:
- Specific change 1
- Specific change 2
- Specific change 3

Technical details or implementation notes if relevant.

STATUS or OUTCOME"
```

### Content Guidelines

#### What to Include
- **Clear title** summarizing the main change
- **Detailed explanation** of what was modified
- **Key changes list** with specific items
- **Technical context** when relevant (API changes, fixes, new features)
- **Status indicators** (WORKING, COMPLETE, FIXED, etc.)
- **Impact assessment** (what this enables or resolves)

#### What NOT to Include
- Emojis or special characters that might cause shell issues
- Complex formatting that requires escape characters
- References to temporary files or debug outputs
- Overly verbose descriptions that could be simplified

### Example Good Commit
```bash
git commit -m "MAJOR FIXES: Matchup Parsing and Starting Lineup Detection

Fixed critical issues with Yahoo API data parsing.

Key changes:
- Fixed matchup parsing to extract real team names instead of Unknown
- Added missing roster parsing method for starting lineup detection
- Enhanced JSON parsing for complex nested Yahoo API structures
- Improved error handling with detailed logging

Technical improvements:
- Proper selected_position parsing from nested arrays
- Robust team data extraction from multiple JSON levels
- Enhanced table formatting with dynamic column alignment

READY FOR PROJECTED POINTS INTEGRATION"
```

### Example Bad Commit (Avoid)
```bash
# DON'T DO THIS - requires temp file
echo "Complex message..." > commit_message.txt
git commit -F commit_message.txt

# DON'T DO THIS - too simple
git commit -m "fixes"

# DON'T DO THIS - shell escape issues
git commit -m "🎉 MAJOR UPDATE: Fixed \"complex\" parsing (100% working!)"
```

### Commit Frequency
- Commit after completing logical units of work
- Don't wait to batch multiple unrelated changes
- Commit before major refactoring or risky changes
- Always commit working states before experimenting

### Branch and Tagging
- Use descriptive branch names for features: `feature/external-api-integration`
- Tag major milestones: `git tag -a v1.0.0 -m "Core data retrieval complete"`
- Keep main branch stable and working

### File Management
- Always `git add -A` to stage all changes including new files
- Use `.gitignore` for temporary files, debug outputs, and sensitive data
- Clean up temporary files before committing
- Organize commits to include related file changes together

### Error Handling
- If commit fails due to message formatting, simplify the message
- Avoid special characters that might cause shell interpretation issues
- Use single quotes inside double-quoted messages if needed
- Test complex messages in a simple form first

### Performance Notes
- Prefer direct `git commit -m` over file-based commits for efficiency
- Keep commit messages informative but not excessively long
- Focus on clarity and usefulness for future reference
