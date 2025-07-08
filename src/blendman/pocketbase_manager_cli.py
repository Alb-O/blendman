"""
CLI entry point for managing the PocketBase server from the main src package.
"""

import argparse
import os
from typing import Optional
import subprocess
import time


class PocketBaseManager:
    """
    Manages the PocketBase server process.
    """

    def __init__(self, binary_path: Optional[str] = None, port: int = 8090):
        """
        Args:
            binary_path (str, optional): Path to the PocketBase binary. Defaults to './pocketbase_bin'.
            port (int): Port to run PocketBase on.
        """
        self.binary_path = binary_path or os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../packages/pocketbase/pocketbase_bin"
            )
        )
        self.port = port
        self.process: Optional[subprocess.Popen[bytes]] = None

    def start(self):
        """
        Starts the PocketBase server as a subprocess.
        """
        if self.process is not None:
            raise RuntimeError("PocketBase is already running.")
        self.process = subprocess.Popen(
            [self.binary_path, "serve", "--http", f"127.0.0.1:{self.port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Wait a moment for the server to start
        time.sleep(2)
        print(f"PocketBase started on http://127.0.0.1:{self.port}")

    def stop(self):
        """
        Stops the PocketBase server subprocess.
        """
        if self.process is None:
            print("PocketBase is not running.")
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        print("PocketBase stopped.")
        self.process = None


def main():
    """
    CLI entry point for starting/stopping PocketBase server.
    """
    parser = argparse.ArgumentParser(description="Manage PocketBase server.")
    parser.add_argument(
        "command", choices=["start", "stop"], help="Command to execute."
    )
    parser.add_argument(
        "--port", type=int, default=8090, help="Port to run PocketBase on."
    )
    args = parser.parse_args()

    manager = PocketBaseManager(port=args.port)
    if args.command == "start":
        manager.start()
        print("Press Ctrl+C to stop PocketBase.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
    elif args.command == "stop":
        manager.stop()


if __name__ == "__main__":
    main()
