# Session Logs Instructions

This directory contains session logs that capture the current context and state of the Fantasy Football AI project to help new chat sessions understand where we left off.

## Purpose

Session logs serve as a bridge between chat sessions, providing:
- Current project context and achievements
- Recent tasks completed and remaining
- Current todo list state
- Key technical details and system status
- Next steps and priorities

## File Naming Convention

Session log files should follow this pattern:
```
{YYYYMMDD_HHMMSS}_session_log.md
```

**Important**: Use Pacific Time (US/Pacific) for all timestamps.

Example: `20250902_121110_session_log.md` (for 12:11:10 PDT)

## When to Create Session Logs

Create a session log when:
- ✅ **Ending a significant work session** - After completing major features or phases
- ✅ **Before starting new major work** - To establish clear context
- ✅ **After resolving complex issues** - To document solutions and current state
- ✅ **When switching between different aspects** - Data collection vs. AI agents vs. web app
- ✅ **At project milestones** - Major feature completions or phase transitions

## Session Log Content Structure

Each session log should include:

### 1. Header Information
- Session date/time
- Current project phase
- Major achievements since last log
- Next immediate priorities

### 2. Current Context Summary
- Project overview and current capabilities
- Recent technical achievements
- System status and health
- Key files and directories

### 3. Recent Tasks Completed
- List of completed tasks with brief descriptions
- Technical implementations and features added
- Documentation updates
- Testing and validation results

### 4. Outstanding Tasks
- Current todo list from TodoWrite tool
- Immediate next steps
- Future enhancements planned
- Technical debt or issues to address

### 5. Technical Details
- Current system architecture
- API integrations and status
- Key configuration details
- Important file locations

### 6. References
- Links to key documentation files
- Reference to DEVELOPMENT_TASKS.md
- Important commit hashes or versions
- External resources or documentation

## Creating a Session Log

### Method 1: Manual Creation
1. Create a new file with timestamp prefix
2. Follow the content structure above
3. Include current todo list from TodoWrite tool
4. Reference key files and documentation

### Method 2: AI Assistant Creation
Ask the AI assistant to:
1. Compile current context from the conversation
2. Capture recent achievements and current state
3. Include current todo list
4. Reference DEVELOPMENT_TASKS.md
5. Create comprehensive session log

## Usage in New Sessions

When starting a new chat session:
1. **Read the latest session log** to understand current context
2. **Review DEVELOPMENT_TASKS.md** for full project timeline
3. **Check current todo list** for immediate priorities
4. **Validate system status** if needed
5. **Continue from where the previous session left off**

## Best Practices

- **Keep logs concise but comprehensive** - Include key details without overwhelming detail
- **Update regularly** - Don't let too much time pass between logs
- **Include actionable next steps** - Make it clear what should happen next
- **Reference key files** - Help new sessions find important information quickly
- **Maintain consistency** - Use similar structure and format across logs

## File Management

- **Keep logs organized** - Use consistent naming and structure
- **Archive old logs** - Move very old logs to archive subdirectory if needed
- **Version control** - Include session logs in git for full project history
- **Clean up** - Remove temporary or duplicate logs

## Example Session Log Structure

```markdown
# Session Log - 2025-09-02 12:11:10 PDT

## Current Status
- Phase: AI Agent Implementation COMPLETE
- Major Achievement: External prompt management system implemented
- Next Priority: System prompt optimization

## Recent Achievements
- [List of recent completions]

## Current Context
- [System overview and capabilities]

## Outstanding Tasks
- [Current todo list]

## Technical Details
- [Key technical information]

## References
- DEVELOPMENT_TASKS.md
- [Other key files]
```

---

**Note**: This system helps maintain continuity across chat sessions and ensures no context is lost when switching between different AI assistants or starting new conversations.
