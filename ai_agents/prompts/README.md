# AI Agent System Prompts

This directory contains external system prompts for all AI agents in the Fantasy Football system.

## File Naming Convention

System prompt files should follow this naming pattern:
```
{agent_name}_system_prompt.md
```

Examples:
- `analyst_agent_system_prompt.md` - System prompt for the Analyst Agent
- `coach_agent_system_prompt.md` - System prompt for the Coach Agent
- `scout_agent_system_prompt.md` - System prompt for the Scout Agent

## Dynamic Placeholders

System prompts support dynamic placeholders that are automatically replaced when loaded:

- `{current_date}` - Current date in "Monday, January 01, 2025" format
- `{current_time}` - Current time in "10:30 AM PST" format  
- `{current_week}` - Current NFL game week (1-18)

## Editing Prompts

### Best Practices
1. **Keep prompts focused** - Each agent should have a clear, specific role
2. **Use clear formatting** - Markdown formatting helps with readability
3. **Include examples** - Show expected output formats when helpful
4. **Test changes** - Use the Prompt Manager validation tools
5. **Version control** - All prompt changes are tracked in git

### Making Changes
1. Edit the appropriate `{agent_name}_system_prompt.md` file
2. Test your changes using the Prompt Manager:
   ```bash
   cd ai_agents
   python prompt_manager.py
   ```
3. Validate the prompt:
   ```python
   from ai_agents.prompt_manager import PromptManager
   manager = PromptManager()
   validation = manager.validate_prompt_file('analyst_agent')
   print(validation)
   ```

### Reloading Prompts
After editing a prompt file, you can reload it in a running agent:
```python
agent.reload_system_prompt()
```

## Creating New Agent Prompts

1. Copy the template:
   ```bash
   cp agent_prompt_template.md new_agent_system_prompt.md
   ```

2. Edit the template with your agent's specific requirements

3. Test the new prompt:
   ```python
   from ai_agents.prompt_manager import PromptManager
   manager = PromptManager()
   prompt = manager.get_system_prompt('new_agent')
   ```

## Validation

The Prompt Manager automatically validates prompts for:
- File existence and readability
- Proper placeholder formatting
- Minimum content length
- Formatting errors

## Current Agents

- **analyst_agent** - Fantasy football analysis and recommendations
- *Additional agents will be added as they are implemented*

## Template

See `agent_prompt_template.md` for a template to create new agent prompts.
