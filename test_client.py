import ssl
import os # Import the os module to work with file paths
from kmip.services.kmip_client import KMIPProxy

# Define the base directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script directory
keyfile_path = os.path.join(script_dir, 'server.key')
certfile_path = os.path.join(script_dir, 'server.crt')
ca_certs_path = os.path.join(script_dir, 'server.crt')

# --- Verification Step (Optional but recommended) ---
# Check if the files exist before initializing the proxy
if not os.path.exists(keyfile_path):
    raise FileNotFoundError(f"Key file not found at: {keyfile_path}")
if not os.path.exists(certfile_path):
    raise FileNotFoundError(f"Certificate file not found at: {certfile_path}")
if not os.path.exists(ca_certs_path):
    raise FileNotFoundError(f"CA certificate file not found at: {ca_certs_path}")
# --- End Verification Step ---


# Initialize the low-level proxy with absolute paths
proxy = KMIPProxy(
    host='127.0.0.1',
    port=5696,
    keyfile=keyfile_path,
    certfile=certfile_path,
    ca_certs=ca_certs_path,
    cert_reqs=ssl.CERT_NONE,            # disable verification; use ssl.CERT_REQUIRED to enforce it
    ssl_version='PROTOCOL_TLSv1_2',    # Pass the protocol name as a string
    do_handshake_on_connect=True,
    suppress_ragged_eofs=True
)

# Open, call discover_versions, then clean up
try:
    proxy.open()
    print("Connection opened successfully.")
    result = proxy.discover_versions()
    # Access the protocol_versions attribute from the result object
    print(f"Supported KMIP versions: {result.protocol_versions}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    proxy.close()
    print("Connection closed.")
