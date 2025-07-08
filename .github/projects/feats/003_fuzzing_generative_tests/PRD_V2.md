# PRD_V2: Bullet-Proof Fuzzing & Generative Tests for Rename Watcher

## Background

The `rename_watcher` package must detect file and directory renames/moves with 100% certainty and accuracy, under all conditions. To guarantee reliability, the test suite must go far beyond basic unit tests, employing both fuzzing and property-based (generative) testing to uncover edge cases, race conditions, and platform-specific issues. This document supersedes previous versions and incorporates best practices and up-to-date research on all referenced tools and APIs.

## Goals

- Ensure the watcher never misses, misattributes, or duplicates rename/move events.
- Harden the watcher against all known and unknown edge cases, including those arising from OS, filesystem, or user behavior.
- Provide a test suite that is maintainable, extensible, and runs in CI across all supported platforms.

## Requirements

- **Fuzz Testing:**
  - Randomized, high-frequency sequences of file and directory operations (create, delete, rename, move, modify).
  - Generation of edge-case filenames (long, unicode, reserved, control characters).
  - Deeply nested directory structures and rapid, concurrent operations.
  - Monitoring for crashes, hangs, resource leaks, and missed/incorrect events.
  - Note: True concurrent fuzzing in Python is non-trivial due to the GIL and filesystem locks; design with care.
- **Property-Based Testing:**
  - Use Hypothesis stateful testing (`RuleBasedStateMachine` or `Bundle`) as the primary approach for modeling operation sequences and invariants.
  - Define invariants (e.g., "the watcher’s state always matches the real filesystem").
  - Implement or tune custom shrinking strategies for complex stateful scenarios.
  - Random generation of valid directory trees and operation sequences.
  - Automatic shrinking of failing cases to minimal reproducible examples.
- **Coverage:**
  - Explicit tests for all identified edge cases and failure modes (see below).
  - Tests must run on Linux, Windows, and macOS, and on multiple filesystems where possible.
  - Maintain a compatibility matrix for platform-specific event API differences.
- **Tooling:**
  - Use `pytest` for orchestration, `Hypothesis` (with stateful testing) for property-based testing, and `pyfakefs` for fast simulation of filesystem logic.
  - Use real filesystems and real event APIs for integration tests, especially for event delivery semantics and platform-specific behaviors.
  - AFL/python-afl may be used experimentally, but are not required for Python code.
  - All test files must be <500 lines; use shared utility modules for test data and helpers.
  - All property-based and fuzz tests must log minimal failing cases and measure code coverage (e.g., via `pytest-cov`).

## Edge Cases & Failure Modes

- Path length limits (max path, max filename)
- Special characters (unicode, control, reserved names)
- Case-only renames on case-insensitive filesystems
- Deeply nested structures
- Symlinks and hardlinks (note: pyfakefs has partial support; validate on real filesystems)
- Open file handles during rename/move
- Cross-filesystem moves
- Rapid, chained renames (A→B→C)
- Directory overwrites
- Permission errors
- Hidden/system files
- Missed, duplicate, or out-of-order events
- Resource exhaustion (file descriptors, disk space; simulate in isolated environments only)
- Platform-specific event semantics (see compatibility matrix)
- Watcher restarts mid-operation
- Path traversal and malformed input attacks

## Test Strategy

### Fuzz Testing
- Use automated scripts to generate and execute random sequences of file/directory operations.
- Include edge-case names, deep nesting, and concurrent operations.
- Monitor for program stability and event correctness.
- Run on both simulated (`pyfakefs`) and real filesystems.
- For concurrency, design tests to avoid GIL and locking pitfalls.

### Property-Based Testing
- Use Hypothesis stateful testing as the primary approach.
- Define invariants, e.g.:
  - Every rename/move event matches a real filesystem change.
  - The watcher’s state matches the actual filesystem after any operation sequence.
  - No duplicate or missing events.
- Implement custom shrinking for complex operation sequences.
- Validate event order, timing, and correctness, but tolerate minor timing variations due to platform event delivery semantics.

### Test Suite Structure
- `/tests/rename_watcher/`
  - `test_fuzzing.py`: Fuzz tests for stability and event correctness.
  - `test_properties.py`: Property-based tests for invariants (using Hypothesis stateful testing).
  - `test_edge_cases.py`: Explicit tests for each edge case/failure mode.
  - `test_platforms.py`: Platform-specific and real-filesystem tests.
  - `utils.py`: Shared test data generators and helpers.
- All test files must be <500 lines; refactor as needed.

### Example Invariants
- After any valid sequence of operations, the watcher’s state matches the real filesystem.
- Every rename/move event is reported exactly once, with correct source and destination.
- No event is missed, duplicated, or misattributed, even under high load or concurrent operations.

### Event Validation
- Validate logical correctness of events, not strict timing/order, unless required by the API.
- Log and save minimal failing cases for all property-based and fuzz tests.

### Resource Exhaustion
- Simulate resource exhaustion (file descriptors, disk space) only in isolated environments; skip in CI if disruptive.

### Documentation and Reporting
- Maintain a compatibility matrix for platform-specific event API differences (inotify, FSEvents, ReadDirectoryChangesW).
- Require code coverage measurement and reporting.
- All failures must be logged with minimal reproducible cases.


## Practical Guidance & Deep Dives

### Hypothesis (Property-Based Testing for Python)
**Stateful Testing:** Use `RuleBasedStateMachine` for modeling sequences of filesystem operations and invariants. See [Stateful Testing Guide](https://hypothesis.readthedocs.io/en/latest/stateful.html).

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, precondition
from hypothesis import strategies as st

class FileSystemMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.files = set()

    @rule(filename=st.text(min_size=1, max_size=32))
    def create_file(self, filename):
        # Simulate file creation
        self.files.add(filename)
        # Invariant: file should exist
        assert filename in self.files

    @precondition(lambda self: len(self.files) > 0)
    @rule()
    def delete_file(self):
        filename = self.files.pop()
        # Invariant: file should not exist
        assert filename not in self.files

TestFS = FileSystemMachine.TestCase
```

**Custom Shrinking:** For complex stateful scenarios, implement custom shrinking to minimize failing cases. See [How-to: Custom Shrinking](https://hypothesis.readthedocs.io/en/latest/how-to.html#shrinking).

**Edge Cases:** Use strategies like `st.text()` with custom filters to generate edge-case filenames (unicode, reserved, long, etc.).

```python
@given(st.text(alphabet=st.characters(blacklist_categories=['Cs']), min_size=1, max_size=255))
def test_filename_edge_cases(name):
    # Test watcher with edge-case filenames
    ...
```

**Best Practices:** Review [How-to Guides](https://hypothesis.readthedocs.io/en/latest/how-to/index.html) and [Explanations](https://hypothesis.readthedocs.io/en/latest/explanation/index.html) for advanced usage.

### pyfakefs (Filesystem Mocking for Python Tests)
**Scope:** Mocks Python’s file system modules in-memory for fast, isolated tests. See [Usage Guide](https://pytest-pyfakefs.readthedocs.io/en/latest/usage.html).

```python
def test_file_creation(fs):
    fs.create_file('/foo/bar.txt', contents='hello')
    assert open('/foo/bar.txt').read() == 'hello'
```

**Limitations:** Does not patch C extensions or simulate OS-level event APIs (inotify, FSEvents, etc). See [Limitations](https://pytest-pyfakefs.readthedocs.io/en/latest/intro.html#limitations).

**Partial Symlink/Hardlink Support:** Validate symlink/hardlink edge cases on real filesystems.

```python
def test_symlink(fs):
    fs.create_file('/foo/target.txt')
    fs.create_symlink('/foo/link.txt', '/foo/target.txt')
    assert os.path.islink('/foo/link.txt')
```

**Emulation:** Can emulate Linux, macOS, or Windows behaviors, but not all platform quirks.

### AFL (American Fuzzy Lop) and python-afl
**Primary Use:** AFL is a coverage-guided fuzzer for native binaries (C/C++). See [AFL README](https://lcamtuf.coredump.cx/afl/README.txt).

```c
// Example: Fuzzing a C extension (not pure Python)
// Compile with AFL instrumentation, then run:
// afl-fuzz -i input_dir -o output_dir -- ./your_binary @@
```

**Python Fuzzing:** Use [python-afl](http://jwilk.net/software/python-afl) for native fuzzing of Python C extensions, but for pure Python, prefer Hypothesis.

```python
# Example: python-afl usage
import afl
import sys

afl.init()
for line in sys.stdin:
    # Fuzz your C extension or parser here
    pass
```

**AFL++:** For advanced features and active maintenance, see [AFL++](https://github.com/AFLplusplus/AFLplusplus).

### Linux: inotify
**API:** See [inotify(7) man page](https://man7.org/linux/man-pages/man7/inotify.7.html).

```python
import os
import sys
import select
import struct

fd = os.inotify_init()
wd = os.inotify_add_watch(fd, b'/tmp', os.IN_CREATE | os.IN_DELETE | os.IN_MOVED_FROM | os.IN_MOVED_TO)

while True:
    rlist, _, _ = select.select([fd], [], [])
    for event in os.read(fd, 4096):
        # Parse event struct, match IN_MOVED_FROM/IN_MOVED_TO by cookie
        pass
```

**Event Semantics:** Events are inode-based, not recursive (must add watches for subdirs), and may be coalesced. Use the `cookie` field to match IN_MOVED_FROM/IN_MOVED_TO pairs for renames.

**Limitations:** No user/process info, not reliable for network filesystems, not recursive, event queue can overflow (IN_Q_OVERFLOW), and event order is not always atomic for renames.

**Best Practices:** Rebuild state/cache on overflow or inconsistency. See [inotify_add_watch(2)](https://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) and [inotifywait(1)](https://man7.org/linux/man-pages/man1/inotifywait.1.html) for CLI usage.

### Windows: ReadDirectoryChangesW
**API:** See [ReadDirectoryChangesW docs](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-readdirectorychangesw).

```python
# Example: Using pywin32 to monitor directory changes
import win32file, win32con

path = 'C:\\watched_dir'
handle = win32file.CreateFile(
    path,
    win32con.GENERIC_READ,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)

while True:
    results = win32file.ReadDirectoryChangesW(
        handle,
        1024,
        True,  # Watch subtree
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
        win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | win32con.FILE_NOTIFY_CHANGE_SIZE |
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | win32con.FILE_NOTIFY_CHANGE_SECURITY,
        None,
        None
    )
    for action, file in results:
        print('Action:', action, 'File:', file)
```

**Event Semantics:** Can monitor subtrees, but buffer overflows discard all changes since last read. Use [FILE_NOTIFY_INFORMATION](https://learn.microsoft.com/en-us/windows/desktop/api/winnt/ns-winnt-file_notify_information) for event details.

**Limitations:** Buffer size limits (esp. over network shares), no direct mapping to inotify/FSEvents event types, and some changes (e.g., security) may not be reported depending on filter.

**Best Practices:** Use asynchronous I/O for high-frequency changes, and enumerate directory on overflow.

### macOS: FSEvents
**API:** See [FSEvents docs](https://developer.apple.com/documentation/coreservices/file_system_events).

```python
# Example: Using macFSEvents (third-party Python binding)
from fsevents import Observer, Stream

def callback(event):
    print(event.name, event.mask)

observer = Observer()
stream = Stream(callback, '/tmp', file_events=True)
observer.schedule(stream)
observer.start()
# ...
observer.stop()
observer.join()
```

**Event Semantics:** Monitors entire directory trees, but events are coalesced and may be delivered with delay. No per-file event granularity.

**Limitations:** No guarantee of event delivery order, and events may be missed if the event queue overflows.

**Best Practices:** Use event IDs to detect missed events and resync state as needed.

## References
- **Hypothesis:**
  - [Documentation](https://hypothesis.readthedocs.io/)
  - [Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html)
  - [Stateful Testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)
  - [How-to Guides](https://hypothesis.readthedocs.io/en/latest/how-to/index.html)
  - [Explanations](https://hypothesis.readthedocs.io/en/latest/explanation/index.html)
- **pyfakefs:**
  - [Documentation](https://github.com/jmcgeheeiv/pyfakefs)
  - [Usage Guide](https://pytest-pyfakefs.readthedocs.io/en/latest/usage.html)
  - [Limitations](https://pytest-pyfakefs.readthedocs.io/en/latest/intro.html#limitations)
- **AFL:**
  - [AFL README](https://lcamtuf.coredump.cx/afl/README.txt)
  - [python-afl](http://jwilk.net/software/python-afl)
  - [AFL++](https://github.com/AFLplusplus/AFLplusplus)
- **Filesystem Event APIs:**
  - [Linux: inotify(7)](https://man7.org/linux/man-pages/man7/inotify.7.html)
  - [inotify_add_watch(2)](https://man7.org/linux/man-pages/man2/inotify_add_watch.2.html)
  - [inotifywait(1)](https://man7.org/linux/man-pages/man1/inotifywait.1.html)
  - [Windows: ReadDirectoryChangesW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-readdirectorychangesw)
  - [FILE_NOTIFY_INFORMATION](https://learn.microsoft.com/en-us/windows/desktop/api/winnt/ns-winnt-file_notify_information)
  - [macOS: FSEvents](https://developer.apple.com/documentation/coreservices/file_system_events)

---

**This PRD is the authoritative guide for implementing bullet-proof, generative and fuzzing-based tests for the rename watcher. All future test code must adhere to these requirements and strategies.**
