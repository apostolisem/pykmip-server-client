# PyKMIP Server and Client Example

This project demonstrates a simple KMIP server and client using the `pykmip` library.

## Setup

1.  **Clone the repository (or download the files).**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Generate Certificates:**
    The server requires a private key (`server.key`) and a certificate (`server.crt`). You can generate a self-signed certificate for testing using OpenSSL:
    ```bash
    openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt
    ```
    Place the generated `server.key` and `server.crt` files in the project's root directory (or update the paths in `server.conf` and the client scripts if you place them elsewhere).

## Running the Server

1.  **Configure the server:** Edit `server.conf` if needed. By default, it listens on `127.0.0.1:5696` and uses `server.crt` and `server.key`.
2.  **Start the server:**
    ```bash
    pykmip-server -f server.conf
    ```
    OR
    ```bash
    python -m kmip.services.server --config server.conf
    ```
    The server will start and log output to the console. It will create a `pykmip.db` file to store key information.

## Running the Client

Three example client scripts are provided:

*   `test_client.py`: Connects to the server and discovers supported KMIP versions.
*   `key_retrieval.py`: Connects to the server, creates a new AES-256 symmetric key, and then retrieves it.
*   `read_all_keys.py`: Connects to the server and retrieves the UUIDs and details of all managed objects (keys, certificates, etc.).

Run them like standard Python scripts:

```bash
python test_client.py
```

```bash
python key_retrieval.py
```

```bash
python read_all_keys.py
```

**Note:** The client scripts expect `server.key` and `server.crt` to be present in the same directory for client-side authentication/TLS setup. Ensure these files match those used by the server configuration.
