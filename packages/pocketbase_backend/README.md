PocketBase Integration
======================

This project uses [PocketBase](https://pocketbase.io/) as a backend service. PocketBase is a Go application, not a Python library, so it is bundled as a binary in `packages/pocketbase/` and managed from Python.


Setup
-----
1. The PocketBase binary is located in `packages/pocketbase/pocketbase`.
2. If you need to update or re-extract the binary, run:

    cd packages/pocketbase
    python3 extract_pocketbase.py


3. To start/stop PocketBase from the command line using uv, run:

    uv run pocketbase-manager start

   To stop (if running in the background or another terminal):

    uv run pocketbase-manager stop

   You can also specify a port:

    uv run pocketbase-manager start --port 8091

4. To start/stop PocketBase from Python, use the `PocketBaseManager` class:

```python
from packages.pocketbase.pocketbase_manager import PocketBaseManager
pb = PocketBaseManager()
pb.start()
# ... interact with PocketBase at http://127.0.0.1:8090 ...
pb.stop()
```

5. Interact with PocketBase using its REST API (e.g., with the `requests` library).

Notes
-----
- The PocketBase server will create `pb_data` and `pb_migrations` directories in the same folder as the binary.
- For more information, see the [PocketBase documentation](https://pocketbase.io/docs/).
- If you need to automate binary updates, consider scripting the download and extraction process.
