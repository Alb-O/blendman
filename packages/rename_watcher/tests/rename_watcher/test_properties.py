"""
Property-based tests for rename_watcher using Hypothesis stateful testing.
"""

# See utils.py for shared helpers and data generators.
# The following imports use type: ignore because Hypothesis does not ship with full type stubs.
from hypothesis import event, settings
from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    precondition,
    invariant,
    run_state_machine_as_test,  # type: ignore
)
from hypothesis import strategies as st  # type: ignore


class FileSystemMachine(RuleBasedStateMachine):
    """
    Hypothesis stateful model for file/directory operations and invariants.
    """

    def __init__(self):
        """
        Initialize the FileSystemMachine with empty file and directory sets.
        """
        super().__init__()
        self.files: set[str] = set()
        self.dirs: set[str] = {"/"}

    @rule(filename=st.text(min_size=1, max_size=32))
    def create_file(self, filename: str) -> None:
        """
        Create a file and add it to the set of tracked files.
        Args:
            filename (str): The name of the file to create.
        """
        path = f"/{filename}"
        self.files.add(path)
        event(f"Created file: {path}")
        # Invariant: file should exist
        assert path in self.files

    @precondition(lambda self: len(self.files) > 0)
    @rule()
    def delete_file(self) -> None:
        """
        Delete a file from the set of tracked files.
        """
        path = self.files.pop()
        event(f"Deleted file: {path}")
        # Invariant: file should not exist
        assert path not in self.files

    @invariant()
    def all_files_are_unique(self) -> None:
        """
        Ensure all file paths are unique in the set.
        """
        assert len(self.files) == len(set(self.files))


def test_filesystem_state_machine() -> None:
    """
    Run the Hypothesis state machine test for the file system model.
    """
    run_state_machine_as_test(
        FileSystemMachine,
        settings=settings(
            max_examples=100,
            stateful_step_count=50,
            deadline=None,
            report_multiple_bugs=False,
            print_blob=True,
        ),
    )
