import ssl
import os
from kmip.pie.client import ProxyKmipClient
from kmip.pie import objects
from kmip.pie import client
from kmip.core import enums, exceptions

# Define the base directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script directory
keyfile_path = os.path.join(script_dir, 'server.key')
certfile_path = os.path.join(script_dir, 'server.crt')
ca_certs_path = os.path.join(script_dir, 'server.crt')

# --- Verification Step (Optional but recommended) ---
# Check if the files exist before initializing the client
if not os.path.exists(keyfile_path):
    raise FileNotFoundError(f"Key file not found at: {keyfile_path}")
if not os.path.exists(certfile_path):
    raise FileNotFoundError(f"Certificate file not found at: {certfile_path}")
if not os.path.exists(ca_certs_path):
    raise FileNotFoundError(f"CA certificate file not found at: {ca_certs_path}")
# --- End Verification Step ---

# Configure the client
kmip_client = ProxyKmipClient(
    hostname='127.0.0.1',
    port=5696,
    cert=certfile_path,
    key=keyfile_path,
    ca=ca_certs_path,
    ssl_version='PROTOCOL_TLSv1_2'
    # Removed 'cert_reqs=ssl.CERT_NONE' as it's not a valid argument for ProxyKmipClient
)

key_uuid = None

try:
    # Open the connection
    with kmip_client:
        print("Connection opened successfully.")

        # 1. Create a symmetric key
        print("Creating a symmetric key...")
        create_result = kmip_client.create(
            enums.CryptographicAlgorithm.AES,
            256 # Length in bits
        )

        # Check if the result is a string (UUID) or an object with status
        if isinstance(create_result, str):
            key_uuid = create_result
            print(f"Symmetric key created successfully. UUID: {key_uuid}")
        elif create_result.result_status == enums.ResultStatus.SUCCESS:
            key_uuid = create_result.uuid
            print(f"Symmetric key created successfully. UUID: {key_uuid}")
        else:
            # Handle potential error object if not a string and not success
            status = getattr(create_result, 'result_status', 'UNKNOWN')
            reason = getattr(create_result, 'result_reason', 'UNKNOWN')
            message = getattr(create_result, 'result_message', 'UNKNOWN')
            print(f"Failed to create key. Status: {status}")
            print(f"Reason: {reason}")
            print(f"Message: {message}")
            exit(1) # Exit if creation failed

        # 2. Retrieve the created key
        if key_uuid:
            print(f"Retrieving key with UUID: {key_uuid}...")
            # get() returns the object directly on success or raises OperationFailure
            retrieved_key = kmip_client.get(key_uuid)

            # If get() succeeded, retrieved_key is the managed object
            if isinstance(retrieved_key, objects.SymmetricKey):
                print("Key retrieved successfully.")
                # The key material is typically in retrieved_key.value
                # Be cautious printing raw key material
                print(f"Retrieved Key Type: {type(retrieved_key)}")
                print(f"Retrieved Key Value (hex): {retrieved_key.value.hex() if retrieved_key.value else 'N/A'}")
                # You might want other attributes like activation date, etc.
                # print(f"Activation Date: {retrieved_key.activation_date}")
            else:
                # This case might occur if the UUID exists but isn't a SymmetricKey
                print(f"Retrieved object is not a SymmetricKey: {type(retrieved_key)}")

# Correct the exception name
except exceptions.OperationFailure as e:
    print(f"A KMIP operation failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # The 'with' statement handles closing the connection automatically
    print("Connection closed.")
