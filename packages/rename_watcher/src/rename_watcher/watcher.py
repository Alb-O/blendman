"""
Core watcher logic for rename_watcher.
Wraps watchdog to monitor file and directory events recursively.
"""

from typing import Optional, Callable, Any
import threading
import time
import sys
import os
try:
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
except ImportError:
	Observer = None
	FileSystemEventHandler = object

from .path_map import PathInodeMap
from .event_processor import EventProcessor

class Watcher:
	"""
	Watches directories for file and directory events (create, delete, move, rename),
	and emits high-level events using PathInodeMap and EventProcessor.
	"""

	def __init__(
		self,
		path: str,
		on_event: Optional[Callable[[Any], None]] = None,
		path_map: Optional[PathInodeMap] = None,
		event_processor: Optional[EventProcessor] = None,
		matcher: Optional[Callable[[str], bool]] = None,
	):
		self.path = path
		self.on_event = on_event
		self.matcher = matcher
		self._observer = None
		self._thread = None
		self._running = False
		self._path_map = path_map or PathInodeMap()
		self._event_processor = event_processor or EventProcessor(self._path_map, self._emit_high_level)

	def start(self) -> None:
		if Observer is None:
			raise ImportError("watchdog is required for file system watching. Please install it.")
		if self._observer is not None:
			return  # Already started
		event_handler = self._make_event_handler()
		self._observer = Observer()
		self._observer.schedule(event_handler, self.path, recursive=True)
		self._observer.start()
		self._running = True
		self._thread = threading.Thread(target=self._run_loop, daemon=True)
		self._thread.start()

	def stop(self) -> None:
		self._running = False
		if self._observer:
			self._observer.stop()
			self._observer.join()
			self._observer = None
		if self._thread:
			self._thread.join(timeout=1)
			self._thread = None

	def _run_loop(self):
		try:
			while self._running:
				time.sleep(0.2)
		except KeyboardInterrupt:
			self.stop()

	def _make_event_handler(self):
		parent = self
		class Handler(FileSystemEventHandler):
			def on_created(self, event):
				print(f"[Watcher] Raw event: created {event.src_path}")
				parent._handle_raw_event({"type": "created", "src_path": event.src_path, "is_directory": event.is_directory})
			def on_deleted(self, event):
				print(f"[Watcher] Raw event: deleted {event.src_path}")
				parent._handle_raw_event({"type": "deleted", "src_path": event.src_path, "is_directory": event.is_directory})
			def on_moved(self, event):
				print(f"[Watcher] Raw event: moved {event.src_path} -> {event.dest_path}")
				parent._handle_raw_event({"type": "moved", "src_path": event.src_path, "dest_path": event.dest_path, "is_directory": event.is_directory})
			def on_modified(self, event):
				# Optionally handle modified events
				pass
		return Handler()

	def _handle_raw_event(self, event: dict):
		print(f"[Watcher] Handling raw event: {event}")
		# Optionally filter with matcher
		path = event.get("src_path") or event.get("dest_path")
		if self.matcher and path and not self.matcher(path):
			print(f"[Watcher] Event filtered by matcher: {path}")
			return
		# Track inodes for created files
		if event["type"] == "created" and not event.get("is_directory"):
			try:
				inode = os.stat(event["src_path"]).st_ino
				self._path_map.add(event["src_path"], inode)
				print(f"[Watcher] Added inode mapping: {event['src_path']} -> {inode}")
			except Exception as e:
				print(f"[Watcher] Failed to stat created file: {e}")
		self._event_processor.process(event)

	def _emit_high_level(self, event_type: str, payload: dict):
		payload = dict(payload)
		payload["type"] = event_type
		print(f"[Watcher] Emitting high-level event: {payload}")
		if self.on_event:
			self.on_event(payload)
