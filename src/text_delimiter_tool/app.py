from __future__ import annotations

from pathlib import Path

import tkinter as tk
from tkinter import ttk

from text_delimiter_tool.formatter import FormatOptions, format_lines
from text_delimiter_tool.version import APP_NAME, APP_VERSION

WINDOW_BG = "#f3f1ec"
CARD_BG = "#fbfaf7"
CARD_BORDER = "#d9d2c7"
INPUT_BG = "#f8f6f2"
OUTPUT_BG = "#fffdfa"
TEXT_FG = "#1f2328"
MUTED_FG = "#6b7280"
SOFT_FG = "#9aa3af"
ACCENT = "#1f6f78"
ACCENT_ACTIVE = "#185961"
BUTTON_BG = "#ebe4da"
BUTTON_ACTIVE = "#ddd2c3"
SUCCESS_BG = "#d7efe7"
SUCCESS_FG = "#0f5132"
BADGE_BG = "#d7ecef"
BADGE_FG = ACCENT


class TextDelimiterApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1120x720")
        self.root.minsize(960, 620)
        self.root.configure(bg=WINDOW_BG)
        self.window_icon: tk.PhotoImage | None = None
        self.about_window: tk.Toplevel | None = None
        self._load_app_icon()

        self.prefix_var = tk.StringVar(value="")
        self.suffix_var = tk.StringVar(value="")
        self.delimiter_var = tk.StringVar(value=",")
        self.trailing_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready for formatting")
        self.output_state_var = tk.StringVar(value="Waiting for input")
        self.active_preset = "number"
        self.copy_reset_job: str | None = None

        self._configure_style()
        self._build_layout()
        self._bind_events()
        self._apply_text_theme(self.input_text, INPUT_BG)
        self._apply_text_theme(self.output_text, OUTPUT_BG)
        self._set_placeholder_state(self.input_text, self.input_placeholder, True)
        self._set_placeholder_state(self.output_text, self.output_placeholder, True)
        self._refresh_preset_buttons()
        self.update_output()
        self.root.after(50, self._focus_input)

    def _load_app_icon(self) -> None:
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "app.png"
        if not icon_path.exists():
            return

        try:
            self.window_icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.window_icon)
        except tk.TclError:
            self.window_icon = None

    def _configure_style(self) -> None:
        default_font = ("Segoe UI", 11)
        title_font = ("Segoe UI Semibold", 24)
        subtitle_font = ("Segoe UI", 11)
        section_font = ("Segoe UI Semibold", 12)
        label_font = ("Segoe UI Semibold", 10)

        self.root.option_add("*Font", default_font)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background=WINDOW_BG)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Title.TLabel", background=WINDOW_BG, foreground=TEXT_FG, font=title_font)
        style.configure("Subtitle.TLabel", background=WINDOW_BG, foreground=MUTED_FG, font=subtitle_font)
        style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_FG, font=section_font)
        style.configure("CardSubtitle.TLabel", background=CARD_BG, foreground=MUTED_FG, font=("Segoe UI", 10))
        style.configure("FieldLabel.TLabel", background=CARD_BG, foreground=MUTED_FG, font=label_font)
        style.configure("Status.TLabel", background=WINDOW_BG, foreground=MUTED_FG, font=("Segoe UI", 10))
        style.configure("Tool.TCheckbutton", background=CARD_BG, foreground=TEXT_FG, font=("Segoe UI", 10))
        style.map("Tool.TCheckbutton", background=[("active", CARD_BG)])

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root, style="App.TFrame", padding=(28, 24, 28, 20))
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)

        self._build_menu()
        self._build_header(shell)
        self._build_controls_card(shell)
        self._build_editor_area(shell)
        self._build_status_bar(shell)

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def _show_about(self) -> None:
        if self.about_window is not None and self.about_window.winfo_exists():
            self.about_window.deiconify()
            self.about_window.lift()
            self.about_window.focus_force()
            return

        window = tk.Toplevel(self.root)
        self.about_window = window
        window.title(f"About {APP_NAME}")
        window.configure(bg=WINDOW_BG)
        window.resizable(False, False)
        window.transient(self.root)
        if self.window_icon is not None:
            window.iconphoto(True, self.window_icon)
        window.protocol("WM_DELETE_WINDOW", self._close_about)

        shell = tk.Frame(window, bg=WINDOW_BG, padx=24, pady=24)
        shell.grid(row=0, column=0, sticky="nsew")

        card = tk.Frame(shell, bg=CARD_BG, bd=1, relief="solid", highlightthickness=1, highlightbackground=CARD_BORDER)
        card.grid(row=0, column=0, sticky="nsew")

        header = tk.Frame(card, bg=CARD_BG, padx=22, pady=20)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        icon_holder = tk.Frame(header, bg=BADGE_BG, width=72, height=72)
        icon_holder.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 16))
        icon_holder.grid_propagate(False)
        if self.window_icon is not None:
            icon_label = tk.Label(icon_holder, image=self.window_icon, bg=BADGE_BG)
            icon_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            tk.Label(
                icon_holder,
                text="' ,",
                bg=BADGE_BG,
                fg=BADGE_FG,
                font=("Segoe UI Semibold", 20),
            ).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            header,
            text=APP_NAME,
            bg=CARD_BG,
            fg=TEXT_FG,
            font=("Segoe UI Semibold", 18),
            anchor="w",
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            header,
            text=f"Version {APP_VERSION}",
            bg=CARD_BG,
            fg=MUTED_FG,
            font=("Segoe UI", 11),
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(4, 0))

        body = tk.Frame(card, bg=CARD_BG, padx=22, pady=0)
        body.grid(row=1, column=0, sticky="ew")

        tk.Label(
            body,
            text="A lightweight Windows tool for converting raw columns into delimiter-ready output.",
            bg=CARD_BG,
            fg=TEXT_FG,
            justify="left",
            wraplength=360,
            font=("Segoe UI", 11),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        capabilities = tk.Frame(body, bg=CARD_BG, pady=14)
        capabilities.grid(row=1, column=0, sticky="ew")
        for idx, text in enumerate(
            (
                "Real-time formatting with prefix, suffix, and delimiter controls",
                "Preset workflows for common database formatting patterns",
                "Fast keyboard actions for copy and clear",
            )
        ):
            tk.Label(
                capabilities,
                text=f"- {text}",
                bg=CARD_BG,
                fg=MUTED_FG,
                justify="left",
                anchor="w",
                wraplength=360,
                font=("Segoe UI", 10),
            ).grid(row=idx, column=0, sticky="w", pady=(0, 6))

        shortcuts = tk.Frame(card, bg=INPUT_BG, padx=22, pady=16)
        shortcuts.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 18))
        shortcuts.columnconfigure(1, weight=1)
        tk.Label(
            shortcuts,
            text="Shortcuts",
            bg=INPUT_BG,
            fg=TEXT_FG,
            font=("Segoe UI Semibold", 11),
        ).grid(row=0, column=0, sticky="w", columnspan=2, pady=(0, 10))
        tk.Label(shortcuts, text="Ctrl+Enter", bg=INPUT_BG, fg=BADGE_FG, font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky="w")
        tk.Label(shortcuts, text="Copy formatted result", bg=INPUT_BG, fg=MUTED_FG, font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", padx=(12, 0))
        tk.Label(shortcuts, text="Ctrl+L", bg=INPUT_BG, fg=BADGE_FG, font=("Consolas", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Label(shortcuts, text="Clear input and keep focus ready", bg=INPUT_BG, fg=MUTED_FG, font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=(12, 0), pady=(6, 0))

        actions = tk.Frame(card, bg=CARD_BG, padx=22, pady=0)
        actions.grid(row=3, column=0, sticky="ew")
        close_button = tk.Button(
            actions,
            text="Close",
            command=self._close_about,
            bg=ACCENT,
            fg="#ffffff",
            activebackground=ACCENT_ACTIVE,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=10,
            font=("Segoe UI Semibold", 10),
            cursor="hand2",
        )
        close_button.pack(anchor="e", pady=(0, 20))

        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        x = root_x + max((root_w - width) // 2, 20)
        y = root_y + max((root_h - height) // 2, 20)
        window.geometry(f"+{x}+{y}")
        window.grab_set()
        close_button.focus_set()

    def _close_about(self) -> None:
        if self.about_window is None:
            return
        if self.about_window.winfo_exists():
            self.about_window.grab_release()
            self.about_window.destroy()
        self.about_window = None

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        text_wrap = ttk.Frame(header, style="App.TFrame")
        text_wrap.grid(row=0, column=0, sticky="w")
        ttk.Label(text_wrap, text=f"{APP_NAME} v{APP_VERSION}", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            text_wrap,
            text="Paste a column, shape it, copy it.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.live_badge = tk.Label(
            header,
            text="LIVE FORMATTING",
            bg=BADGE_BG,
            fg=BADGE_FG,
            font=("Segoe UI Semibold", 9),
            padx=12,
            pady=6,
        )
        self.live_badge.grid(row=0, column=1, sticky="e")

    def _build_controls_card(self, parent: ttk.Frame) -> None:
        card = self._create_card(parent)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        card.grid_columnconfigure(0, weight=1)

        inner = ttk.Frame(card, style="Card.TFrame", padding=(22, 18, 22, 18))
        inner.grid(row=0, column=0, sticky="ew")
        inner.columnconfigure(0, weight=1)

        ttk.Label(inner, text="Formatting Controls", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            inner,
            text="Tune the shape of each line, then copy the finished block.",
            style="CardSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 16))

        fields = ttk.Frame(inner, style="Card.TFrame")
        fields.grid(row=2, column=0, sticky="ew")
        for column in range(3):
            fields.columnconfigure(column, weight=1)

        self.prefix_entry = self._build_field(fields, 0, "Prefix", self.prefix_var)
        self.suffix_entry = self._build_field(fields, 1, "Suffix", self.suffix_var)
        self.delimiter_entry = self._build_field(fields, 2, "Delimiter", self.delimiter_var)

        actions = ttk.Frame(inner, style="Card.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)

        toggle_wrap = ttk.Frame(actions, style="Card.TFrame")
        toggle_wrap.grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(
            toggle_wrap,
            text="Add delimiter to every line",
            variable=self.trailing_var,
            command=self.update_output,
            style="Tool.TCheckbutton",
        ).grid(row=0, column=0, sticky="w")

        presets = ttk.Frame(actions, style="Card.TFrame")
        presets.grid(row=0, column=1, sticky="w")
        self.number_preset_button = self._create_action_button(
            presets,
            text="Number + comma",
            command=self.apply_number_preset,
            kind="secondary",
        )
        self.number_preset_button.grid(row=0, column=0, padx=(0, 8))
        self.quote_preset_button = self._create_action_button(
            presets,
            text="Single quote + comma",
            command=self.apply_quote_preset,
            kind="secondary",
        )
        self.quote_preset_button.grid(row=0, column=1)

        utilities = ttk.Frame(actions, style="Card.TFrame")
        utilities.grid(row=0, column=2, sticky="e")
        self.copy_button = self._create_action_button(utilities, text="Copy result", command=self.copy_output, kind="primary")
        self.copy_button.grid(row=0, column=0, padx=(0, 8))
        self.clear_button = self._create_action_button(utilities, text="Clear", command=self.clear_all, kind="quiet")
        self.clear_button.grid(row=0, column=1, padx=(0, 6))
        self.reset_button = self._create_action_button(
            utilities,
            text="Reset formatting",
            command=self.reset_formatting,
            kind="quiet",
        )
        self.reset_button.grid(row=0, column=2)

    def _build_field(self, parent: ttk.Frame, column: int, label: str, variable: tk.StringVar) -> tk.Entry:
        field = ttk.Frame(parent, style="Card.TFrame")
        field.grid(row=0, column=column, sticky="ew", padx=(0, 14) if column < 2 else 0)
        field.columnconfigure(0, weight=1)

        ttk.Label(field, text=label, style="FieldLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        entry = tk.Entry(
            field,
            textvariable=variable,
            bd=0,
            relief="flat",
            bg=INPUT_BG,
            fg=TEXT_FG,
            insertbackground=ACCENT,
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            highlightcolor=ACCENT,
            font=("Consolas", 12),
        )
        entry.grid(row=1, column=0, sticky="ew", ipady=9)
        return entry

    def _build_editor_area(self, parent: ttk.Frame) -> None:
        content = ttk.Frame(parent, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self.input_card, self.input_text, self.input_placeholder, _ = self._build_text_card(
            content,
            column=0,
            title="Source",
            subtitle="Paste raw values here, one item per line.",
            badge_text=None,
            text_bg=INPUT_BG,
            readonly=False,
            placeholder_text="Paste column values here. Each non-empty line becomes one formatted item.",
        )
        self.output_card, self.output_text, self.output_placeholder, self.output_badge = self._build_text_card(
            content,
            column=1,
            title="Formatted Result",
            subtitle="Copy the generated block directly into SQL or scripts.",
            badge_text="Waiting for input",
            text_bg=OUTPUT_BG,
            readonly=True,
            placeholder_text="Formatted output appears here as soon as you start typing on the left.",
        )

    def _build_text_card(
        self,
        parent: ttk.Frame,
        *,
        column: int,
        title: str,
        subtitle: str,
        badge_text: str | None,
        text_bg: str,
        readonly: bool,
        placeholder_text: str,
    ) -> tuple[tk.Frame, tk.Text, tk.Label, tk.Label | None]:
        outer = self._create_card(parent)
        outer.grid(row=0, column=column, sticky="nsew", padx=(0, 10) if column == 0 else (10, 0))
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(outer, style="Card.TFrame", padding=(20, 18, 20, 12))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=subtitle, style="CardSubtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        badge = None
        if badge_text is not None:
            badge = tk.Label(
                header,
                text=badge_text,
                bg=BADGE_BG,
                fg=BADGE_FG,
                font=("Segoe UI Semibold", 9),
                padx=10,
                pady=5,
            )
            badge.grid(row=0, column=1, rowspan=2, sticky="e")

        body = tk.Frame(outer, bg=CARD_BG, padx=20, pady=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        text_widget = tk.Text(
            body,
            wrap="word",
            bd=0,
            relief="flat",
            bg=text_bg,
            fg=TEXT_FG,
            insertbackground=ACCENT,
            selectbackground="#c7e3e5",
            selectforeground=TEXT_FG,
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            highlightcolor=ACCENT,
            padx=18,
            pady=18,
            font=("Consolas", 12),
            undo=True,
        )
        if readonly:
            text_widget.config(state="disabled")
        text_widget.grid(row=0, column=0, sticky="nsew")

        placeholder = tk.Label(
            body,
            text=placeholder_text,
            bg=text_bg,
            fg=SOFT_FG,
            font=("Segoe UI", 11),
            justify="left",
            anchor="nw",
            padx=20,
            pady=18,
        )
        placeholder.place(relx=0, rely=0, relwidth=1)

        return outer, text_widget, placeholder, badge

    def _build_status_bar(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent, style="App.TFrame")
        footer.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            footer,
            text="Ctrl+Enter to copy  |  Ctrl+L to clear",
            style="Status.TLabel",
        ).grid(row=0, column=1, sticky="e")

    def _create_card(self, parent: tk.Misc) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=CARD_BG,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
        )

    def _create_action_button(self, parent: tk.Misc, *, text: str, command: object, kind: str) -> tk.Button:
        palette = {
            "primary": (ACCENT, "#ffffff", ACCENT_ACTIVE),
            "secondary": (BUTTON_BG, TEXT_FG, BUTTON_ACTIVE),
            "quiet": (CARD_BG, MUTED_FG, WINDOW_BG),
        }
        bg, fg, active_bg = palette[kind]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=10,
            font=("Segoe UI Semibold", 10),
            cursor="hand2",
        )

    def _bind_events(self) -> None:
        self.input_text.bind("<<Modified>>", self._handle_input_modified)
        self.root.bind_all("<Control-Return>", self._handle_copy_shortcut)
        self.root.bind_all("<Control-l>", self._handle_clear_shortcut)
        self.root.bind_all("<Control-L>", self._handle_clear_shortcut)
        self.prefix_var.trace_add("write", self._handle_option_change)
        self.suffix_var.trace_add("write", self._handle_option_change)
        self.delimiter_var.trace_add("write", self._handle_option_change)

        for widget in (self.prefix_entry, self.suffix_entry, self.delimiter_entry, self.input_text, self.output_text):
            widget.bind("<FocusIn>", self._handle_focus_in)
            widget.bind("<FocusOut>", self._handle_focus_out)

    def _handle_copy_shortcut(self, _event: tk.Event[tk.Misc] | None) -> str:
        self.copy_output()
        return "break"

    def _handle_clear_shortcut(self, _event: tk.Event[tk.Misc] | None) -> str:
        self.clear_all()
        self._focus_input()
        return "break"

    def _focus_input(self) -> None:
        self.input_text.focus_set()
        self.input_text.mark_set("insert", "1.0")

    def _handle_focus_in(self, event: tk.Event[tk.Misc]) -> None:
        widget = event.widget
        if isinstance(widget, tk.Text):
            self._apply_text_theme(widget, widget.cget("bg"), focused=True)
        elif isinstance(widget, tk.Entry):
            widget.configure(highlightbackground=ACCENT, highlightcolor=ACCENT)

    def _handle_focus_out(self, event: tk.Event[tk.Misc]) -> None:
        widget = event.widget
        if isinstance(widget, tk.Text):
            self._apply_text_theme(widget, widget.cget("bg"), focused=False)
        elif isinstance(widget, tk.Entry):
            widget.configure(highlightbackground=CARD_BORDER, highlightcolor=ACCENT)

    def _apply_text_theme(self, widget: tk.Text, background: str, focused: bool = False) -> None:
        border = ACCENT if focused else CARD_BORDER
        widget.configure(bg=background, highlightbackground=border, highlightcolor=ACCENT)

    def _handle_input_modified(self, _event: tk.Event[tk.Misc]) -> None:
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            self.update_output()

    def _handle_option_change(self, *_args: object) -> None:
        self._sync_preset_state_from_fields()
        self.update_output()

    def _sync_preset_state_from_fields(self) -> None:
        current = (
            self.prefix_var.get(),
            self.suffix_var.get(),
            self.delimiter_var.get(),
            self.trailing_var.get(),
        )
        if current == ("", "", ",", False):
            self.active_preset = "number"
        elif current == ("'", "'", ",", False):
            self.active_preset = "quote"
        else:
            self.active_preset = "custom"
        self._refresh_preset_buttons()

    def _refresh_preset_buttons(self) -> None:
        self._set_preset_button_state(self.number_preset_button, self.active_preset == "number")
        self._set_preset_button_state(self.quote_preset_button, self.active_preset == "quote")

    def _set_preset_button_state(self, button: tk.Button, active: bool) -> None:
        if active:
            button.configure(bg=ACCENT, fg="#ffffff", activebackground=ACCENT_ACTIVE, activeforeground="#ffffff")
        else:
            button.configure(bg=BUTTON_BG, fg=TEXT_FG, activebackground=BUTTON_ACTIVE, activeforeground=TEXT_FG)

    def _current_options(self) -> FormatOptions:
        return FormatOptions(
            prefix=self.prefix_var.get(),
            suffix=self.suffix_var.get(),
            delimiter=self.delimiter_var.get(),
            trailing_delimiter=self.trailing_var.get(),
        )

    def update_output(self) -> None:
        source = self.input_text.get("1.0", "end-1c")
        formatted = format_lines(source, self._current_options())
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", formatted)
        self.output_text.config(state="disabled")
        self._set_placeholder_state(self.input_text, self.input_placeholder, not bool(source.strip()))
        self._set_placeholder_state(self.output_text, self.output_placeholder, not bool(formatted.strip()))
        self._update_status(formatted)
        self._sync_preset_state_from_fields()

    def _set_placeholder_state(self, text_widget: tk.Text, placeholder: tk.Label, visible: bool) -> None:
        if visible:
            placeholder.lift(text_widget)
            placeholder.place(relx=0, rely=0, relwidth=1)
        else:
            placeholder.place_forget()

    def _update_status(self, formatted: str) -> None:
        line_count = len([line for line in formatted.splitlines() if line])
        if line_count == 0:
            self.status_var.set("Ready for formatting")
            self.output_state_var.set("Waiting for input")
            if self.output_badge is not None:
                self.output_badge.configure(text="Waiting for input", bg=BADGE_BG, fg=BADGE_FG)
        elif line_count == 1:
            self.status_var.set("1 line formatted")
            self.output_state_var.set("Ready to copy")
            if self.output_badge is not None:
                self.output_badge.configure(text="Ready to copy", bg=SUCCESS_BG, fg=SUCCESS_FG)
        else:
            self.status_var.set(f"{line_count} lines formatted")
            self.output_state_var.set("Ready to copy")
            if self.output_badge is not None:
                self.output_badge.configure(text="Ready to copy", bg=SUCCESS_BG, fg=SUCCESS_FG)

    def apply_number_preset(self) -> None:
        self.prefix_var.set("")
        self.suffix_var.set("")
        self.delimiter_var.set(",")
        self.trailing_var.set(False)
        self.active_preset = "number"
        self._refresh_preset_buttons()
        self.update_output()
        self.status_var.set("Preset applied: Number + comma")

    def apply_quote_preset(self) -> None:
        self.prefix_var.set("'")
        self.suffix_var.set("'")
        self.delimiter_var.set(",")
        self.trailing_var.set(False)
        self.active_preset = "quote"
        self._refresh_preset_buttons()
        self.update_output()
        self.status_var.set("Preset applied: Single quote + comma")

    def copy_output(self) -> None:
        content = self.output_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        self.status_var.set("Formatted result copied to clipboard")
        self._show_copy_feedback()

    def _show_copy_feedback(self) -> None:
        if self.copy_reset_job is not None:
            self.root.after_cancel(self.copy_reset_job)
        self.copy_button.configure(text="Copied", bg=SUCCESS_BG, fg=SUCCESS_FG, activebackground=SUCCESS_BG, activeforeground=SUCCESS_FG)
        self.copy_reset_job = self.root.after(1000, self._reset_copy_button)

    def _reset_copy_button(self) -> None:
        self.copy_button.configure(text="Copy result", bg=ACCENT, fg="#ffffff", activebackground=ACCENT_ACTIVE, activeforeground="#ffffff")
        self.copy_reset_job = None

    def clear_all(self) -> None:
        self.input_text.delete("1.0", "end")
        self.update_output()
        self.status_var.set("Input cleared")

    def reset_formatting(self) -> None:
        self.apply_number_preset()
        self.status_var.set("Formatting reset to default")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = TextDelimiterApp()
    app.run()


