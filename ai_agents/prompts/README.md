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

### Method 1: Direct File Editing (Recommended)
**Best for:** Heavy editing, using your preferred editor, version control workflows

```bash
# Edit directly with your preferred editor
code ai_agents/prompts/analyst_agent_system_prompt.md
# or
vim ai_agents/prompts/analyst_agent_system_prompt.md
# or
nano ai_agents/prompts/analyst_agent_system_prompt.md
```

**Advantages:**
- Full control over editing process
- Use your preferred editor with syntax highlighting
- Easy to see git diffs and changes
- Better for complex formatting and markdown

### Method 2: Management Utility
**Best for:** Quick edits, validation, creating new prompts

```bash
cd ai_agents

# Edit a prompt (opens in default editor)
python manage_prompts.py edit analyst_agent

# List all prompts with validation status
python manage_prompts.py list

# Validate a specific prompt
python manage_prompts.py validate analyst_agent

# Show prompt content
python manage_prompts.py show analyst_agent

# Create new prompt from template
python manage_prompts.py create coach_agent
```

**Advantages:**
- Built-in validation after editing
- Quick overview of all prompts
- Template-based creation of new prompts
- Command-line convenience

### Making Changes - Step by Step

#### Option A: Direct Editing Workflow
1. **Edit the prompt file:**
   ```bash
   code ai_agents/prompts/analyst_agent_system_prompt.md
   ```

2. **Validate your changes:**
   ```bash
   cd ai_agents
   python manage_prompts.py validate analyst_agent
   ```

3. **Test the updated prompt:**
   ```bash
   python test_analyst_agent.py
   ```

#### Option B: Management Utility Workflow
1. **Edit using the utility:**
   ```bash
   cd ai_agents
   python manage_prompts.py edit analyst_agent
   ```

2. **The utility automatically validates after you save and close the editor**

3. **Test the updated prompt:**
   ```bash
   python test_analyst_agent.py
   ```

### Reloading Prompts
After editing a prompt file, you can reload it in a running agent without restarting:

```python
# In a Python session or script
from ai_agents.analyst_agent import AnalystAgent

agent = AnalystAgent(model_provider='openai', model_name='gpt-4')

# Reload the system prompt from the external file
agent.reload_system_prompt()

# Now use the updated prompt
result = agent.analyze('Your analysis request here')
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

## Troubleshooting

### Common Issues

**Prompt not loading:**
```bash
# Check if the file exists
ls ai_agents/prompts/analyst_agent_system_prompt.md

# Validate the prompt
cd ai_agents
python manage_prompts.py validate analyst_agent
```

**Placeholder errors:**
- Make sure placeholders use curly braces: `{current_date}`
- Check for typos in placeholder names
- Ensure all placeholders are properly closed

**Agent not using updated prompt:**
```python
# Reload the prompt in your agent
agent.reload_system_prompt()
```

**Validation errors:**
- Check for unclosed placeholders: `{current_date` (missing closing brace)
- Ensure file is not empty
- Verify markdown formatting is correct

### Getting Help

1. **Check validation output:**
   ```bash
   cd ai_agents
   python manage_prompts.py validate analyst_agent
   ```

2. **Test the prompt manager:**
   ```bash
   python prompt_manager.py
   ```

3. **Check agent initialization:**
   ```bash
   python test_analyst_agent.py
   ```

4. **View prompt content:**
   ```bash
   python manage_prompts.py show analyst_agent
   ```
