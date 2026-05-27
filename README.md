# README Generator & Editor

![Language](https://img.shields.io/badge/language-Python-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Cross--Platform-lightgrey)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)

A professional, user-friendly desktop application for creating and editing GitHub README.md files with a live graphical preview. Built with Python and tkinter — no external dependencies required.

Whether you are starting a new project or refining an existing README, this tool guides you through every section with an intuitive graphical interface, real-time preview, and one-click export.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Sections](#supported-sections)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

## Features

- **Dual-Mode Workflow** — Create a new README from scratch or load and edit an existing one
- **Graphical Section Selection** — Tick checkboxes to choose which sections to include; sensible defaults pre-selected
- **Step-by-Step Compilation** — Walks through each selected section one-by-one with context-aware hints
- **Custom Sections** — Add any number of user-defined sections beyond the built-in list
- **Live Markdown Preview** — Renders headers, lists, code blocks, badges, bold/italic, and blockquotes in real time
- **Existing File Editor** — Parses existing README.md files into editable sections with add/remove/reorder capabilities
- **One-Click Export** — Save to file or copy raw markdown to clipboard
- **Error Logging** — Automatic crash logging to `readme_generator_error.log` for easy debugging
- **Zero Dependencies** — Uses only Python standard library (tkinter); no pip install required
- **Cross-Platform** — Runs on Windows, macOS, and Linux

## Screenshots

> *Screenshots will be added here. To generate your own, run the application and capture the Welcome screen, Section Selection screen, and Live Preview screen.*

## Installation

### Prerequisites

- **Python 3.7 or later** (tkinter is included in the standard library)
- No additional packages required

### Download

1. Clone the repository or download the latest release:
   ```bash
   git clone https://github.com/yourusername/readme-generator-editor.git
   cd readme-generator-editor
   ```

2. Ensure Python is installed and tkinter is available:
   ```bash
   python --version
   python -c "import tkinter; print(tkinter.Tcl().eval('info patchlevel'))"
   ```

### Running the Application

#### Windows

Double-click `readme_generator_gui.py` or run from Command Prompt:
```bash
python readme_generator_gui.py
```

> **Tip**: If the window opens and closes immediately, check `readme_generator_error.log` in the same folder, or run from Command Prompt to see live error output.

#### macOS / Linux

```bash
python3 readme_generator_gui.py
```

If you encounter display issues on Linux, ensure `python3-tk` is installed:
```bash
sudo apt-get install python3-tk
```

## Usage

### Creating a New README

1. Launch the application and click **"Create New README"**
2. **Select Sections** — Tick the checkboxes for sections you want to include (Title and Description are always required)
3. **Compile Each Section** — The app walks you through each selected section:
   - Enter your **Project Title**
   - Write your **Project Description**
   - Fill in **Badges** (Language, License, Version, Platform)
   - Add content for each optional section with inline hints
   - Click **Skip** if a section is not needed after all
4. **Add Custom Sections** (optional) — Enter any custom title and content (e.g., "Safety", "Bill of Materials", "Troubleshooting")
5. **Preview** — Review the live-rendered README
6. **Save or Copy** — Export to `README.md` or copy markdown to clipboard

### Editing an Existing README

1. Click **"Load Existing README"** and select your `.md` file
2. The app **parses** all sections automatically
3. **Edit** any section by clicking its **Edit** button
4. **Toggle** sections on/off with checkboxes
5. **Add** new sections from the default list
6. **Preview** updates in real time
7. **Save** to overwrite or choose a new filename

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Confirm / Next (in single-line fields) |
| `Ctrl + S` | Save file (when in preview) |
| `Alt + F4` | Exit with save prompt |

## Supported Sections

### Built-in Sections

| Section | Icon | Description |
|---------|------|-------------|
| **Project Title** | 🏷️ | Repository name and header |
| **Project Description** | 📝 | Elevator pitch and purpose |
| **Badges / Shields** | 🏷️ | shields.io badges auto-generated from metadata |
| **Features** | ✨ | Bullet list of key capabilities |
| **Installation** | ⚙️ | Prerequisites, build steps, flashing instructions |
| **Usage** | 🚀 | How to use the project with examples |
| **Wiring / Hardware Setup** | 🔌 | Pin mappings, power requirements, connections |
| **Architecture / Design** | 🏗️ | System block diagrams, data flow, design rationale |
| **API Reference** | 📚 | Function signatures, parameters, return values |
| **Configuration** | 🔧 | Tunable parameters, `#define` values, settings |
| **Demo / Screenshots** | 🖼️ | Images, GIFs, video links |
| **Contributing** | 🤝 | Guidelines for external contributors |
| **License** | ⚖️ | License type and terms |
| **Acknowledgments** | 🙏 | Credits, references, thanks |
| **Contact / Author** | 📧 | Email, links, support channels |
| **Changelog** | 📋 | Version history and release notes |

### Custom Sections

Any section not in the list above can be added dynamically. The app generates a safe anchor link for the table of contents automatically.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    README Generator & Editor                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Welcome    │─────►│  New / Load  │─────►│   Section    │ │
│  │    Screen    │      │   Choice     │      │  Selection   │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                       │         │
│                                                       ▼         │
│                                              ┌──────────────┐ │
│                                              │   Compile    │ │
│                                              │  (One-by-One)│ │
│                                              └──────────────┘ │
│                                                       │         │
│                              ┌────────────────────────┘         │
│                              ▼                                  │
│                     ┌──────────────┐                           │
│                     │   Custom     │                           │
│                     │   Sections?  │                           │
│                     └──────────────┘                           │
│                              │                                  │
│                              ▼                                  │
│                     ┌──────────────┐                           │
│                     │ Live Preview │◄────────────────────┐    │
│                     │  (Rendered)  │                      │    │
│                     └──────────────┘                      │    │
│                              │                            │    │
│                              ▼                            │    │
│                     ┌──────────────┐    Edit / Refresh    │    │
│                     │ Save / Copy  │──────────────────────┘    │
│                     │   / Exit     │                           │
│                     └──────────────┘                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Core Classes:                                             │ │
│  │  • ReadmeBuilder    — Constructs markdown, manages sections│ │
│  │  • ReadmeParser     — Parses existing .md into sections  │ │
│  │  • MarkdownRenderer — Renders markdown to tkinter Text    │ │
│  │  • ReadmeApp        — Main GUI controller & navigation   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
readme-generator-editor/
├── readme_generator_gui.py      # Main application (single-file)
├── README.md                    # This file
├── LICENSE                      # MIT License
└── readme_generator_error.log   # Auto-generated crash logs
```

### Design Decisions

- **Single-file architecture** — Everything in one `.py` file for maximum portability; no package installation needed
- **tkinter over Qt/Electron** — Zero dependencies, native OS look-and-feel, lightweight footprint
- **Builder + Parser pattern** — Separates construction logic from parsing logic for clean editing workflows
- **Raw string literals** — Prevents escape-sequence corruption during file generation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- Follow **PEP 8** guidelines
- Use **type hints** where practical
- Document all public methods with docstrings
- Keep GUI event handlers under 50 lines; refactor complex logic into helper methods

### Reporting Bugs

If the application crashes:

1. Check `readme_generator_error.log` in the application folder
2. Include the log contents in your bug report
3. Specify your OS, Python version, and tkinter patch level

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Acknowledgments

- **Python Software Foundation** — For tkinter and the batteries-included philosophy
- **GitHub / shields.io** — For the badge specification that inspired the auto-generation feature
- **The open-source community** — For README templates and best-practice guides that shaped the default section list

## Contact

**Project Maintainer** — [Your Name](mailto:your.email@example.com)

- **GitHub Issues**: [https://github.com/yourusername/readme-generator-editor/issues](https://github.com/yourusername/readme-generator-editor/issues)
- **Discussions**: [https://github.com/yourusername/readme-generator-editor/discussions](https://github.com/yourusername/readme-generator-editor/discussions)
- **Feature Requests**: Open an issue with the label `enhancement`

---

<p align="center">
  <sub>Built to make documentation effortless. 📄✨</sub>
</p>
