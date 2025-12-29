# Development Environment Setup

This document describes the development environment configuration for KRWL HOF, including GitHub Copilot custom instructions, VS Code settings, devcontainer setup, and Model Context Protocol (MCP) configuration.

## Overview

The project includes comprehensive development environment configuration to make GitHub Copilot and other AI assistants more effective when working with this codebase.

## Components

### 1. GitHub Copilot Instructions

**Location**: `.github/copilot-instructions.md`

Comprehensive instructions for GitHub Copilot that include:
- Project architecture overview
- Technology stack details
- Critical file warnings (auto-generated files)
- Build and test instructions
- Code guidelines (KISS principle, style guides)
- Feature registry system
- Testing requirements
- Deployment workflow
- Common tasks and workflows

### 2. VS Code Configuration

**Location**: `.vscode/`

#### `settings.json`
Workspace-level settings including:
- Python linting and formatting configuration
- JavaScript/JSON validation settings
- GitHub Copilot enablement
- Auto-generated file protection (read-only markers)
- Search and file watching exclusions
- Editor formatting rules

#### `extensions.json`
Recommended VS Code extensions:
- GitHub Copilot and Copilot Chat
- Python development tools
- Web development tools
- Git utilities
- Markdown support

#### `tasks.json`
Predefined tasks for common operations:
- Setup: Install dependencies, download libraries
- Test: Run all test suites
- Generate: Static site and documentation
- Server: Start local development server
- TUI: Launch event manager

#### `launch.json`
Debug configurations for:
- Running Python files
- Launching the TUI
- Generating static site
- Running tests with debugging

### 3. Devcontainer Configuration

**Location**: `.devcontainer/devcontainer.json`

Docker-based development container with:
- Python 3.11 base image
- Pre-installed Git and GitHub CLI
- All recommended VS Code extensions
- Automatic dependency installation on creation
- Port forwarding for local development server (port 8000)

**Benefits**:
- Consistent development environment across machines
- Quick onboarding for new contributors
- Isolated from host system

### 4. Model Context Protocol (MCP)

**Location**: `.github/mcp/`

MCP server configuration for enhanced AI context:

#### Configured Servers:
1. **GitHub Server**: Repository context (issues, PRs, workflows)
2. **Filesystem Server**: Workspace file access
3. **Memory Server**: Persistent context across sessions

#### Context Files:
Automatically provided to AI assistants:
- `.github/copilot-instructions.md`
- `features.json`
- `README.md`
- `TESTING.md`
- Configuration files (`config.dev.json`, `config.prod.json`)
- `static/.copilot-protected`

## Setup Instructions

### Quick Start (VS Code)

1. **Open the project in VS Code**
   ```bash
   code /path/to/krwl-hof
   ```

2. **Install recommended extensions**
   - VS Code will prompt to install recommended extensions
   - Or manually: `Ctrl+Shift+P` → "Extensions: Show Recommended Extensions"

3. **Activate Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run setup task**
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "Setup: Download Frontend Libraries"

### Using Devcontainer

1. **Prerequisites**
   - Install [Docker](https://www.docker.com/products/docker-desktop)
   - Install [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in container**
   - Open project in VS Code
   - `Ctrl+Shift+P` → "Remote-Containers: Reopen in Container"
   - Wait for container to build and dependencies to install

### MCP Setup

1. **Install Node.js** (required for MCP servers)
   ```bash
   # macOS
   brew install node
   
   # Ubuntu/Debian
   sudo apt install nodejs npm
   
   # Windows
   # Download from https://nodejs.org/
   ```

2. **Set GitHub token** (optional, for GitHub MCP server)
   ```bash
   export GITHUB_TOKEN=your_github_personal_access_token
   ```

3. **Verify MCP configuration**
   - MCP servers are installed automatically via `npx` when needed
   - Compatible AI tools will detect `.github/mcp/servers.json` automatically

## Using the Configuration

### Running Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

- **Setup: Install Python Dependencies** - Install Python packages
- **Setup: Download Frontend Libraries** - Download Leaflet.js and dependencies
- **Test: All Tests** - Run complete test suite
- **Test: Feature Verification** - Verify features.json registry
- **Generate: Static Site** - Generate HTML/CSS/JS from templates
- **Generate: Documentation** - Regenerate README.md
- **Server: Start Local Development Server** - Launch development server on port 8000
- **TUI: Launch Event Manager** - Start interactive event management TUI

### Debugging

Press `F5` or use the Debug panel to:
- Debug current Python file
- Debug TUI main
- Debug static site generation
- Debug scrapers and tests

### GitHub Copilot Integration

With the configuration in place:
1. **Context-Aware Suggestions**: Copilot understands project structure and conventions
2. **Auto-Generated File Protection**: Copilot is warned about files it shouldn't edit
3. **KISS Principle Awareness**: Suggestions follow simplicity guidelines
4. **Testing Integration**: Copilot knows how to run and verify tests

### MCP Benefits

When using MCP-compatible AI tools:
1. **Repository Context**: AI can access issues, PRs, and workflow information
2. **Persistent Memory**: Context is maintained across sessions
3. **File Access**: AI can read and understand project structure
4. **Automatic Context Loading**: Key files are preloaded for better suggestions

## File Protection

### Auto-Generated Files

The following files are marked as read-only in VS Code settings:
- `static/index.html`
- `static/js/app.js`
- `static/css/style.css`

**To modify these files**:
1. Edit templates in `src/modules/generator.py`
2. Run: `python3 src/main.py generate`
3. Commit both template changes and generated files

## Customization

### Adding New Tasks

Edit `.vscode/tasks.json`:
```json
{
  "label": "My Custom Task",
  "type": "shell",
  "command": "python3 my_script.py",
  "group": "test"
}
```

### Adding Debug Configurations

Edit `.vscode/launch.json`:
```json
{
  "name": "Debug My Script",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/my_script.py",
  "console": "integratedTerminal"
}
```

### Extending MCP Context

Edit `.github/mcp/servers.json`:
```json
{
  "settings": {
    "contextFiles": [
      ".github/copilot-instructions.md",
      "your-new-context-file.md"
    ]
  }
}
```

## Troubleshooting

### VS Code Extensions Not Installing

- Manually install from Extensions marketplace (`Ctrl+Shift+X`)
- Check internet connectivity
- Restart VS Code

### Devcontainer Fails to Build

- Ensure Docker is running
- Check Docker has sufficient resources allocated
- Try rebuilding: `Ctrl+Shift+P` → "Remote-Containers: Rebuild Container"

### MCP Servers Not Working

- Verify Node.js is installed: `node --version`
- Check MCP-compatible AI tool is being used
- For GitHub server, ensure `GITHUB_TOKEN` is set

### Python Virtual Environment Issues

- Recreate venv:
  ```bash
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Benefits of This Setup

1. **Faster Onboarding**: New developers can be productive quickly
2. **Consistent Environment**: Same setup across all machines
3. **Enhanced AI Assistance**: Copilot provides more accurate suggestions
4. **Integrated Testing**: Run tests directly from VS Code
5. **Protected Files**: Prevents accidental editing of generated files
6. **Task Automation**: Common operations available via tasks
7. **Debugging Support**: Easy debugging of Python code and tests

## Maintaining the Configuration

### When Adding Features

1. Update `.github/copilot-instructions.md` if architecture changes
2. Add feature to `features.json`
3. Update `contextFiles` in `.github/mcp/servers.json` if new docs are added

### When Changing Build Process

1. Update tasks in `.vscode/tasks.json`
2. Update `postCreateCommand` in `.devcontainer/devcontainer.json`
3. Document changes in this file

### When Adding Dependencies

1. Update `requirements.txt`
2. Update devcontainer `postCreateCommand` if needed
3. Update "Setup" tasks in `.vscode/tasks.json`

## Related Documentation

- [GitHub Copilot Instructions](.github/copilot-instructions.md)
- [MCP Configuration](.github/mcp/README.md)
- [Testing Guide](TESTING.md)
- [Feature Registry](.github/FEATURE_REGISTRY.md)

## References

- [VS Code Settings Reference](https://code.visualstudio.com/docs/getstarted/settings)
- [Devcontainers Specification](https://containers.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
