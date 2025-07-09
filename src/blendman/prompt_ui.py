"""Interactive full-screen UI using prompt_toolkit."""

from __future__ import annotations

import io
import shlex
import sys
import logging
from typing import List

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.patch_stdout import patch_stdout
from pygments.lexers.python import PythonLexer

from rich.console import Console

from .cli import app

console = Console()


class BufferIO(io.TextIOBase):
    """File-like object that writes to a prompt_toolkit buffer."""

    def __init__(self, buffer: Buffer) -> None:
        self.buffer = buffer

    def write(self, data: str) -> int:  # type: ignore[override]
        self.buffer.insert_text(data)
        return len(data)

    def flush(self) -> None:  # noqa: D401 - no-op
        """Flush is a no-op."""


class BufferLogHandler(logging.Handler):
    """Logging handler that writes log records to a buffer."""

    def __init__(self, buffer: Buffer) -> None:
        super().__init__()
        self.buffer = buffer
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        msg = self.format(record)
        self.buffer.insert_text(msg + "\n")


class BlendmanApp:
    """Full-screen application with command input and log panel."""

    def __init__(self) -> None:
        self.history = InMemoryHistory()
        self.output_buffer = Buffer(read_only=True)
        self.log_buffer = Buffer(read_only=True)
        self.stdout_io = BufferIO(self.output_buffer)
        self.stderr_io = BufferIO(self.output_buffer)
        self.log_handler = BufferLogHandler(self.log_buffer)
        logging.getLogger().addHandler(self.log_handler)

        self.input_field = TextArea(
            height=1,
            prompt="blendman> ",
            history=self.history,
            multiline=False,
            lexer=PygmentsLexer(PythonLexer),
            completer=WordCompleter(
                ["watcher", "config", "backend", "pocketbase", "help", "exit", "quit"],
                ignore_case=True,
            ),
        )
        self.output_field = TextArea(scrollbar=True, focusable=False)
        self.output_field.buffer = self.output_buffer
        self.log_field = TextArea(scrollbar=True, focusable=False)
        self.log_field.buffer = self.log_buffer

        body = VSplit(
            [
                self.output_field,
                Window(width=1, char="|", style="class:line"),
                self.log_field,
            ]
        )

        self.root_container = HSplit(
            [
                Window(
                    height=1,
                    content=FormattedTextControl(self._get_titlebar_text),
                    align=WindowAlign.CENTER,
                ),
                Window(height=1, char="-", style="class:line"),
                body,
                self.input_field,
            ]
        )

        kb = KeyBindings()

        @kb.add("c-c", eager=True)
        @kb.add("c-q", eager=True)
        def _(event) -> None:
            event.app.exit()

        self.application = Application(
            layout=Layout(self.root_container, focused_element=self.input_field),
            key_bindings=kb,
            mouse_support=True,
            full_screen=True,
            style=Style.from_dict({"line": "fg:#004444"}),
        )

    def _get_titlebar_text(self) -> List[tuple]:
        return [
            ("class:title", " Blendman CLI (Ctrl-Q to quit) "),
        ]

    def run_command(self, text: str) -> None:
        if not text.strip():
            return
        if text.strip() in {"exit", "quit"}:
            self.application.exit()
            return
        args = shlex.split(text)
        with patch_stdout(raw=True):
            original_stdout, original_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = self.stdout_io, self.stderr_io
            try:
                app(args, standalone_mode=False)
            except SystemExit as exc:
                if exc.code != 0:
                    self.stdout_io.write(f"Command failed with code {exc.code}\n")
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.stdout_io.write(f"Error: {exc}\n")
            finally:
                sys.stdout, sys.stderr = original_stdout, original_stderr

    def run(self) -> None:
        def accept(buff: Buffer) -> bool:
            text = buff.text
            self.input_field.buffer.reset()
            self.run_command(text)
            return True

        self.input_field.accept_handler = accept

        with patch_stdout(raw=True):
            self.application.run()


def run_shell() -> None:
    """Start the Blendman interactive application."""
    BlendmanApp().run()
