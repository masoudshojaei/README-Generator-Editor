#!/usr/bin/env python3
"""
README Generator & Editor - GUI Application
A professional desktop application for creating and editing GitHub README.md files
with live graphical preview, built with tkinter.

Author: Generated for CAN-HMI Project
License: MIT
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import os
import sys
import re
from datetime import datetime
from pathlib import Path


class MarkdownRenderer:
    """Simple markdown-to-tkinter text widget renderer."""

    def __init__(self, text_widget):
        self.text = text_widget
        self.setup_tags()

    def setup_tags(self):
        """Configure text tags for markdown styling."""
        self.text.tag_configure("h1", font=("Segoe UI", 20, "bold"), foreground="#2f363d", spacing3=8)
        self.text.tag_configure("h2", font=("Segoe UI", 16, "bold"), foreground="#24292e", spacing3=6)
        self.text.tag_configure("h3", font=("Segoe UI", 13, "bold"), foreground="#24292e", spacing3=4)
        self.text.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.text.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.text.tag_configure("code", font=("Consolas", 9), background="#f6f8fa", foreground="#e83e8c")
        self.text.tag_configure("code_block", font=("Consolas", 9), background="#f6f8fa", foreground="#24292e")
        self.text.tag_configure("link", font=("Segoe UI", 10), foreground="#0366d6", underline=True)
        self.text.tag_configure("list", font=("Segoe UI", 10), foreground="#24292e", lmargin1=20, lmargin2=40)
        self.text.tag_configure("quote", font=("Segoe UI", 10), foreground="#6a737d", lmargin1=20, lmargin2=20)
        self.text.tag_configure("normal", font=("Segoe UI", 10), foreground="#24292e")
        self.text.tag_configure("badge", font=("Segoe UI", 9), foreground="#586069", background="#f1f8ff")
        self.text.tag_configure("hr", font=("Segoe UI", 2), foreground="#e1e4e8")

    def render(self, content):
        """Render markdown content into the text widget."""
        self.text.delete(1.0, tk.END)
        lines = content.split('\n')
        in_code_block = False
        code_lines = []

        for line in lines:
            stripped = line.strip()

            # Code blocks
            if stripped.startswith('```'):
                if in_code_block:
                    code_text = '\n'.join(code_lines)
                    self.text.insert(tk.END, code_text + '\n', "code_block")
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Horizontal rule
            if stripped == '---' or stripped == '___' or stripped == '***':
                self.text.insert(tk.END, '─' * 60 + '\n', "hr")
                continue

            # Headers
            if stripped.startswith('# ') and not stripped.startswith('## '):
                self.text.insert(tk.END, stripped[2:] + '\n', "h1")
                continue
            elif stripped.startswith('## '):
                self.text.insert(tk.END, '\n' + stripped[3:] + '\n', "h2")
                continue
            elif stripped.startswith('### '):
                self.text.insert(tk.END, stripped[4:] + '\n', "h3")
                continue

            # Badges (shields.io)
            if 'shields.io' in stripped or 'img.shields.io' in stripped:
                self.text.insert(tk.END, '[Badge] ' + stripped[:60] + '...\n', "badge")
                continue

            # Blockquote
            if stripped.startswith('>'):
                self.text.insert(tk.END, stripped[1:].strip() + '\n', "quote")
                continue

            # Lists
            if stripped.startswith('- ') or stripped.startswith('* '):
                content_text = stripped[2:]
                self.text.insert(tk.END, '  • ' + content_text + '\n', "list")
                continue
            if re.match(r'^[0-9]+\.\s', stripped):
                content_text = re.sub(r'^[0-9]+\.\s', '', stripped)
                self.text.insert(tk.END, '  ' + stripped[:2] + content_text + '\n', "list")
                continue

            # Inline code
            if '`' in stripped:
                parts = re.split(r'`([^`]+)`', stripped)
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        self.text.insert(tk.END, part, "code")
                    else:
                        self.text.insert(tk.END, part, "normal")
                self.text.insert(tk.END, '\n')
                continue

            # Bold/Italic
            if stripped:
                text_to_insert = stripped
                text_to_insert = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text_to_insert)
                text_to_insert = re.sub(r'\*\*(.+?)\*\*', r'\1', text_to_insert)
                text_to_insert = re.sub(r'\*(.+?)\*', r'\1', text_to_insert)
                self.text.insert(tk.END, text_to_insert + '\n', "normal")
            else:
                self.text.insert(tk.END, '\n')


class ReadmeBuilder:
    """Handles construction of README content."""

    AVAILABLE_SECTIONS = {
        "title": {"name": "Project Title", "required": True, "icon": "🏷️"},
        "description": {"name": "Project Description", "required": True, "icon": "📝"},
        "badges": {"name": "Badges / Shields", "required": False, "icon": "🏷️"},
        "demo": {"name": "Demo / Screenshots", "required": False, "icon": "🖼️"},
        "features": {"name": "Features", "required": False, "icon": "✨"},
        "installation": {"name": "Installation", "required": False, "icon": "⚙️"},
        "usage": {"name": "Usage", "required": False, "icon": "🚀"},
        "wiring": {"name": "Wiring / Hardware Setup", "required": False, "icon": "🔌"},
        "architecture": {"name": "Architecture / Design", "required": False, "icon": "🏗️"},
        "api": {"name": "API Reference", "required": False, "icon": "📚"},
        "configuration": {"name": "Configuration", "required": False, "icon": "🔧"},
        "contributing": {"name": "Contributing", "required": False, "icon": "🤝"},
        "license": {"name": "License", "required": False, "icon": "⚖️"},
        "acknowledgments": {"name": "Acknowledgments", "required": False, "icon": "🙏"},
        "contact": {"name": "Contact / Author", "required": False, "icon": "📧"},
        "changelog": {"name": "Changelog", "required": False, "icon": "📋"},
    }

    def __init__(self):
        self.sections = {}
        self.section_order = []

    def add_section(self, key, content):
        self.sections[key] = content
        if key not in self.section_order:
            self.section_order.append(key)

    def remove_section(self, key):
        if key in self.sections:
            del self.sections[key]
        if key in self.section_order:
            self.section_order.remove(key)

    def generate_badges(self, info):
        badges = []
        if info.get("language"):
            badges.append(f"![Language](https://img.shields.io/badge/language-{info['language'].replace(' ', '%20')}-blue)")
        if info.get("license"):
            badges.append(f"![License](https://img.shields.io/badge/license-{info['license'].replace(' ', '%20')}-green)")
        if info.get("version"):
            badges.append(f"![Version](https://img.shields.io/badge/version-{info['version']}-orange)")
        if info.get("platform"):
            badges.append(f"![Platform](https://img.shields.io/badge/platform-{info['platform'].replace(' ', '%20')}-lightgrey)")
        return " ".join(badges) if badges else ""

    def build_readme(self):
        lines = []

        if "title" in self.sections:
            lines.append(f"# {self.sections['title']}")
            lines.append("")

        if "badges" in self.sections and self.sections["badges"]:
            lines.append(self.sections["badges"])
            lines.append("")

        if "description" in self.sections:
            lines.append(self.sections["description"])
            lines.append("")

        toc_sections = [k for k in self.section_order if k not in ["title", "badges", "description"]]
        if len(toc_sections) >= 3:
            lines.append("## Table of Contents")
            lines.append("")
            for key in toc_sections:
                anchor = self.AVAILABLE_SECTIONS[key]["name"].lower().replace(" / ", "-").replace(" ", "-").replace(".", "")
                lines.append(f"- [{self.AVAILABLE_SECTIONS[key]['name']}](#{anchor})")
            lines.append("")

        for key in toc_sections:
            if key in self.sections:
                section_name = self.AVAILABLE_SECTIONS[key]["name"]
                lines.append(f"## {section_name}")
                lines.append("")
                content = self.sections[key]
                if isinstance(content, list):
                    for item in content:
                        lines.append(f"- {item}")
                else:
                    lines.append(content)
                lines.append("")

        return "\n".join(lines)


class ReadmeParser:
    """Parse existing README.md files."""

    @staticmethod
    def parse_file(filepath):
        builder = ReadmeBuilder()
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                if current_section:
                    builder.add_section(current_section, '\n'.join(current_content).strip())
                builder.add_section("title", line[2:].strip())
                current_section = None
                current_content = []
            elif line.startswith("## "):
                if current_section:
                    builder.add_section(current_section, '\n'.join(current_content).strip())
                section_name = line[3:].strip().lower()
                current_section = ReadmeParser._map_section(section_name)
                current_content = []
            elif "shields.io" in line or "badge" in line.lower():
                if not current_section:
                    builder.add_section("badges", line.strip())
            else:
                if current_section:
                    current_content.append(line)
                elif line.strip() and "title" in builder.sections and "description" not in builder.sections:
                    current_content.append(line)
                    current_section = "description"

        if current_section and current_content:
            builder.add_section(current_section, '\n'.join(current_content).strip())

        return builder

    @staticmethod
    def _map_section(name):
        mapping = {
            "table of contents": None,
            "project description": "description", "description": "description", "overview": "description",
            "badges": "badges", "shields": "badges",
            "demo": "demo", "screenshots": "demo",
            "features": "features", "key features": "features",
            "installation": "installation", "getting started": "installation", "setup": "installation",
            "usage": "usage", "how to use": "usage",
            "wiring": "wiring", "hardware setup": "wiring", "wiring diagram": "wiring",
            "architecture": "architecture", "design": "architecture", "system architecture": "architecture",
            "api reference": "api", "api": "api",
            "configuration": "configuration", "config": "configuration",
            "contributing": "contributing", "how to contribute": "contributing",
            "license": "license", "licensing": "license",
            "acknowledgments": "acknowledgments", "acknowledgements": "acknowledgments", "credits": "acknowledgments",
            "contact": "contact", "author": "contact", "contact us": "contact",
            "changelog": "changelog", "changes": "changelog", "version history": "changelog",
        }
        return mapping.get(name, "description")


class ReadmeApp:
    """Main GUI application."""

    def __init__(self, root):
        self.root = root
        self.root.title("README Generator & Editor")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f6f8fa")

        self.builder = ReadmeBuilder()
        self.current_file = None

        # Startup logging
        self.log_startup()

        self.setup_styles()
        self.show_welcome_screen()

    def log_startup(self):
        """Log startup information for debugging."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_file = os.path.join(script_dir, "readme_generator_error.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"STARTUP at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
                f.write(f"Python version: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write(f"Working directory: {os.getcwd()}\n")
                f.write(f"Script directory: {script_dir}\n")
                f.write(f"Tkinter version: {tk.Tcl().eval('info patchlevel')}\n")
                f.write("\n")
        except Exception as e:
            print(f"Could not write startup log: {e}")

    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#24292e", background="#f6f8fa")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12), foreground="#586069", background="#f6f8fa")
        style.configure("Section.TLabel", font=("Segoe UI", 14, "bold"), foreground="#24292e", background="#f6f8fa")
        style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Check.TCheckbutton", font=("Segoe UI", 11), background="#ffffff")

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """Show the initial welcome screen with choice."""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding=40)
        main_frame.pack(expand=True, fill="both")
        main_frame.configure(style="Card.TFrame")

        # Title
        ttk.Label(main_frame, text="📄 README Generator & Editor", style="Title.TLabel").pack(pady=(0, 10))
        ttk.Label(main_frame, text="Create professional GitHub README files with live preview", style="Subtitle.TLabel").pack(pady=(0, 40))

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        new_btn = ttk.Button(btn_frame, text="🆕  Create New README", command=self.show_new_project_screen,
                            style="Action.TButton", width=30)
        new_btn.pack(pady=10)

        load_btn = ttk.Button(btn_frame, text="📂  Load Existing README", command=self.load_existing_readme,
                             style="Action.TButton", width=30)
        load_btn.pack(pady=10)

        # Footer
        ttk.Label(main_frame, text="v1.0  •  Built for CAN-HMI Project", style="Subtitle.TLabel").pack(side="bottom", pady=20)

    def load_existing_readme(self):
        """Load an existing README file."""
        filepath = filedialog.askopenfilename(
            title="Select README.md file",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            self.builder = ReadmeParser.parse_file(filepath)
            self.current_file = filepath
            self.show_edit_existing_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def show_edit_existing_screen(self):
        """Screen for editing existing README sections."""
        self.clear_window()

        # Header
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="✏️ Edit Existing README", style="Title.TLabel").pack(side="left")
        if self.current_file:
            ttk.Label(header, text=f"  —  {os.path.basename(self.current_file)}", style="Subtitle.TLabel").pack(side="left", padx=10)

        # Main content - split view
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(expand=True, fill="both", padx=10, pady=10)

        # Left: Sections list
        left_frame = ttk.Frame(paned, padding=10)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Sections", style="Section.TLabel").pack(anchor="w", pady=(0, 10))

        # Sections list with edit buttons
        sections_frame = ttk.Frame(left_frame)
        sections_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(sections_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sections_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.section_vars = {}
        for key in self.builder.section_order:
            if key in ["title", "description"]:
                continue

            section_frame = ttk.Frame(scroll_frame, padding=5)
            section_frame.pack(fill="x", pady=2)

            name = self.builder.AVAILABLE_SECTIONS.get(key, {}).get("name", key)
            icon = self.builder.AVAILABLE_SECTIONS.get(key, {}).get("icon", "📄")

            var = tk.BooleanVar(value=True)
            self.section_vars[key] = var

            cb = ttk.Checkbutton(section_frame, text=f"{icon}  {name}", variable=var,
                                style="Check.TCheckbutton")
            cb.pack(side="left")

            edit_btn = ttk.Button(section_frame, text="Edit", width=8,
                                 command=lambda k=key: self.edit_section_dialog(k))
            edit_btn.pack(side="right", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title and description editors
        ttk.Label(left_frame, text="Required Sections", style="Section.TLabel").pack(anchor="w", pady=(20, 10))

        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill="x", pady=5)
        ttk.Label(title_frame, text="Title:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.title_entry = ttk.Entry(title_frame, font=("Segoe UI", 11))
        self.title_entry.pack(fill="x", pady=2)
        self.title_entry.insert(0, self.builder.sections.get("title", ""))

        desc_frame = ttk.Frame(left_frame)
        desc_frame.pack(fill="x", pady=5)
        ttk.Label(desc_frame, text="Description:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=6, font=("Segoe UI", 10), wrap="word")
        self.desc_text.pack(fill="x", pady=2)
        self.desc_text.insert(1.0, self.builder.sections.get("description", ""))

        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="➕ Add Section", command=self.add_section_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Update Preview", command=self.update_preview).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Save", command=self.save_readme).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="🔙 Back", command=self.show_welcome_screen).pack(side="right", padx=5)

        # Right: Preview
        right_frame = ttk.Frame(paned, padding=10)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="📋 Live Preview", style="Section.TLabel").pack(anchor="w", pady=(0, 10))

        preview_frame = ttk.Frame(right_frame, relief="solid", borderwidth=1)
        preview_frame.pack(fill="both", expand=True)

        self.preview_text = tk.Text(preview_frame, wrap="word", padx=20, pady=20,
                                   bg="#ffffff", fg="#24292e", relief="flat",
                                   font=("Segoe UI", 10))
        self.preview_text.pack(fill="both", expand=True)

        self.renderer = MarkdownRenderer(self.preview_text)
        self.update_preview()

    def edit_section_dialog(self, section_key):
        """Open dialog to edit a section."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {self.builder.AVAILABLE_SECTIONS[section_key]['name']}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=f"Editing: {self.builder.AVAILABLE_SECTIONS[section_key]['name']}",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        text_widget = scrolledtext.ScrolledText(dialog, wrap="word", font=("Consolas", 10), height=25)
        text_widget.pack(fill="both", expand=True, padx=20, pady=10)
        text_widget.insert(1.0, self.builder.sections.get(section_key, ""))

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=10)

        def save():
            content = text_widget.get(1.0, tk.END).strip()
            self.builder.sections[section_key] = content
            self.update_preview()
            dialog.destroy()

        ttk.Button(btn_frame, text="Save Changes", command=save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)

    def add_section_dialog(self):
        """Dialog to add a new section."""
        available = [k for k in self.builder.AVAILABLE_SECTIONS.keys() 
                    if k not in self.builder.sections]

        if not available:
            messagebox.showinfo("Info", "All available sections are already present.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Section")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select section to add:", font=("Segoe UI", 12, "bold")).pack(pady=10)

        listbox = tk.Listbox(dialog, font=("Segoe UI", 11), selectmode="single")
        listbox.pack(fill="both", expand=True, padx=20, pady=10)

        for key in available:
            name = self.builder.AVAILABLE_SECTIONS[key]["name"]
            icon = self.builder.AVAILABLE_SECTIONS[key]["icon"]
            listbox.insert(tk.END, f"{icon}  {name}")

        def add():
            sel = listbox.curselection()
            if sel:
                key = available[sel[0]]
                self.builder.add_section(key, "")
                self.show_edit_existing_screen()
            dialog.destroy()

        ttk.Button(dialog, text="Add Section", command=add).pack(pady=10)

    def show_new_project_screen(self):
        """Screen for creating new README - section selection."""
        self.clear_window()
        self.builder = ReadmeBuilder()

        # Header
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="🆕 Create New README", style="Title.TLabel").pack(side="left")

        # Main content
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Select the sections you want to include:", 
                 style="Section.TLabel").pack(anchor="w", pady=(0, 10))

        # Scrollable section list
        sections_container = ttk.Frame(main_frame)
        sections_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(sections_container, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sections_container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=600)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.new_section_vars = {}

        # Required sections (always included)
        req_frame = ttk.LabelFrame(scroll_frame, text="Required Sections", padding=10)
        req_frame.pack(fill="x", pady=5, padx=5)

        ttk.Label(req_frame, text="🏷️  Project Title  (always included)", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(req_frame, text="📝  Project Description  (always included)", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        # Optional sections
        opt_frame = ttk.LabelFrame(scroll_frame, text="Optional Sections — Check to Include", padding=10)
        opt_frame.pack(fill="x", pady=5, padx=5)

        optional_keys = [k for k in self.builder.AVAILABLE_SECTIONS.keys() 
                        if k not in ["title", "description"]]

        for key in optional_keys:
            name = self.builder.AVAILABLE_SECTIONS[key]["name"]
            icon = self.builder.AVAILABLE_SECTIONS[key]["icon"]
            var = tk.BooleanVar(value=(key in ["features", "installation", "usage", "license"]))
            self.new_section_vars[key] = var
            cb = ttk.Checkbutton(opt_frame, text=f"{icon}  {name}", variable=var,
                                style="Check.TCheckbutton")
            cb.pack(anchor="w", pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="🔙 Back", command=self.show_welcome_screen).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Next ➡️", command=self.show_compile_sections_screen).pack(side="right", padx=5)

    def show_compile_sections_screen(self):
        """Compile each selected section one by one."""
        self.selected_sections = ["title", "description"]
        for key, var in self.new_section_vars.items():
            if var.get():
                self.selected_sections.append(key)

        self.current_compile_idx = 0
        self.compile_next_section()

    def compile_next_section(self):
        """Show dialog to compile the next section."""
        if self.current_compile_idx >= len(self.selected_sections):
            self.show_additional_sections_screen()
            return

        key = self.selected_sections[self.current_compile_idx]
        section_info = self.builder.AVAILABLE_SECTIONS[key]

        self.clear_window()

        # Header
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        progress = f"Section {self.current_compile_idx + 1} of {len(self.selected_sections)}"
        ttk.Label(header, text=f"{section_info['icon']} {section_info['name']}", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f"  —  {progress}", style="Subtitle.TLabel").pack(side="left", padx=10)

        # Content area
        content_frame = ttk.Frame(self.root, padding=20)
        content_frame.pack(fill="both", expand=True)

        # Special handling for title
        if key == "title":
            ttk.Label(content_frame, text="Enter your project title:", font=("Segoe UI", 12)).pack(anchor="w", pady=10)
            self.compile_entry = ttk.Entry(content_frame, font=("Segoe UI", 14), width=60)
            self.compile_entry.pack(pady=10)
            self.compile_entry.focus()

            def save_title():
                title = self.compile_entry.get().strip()
                if title:
                    self.builder.add_section("title", title)
                    self.current_compile_idx += 1
                    self.compile_next_section()
                else:
                    messagebox.showwarning("Required", "Project title is required.")

            btn_frame = ttk.Frame(content_frame)
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="Next ➡️", command=save_title).pack()

        # Special handling for badges
        elif key == "badges":
            ttk.Label(content_frame, text="Configure badges/shields:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=10)

            badge_frame = ttk.Frame(content_frame)
            badge_frame.pack(fill="x", pady=10)

            self.badge_vars = {}
            badge_fields = [
                ("language", "Primary Language (e.g., Python, C, C++)"),
                ("license", "License Type (e.g., MIT, GPL-3.0)"),
                ("version", "Version (e.g., v1.0.0)"),
                ("platform", "Platform (e.g., STM32, Arduino, Linux)")
            ]

            for field, label in badge_fields:
                frame = ttk.Frame(badge_frame)
                frame.pack(fill="x", pady=3)
                ttk.Label(frame, text=label, width=30).pack(side="left")
                entry = ttk.Entry(frame, width=40)
                entry.pack(side="left", padx=5)
                self.badge_vars[field] = entry

            def save_badges():
                info = {k: v.get().strip() for k, v in self.badge_vars.items()}
                badges = self.builder.generate_badges(info)
                if badges:
                    self.builder.add_section("badges", badges)
                self.current_compile_idx += 1
                self.compile_next_section()

            btn_frame = ttk.Frame(content_frame)
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="Skip", command=lambda: (setattr(self, 'current_compile_idx', self.current_compile_idx + 1), self.compile_next_section())).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Add Badges ➡️", command=save_badges).pack(side="left", padx=5)

        # All other sections
        else:
            ttk.Label(content_frame, text=f"Enter content for {section_info['name']}:", 
                     font=("Segoe UI", 12)).pack(anchor="w", pady=10)

            hints = {
                "description": "Describe what your project does, who it's for, and what makes it unique.",
                "features": "List key features. One per line.",
                "installation": "Step-by-step installation instructions.",
                "usage": "How to use the project. Include examples.",
                "wiring": "Describe hardware connections, pin mappings, power requirements.",
                "architecture": "Describe system design, block diagrams, data flow.",
                "api": "Document functions, parameters, return values.",
                "configuration": "List configurable parameters and their defaults.",
                "contributing": "Guidelines for contributors.",
                "license": "License type and terms.",
                "acknowledgments": "Credits, references, thanks.",
                "contact": "Your contact information, email, links.",
                "changelog": "Version history and changes.",
                "demo": "Screenshots, GIFs, video links, demo description."
            }

            hint = hints.get(key, "Enter the content for this section.")
            ttk.Label(content_frame, text=hint, foreground="#586069", font=("Segoe UI", 10, "italic")).pack(anchor="w")

            self.compile_text = scrolledtext.ScrolledText(content_frame, wrap="word", 
                                                         font=("Consolas", 10), height=20)
            self.compile_text.pack(fill="both", expand=True, pady=10)

            defaults = {
                "contributing": "Contributions are welcome! Please feel free to submit a Pull Request.",
                "license": "This project is licensed under the MIT License.",
                "changelog": f"## [{datetime.now().strftime('%Y-%m-%d')}] - Initial Release\n- Project created"
            }
            if key in defaults:
                self.compile_text.insert(1.0, defaults[key])

            def save_section():
                content = self.compile_text.get(1.0, tk.END).strip()
                if content:
                    if key == "features":
                        lines = [l.strip('- ').strip() for l in content.split('\n') if l.strip()]
                        self.builder.add_section(key, lines)
                    else:
                        self.builder.add_section(key, content)
                self.current_compile_idx += 1
                self.compile_next_section()

            btn_frame = ttk.Frame(content_frame)
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Skip", command=lambda: (setattr(self, 'current_compile_idx', self.current_compile_idx + 1), self.compile_next_section())).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Save & Next ➡️", command=save_section).pack(side="left", padx=5)

    def show_additional_sections_screen(self):
        """Ask if user wants to add more custom sections."""
        self.clear_window()

        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="➕ Additional Sections", style="Title.TLabel").pack(side="left")

        content_frame = ttk.Frame(self.root, padding=20)
        content_frame.pack(fill="both", expand=True)

        ttk.Label(content_frame, text="Would you like to add any custom sections?", 
                 font=("Segoe UI", 14)).pack(pady=20)

        ttk.Label(content_frame, text="You can add sections not in the default list (e.g., 'Safety', 'Troubleshooting', 'References').", 
                 foreground="#586069", wraplength=500).pack(pady=10)

        if len(self.builder.section_order) > 2:
            ttk.Label(content_frame, text="Current sections:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(20, 5))
            for key in self.builder.section_order:
                name = self.builder.AVAILABLE_SECTIONS.get(key, {}).get("name", key)
                icon = self.builder.AVAILABLE_SECTIONS.get(key, {}).get("icon", "📄")
                ttk.Label(content_frame, text=f"  {icon} {name}", font=("Segoe UI", 10)).pack(anchor="w")

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="Yes, Add More ➕", command=self.add_custom_section).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="No, Show Preview 👁️", command=self.show_preview_screen).pack(side="left", padx=10)

    def add_custom_section(self):
        """Dialog to add a custom section."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Section")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Custom Section Title:", font=("Segoe UI", 11, "bold")).pack(pady=10)
        title_entry = ttk.Entry(dialog, font=("Segoe UI", 12), width=50)
        title_entry.pack(pady=5)
        title_entry.focus()

        ttk.Label(dialog, text="Content:", font=("Segoe UI", 11, "bold")).pack(pady=10)
        content_text = scrolledtext.ScrolledText(dialog, wrap="word", font=("Consolas", 10), height=15)
        content_text.pack(fill="both", expand=True, padx=20, pady=5)

        def save_custom():
            title = title_entry.get().strip()
            content = content_text.get(1.0, tk.END).strip()
            if title and content:
                safe_key = re.sub(r'[^a-z0-9_]', '_', title.lower())[:30]
                base_key = safe_key
                counter = 1
                while safe_key in self.builder.sections:
                    safe_key = f"{base_key}_{counter}"
                    counter += 1

                self.builder.AVAILABLE_SECTIONS[safe_key] = {"name": title, "required": False, "icon": "📄"}
                self.builder.add_section(safe_key, content)
                dialog.destroy()
                self.show_additional_sections_screen()
            else:
                messagebox.showwarning("Required", "Both title and content are required.")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save & Add Another", command=save_custom).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save & Done", command=lambda: [save_custom(), self.show_preview_screen()]).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def show_preview_screen(self):
        """Show the final preview with save option."""
        self.clear_window()

        if hasattr(self, 'title_entry') and hasattr(self, 'desc_text'):
            title = self.title_entry.get().strip()
            desc = self.desc_text.get(1.0, tk.END).strip()
            if title:
                self.builder.sections["title"] = title
            if desc:
                self.builder.sections["description"] = desc

        # Header
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="👁️ README Preview", style="Title.TLabel").pack(side="left")

        # Toolbar
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="🔄 Refresh", command=self.update_preview).pack(side="left", padx=5)
        ttk.Button(toolbar, text="✏️ Edit Sections", command=self.show_edit_existing_screen).pack(side="left", padx=5)
        ttk.Button(toolbar, text="💾 Save to File", command=self.save_readme).pack(side="right", padx=5)
        ttk.Button(toolbar, text="📋 Copy Markdown", command=self.copy_markdown).pack(side="right", padx=5)

        # Preview area
        preview_frame = ttk.Frame(self.root, relief="solid", borderwidth=1)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_text = tk.Text(preview_frame, wrap="word", padx=30, pady=30,
                                   bg="#ffffff", fg="#24292e", relief="flat",
                                   font=("Segoe UI", 10))
        self.preview_text.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.preview_text, command=self.preview_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.preview_text.configure(yscrollcommand=scrollbar.set)

        self.renderer = MarkdownRenderer(self.preview_text)
        self.update_preview()

        # Bottom bar
        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")

        self.status_label = ttk.Label(bottom, text="Ready", foreground="#586069")
        self.status_label.pack(side="left")

        ttk.Button(bottom, text="🔙 Back to Menu", command=self.show_welcome_screen).pack(side="right", padx=5)
        ttk.Button(bottom, text="🚪 Exit", command=self.on_exit).pack(side="right", padx=5)

    def update_preview(self):
        """Update the preview text widget."""
        if hasattr(self, 'preview_text') and self.preview_text.winfo_exists():
            content = self.builder.build_readme()
            self.renderer.render(content)
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Preview updated — {len(self.builder.section_order)} sections")

    def save_readme(self):
        """Save README to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile="README.md"
        )
        if not filepath:
            return

        try:
            content = self.builder.build_readme()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.current_file = filepath
            messagebox.showinfo("Success", f"README saved successfully to:\n{filepath}")
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Saved to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def copy_markdown(self):
        """Copy markdown to clipboard."""
        content = self.builder.build_readme()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copied", "Markdown content copied to clipboard!")

    def on_exit(self):
        """Handle application exit with save prompt."""
        if messagebox.askyesno("Exit", "Would you like to save before exiting?"):
            self.save_readme()
        self.root.destroy()


def main():
    """Main entry point with error logging."""
    import traceback

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, "readme_generator_error.log")

    def log_error(msg):
        """Write error to log file."""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"ERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(msg)
            f.write("\n")

    try:
        root = tk.Tk()

        # Set DPI awareness for Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        app = ReadmeApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_exit)
        root.mainloop()

    except Exception as e:
        error_msg = f"FATAL ERROR: {str(e)}\n\n{traceback.format_exc()}"
        log_error(error_msg)

        # Try to show a message box if tkinter is partially working
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror(
                "README Generator - Error",
                f"An error occurred and the application had to close.\n\n"
                f"Error: {str(e)}\n\n"
                f"Details have been saved to:\n{log_file}\n\n"
                f"Please check the log file and report the issue."
            )
        except:
            pass

        # Re-raise to see console output if running from terminal
        raise


if __name__ == "__main__":
    main()
