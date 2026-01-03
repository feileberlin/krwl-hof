# Documentation Structure Standard

## 📋 Unified Documentation Template

All README.md files in this project MUST follow this structure:

```markdown
# [Title]

> [One-line description]

## 🎯 Overview

[2-3 sentences describing what this is and why it exists]

## 📦 What's Inside / Contents / Features

[Bulleted list of main items/features/components]

## 🚀 Quick Start / Usage

[How to use/run/test - minimal steps to get started]

## 📚 Detailed Documentation / Reference

[Detailed information - sections with H3 (###) headers]

## 🔧 Advanced / Configuration (optional)

[Advanced topics if needed]

## ❓ Troubleshooting (if applicable)

[Common issues and solutions]

## 🤝 Contributing / Best Practices (if applicable)

[How to contribute or best practices to follow]

## 📖 Related / Resources (if applicable)

[Links to related docs or external resources]
```

## ✅ Required Sections (ALL README.md files)

1. **# Title** (H1) - Only ONE H1 per file
2. **> One-line description** - Blockquote under title
3. **## 🎯 Overview** - What is this and why
4. **## 📦 Contents/Features** - What's inside
5. **## 🚀 Quick Start** - How to use immediately

## 🎨 Emoji Standards

Use consistent emojis for section headers:

- 🎯 = Overview/Purpose/What is this
- 📦 = Contents/Features/What's inside
- 🚀 = Quick Start/Usage/Getting Started
- 📚 = Detailed Documentation/Reference
- 🔧 = Advanced/Configuration
- ❓ = Troubleshooting/FAQ
- 🤝 = Contributing/Best Practices
- 📖 = Related/Resources
- 💡 = Tips/Examples
- ⚠️ = Warnings/Important
- ✅ = Requirements/Checklist
- 🧪 = Testing

## 📏 Style Rules

1. **One H1 only** - File title
2. **H2 for major sections** (##)
3. **H3 for subsections** (###)
4. **No H4 or deeper** - Use lists instead
5. **Emoji + space + Title** for all H2 sections
6. **No emojis in H3 or deeper** sections
7. **Code blocks** must specify language: ```bash, ```python, ```json
8. **Links** use descriptive text, not "click here"
9. **Lists** use `-` for bullets, numbers for ordered
10. **Tables** only when comparing data, not for layout

## 🚫 Anti-Patterns (DON'T DO THIS)

❌ Multiple H1 headers
❌ Inconsistent emoji usage
❌ Deep nesting (H4, H5, H6)
❌ Code blocks without language tags
❌ "Click here" links
❌ Walls of text without structure
❌ Missing one-line description
❌ Using `#` for lists instead of `-`

## ✅ Good Example

```markdown
# Event Manager Module

> CLI and TUI for managing community events

## 🎯 Overview

The event manager provides both command-line and text-based UI for scraping,
reviewing, and publishing community events. It's the main entry point for
all event management operations.

## 📦 Features

- Interactive TUI with keyboard navigation
- CLI commands for automation
- Event approval workflow
- Bulk operations support

## 🚀 Quick Start

```bash
# Launch TUI
python3 src/event_manager.py

# Scrape events
python3 src/event_manager.py scrape
```

## 📚 Commands Reference

### Scraping

...
```

## 🔍 Validation

Use the documentation validator to check compliance:

```bash
python3 scripts/validate_docs.py
```

This will check:
- ✅ Single H1 header
- ✅ One-line description present
- ✅ Required sections present
- ✅ Proper heading hierarchy
- ✅ Emoji consistency
- ✅ Code block language tags
- ✅ No deep nesting

## 📝 Quick Reference Card

```
Structure Cheat Sheet:
├── # Title (ONE ONLY)
├── > One-line description
├── ## 🎯 Overview
├── ## 📦 Contents/Features
├── ## 🚀 Quick Start
├── ## 📚 Detailed Docs
│   ├── ### Subsection
│   └── ### Another subsection
├── ## 🔧 Advanced (optional)
├── ## ❓ Troubleshooting (optional)
└── ## 🤝 Contributing (optional)
```

## 🎓 Philosophy

**KISS + Consistency = Maintainability**

- Documents should be scannable
- Structure should be predictable
- New contributors should know where to look
- Emojis aid quick visual scanning
- Hierarchy should never exceed H3

---

Last updated: 2026-01-03
Applies to: All README.md and documentation markdown files
