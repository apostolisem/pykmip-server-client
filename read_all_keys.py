import ssl
import os
from kmip.pie.client import ProxyKmipClient
from kmip.pie import objects
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

try:
    # Open the connection
    with kmip_client:
        print("Connection opened successfully.")

        # 1. Locate all managed object UUIDs
        print("Locating all managed object UUIDs...")
        locate_result = kmip_client.locate() # No arguments needed to locate all

        all_uuids = [] # Initialize empty list for UUIDs

        # Check the type of the locate result
        if isinstance(locate_result, list):
            # If it's a list, assume success and these are the UUIDs
            all_uuids = locate_result
            print(f"Found {len(all_uuids)} key UUID(s): {all_uuids}")
        elif hasattr(locate_result, 'result_status'):
             # If it's an object with a status attribute
             if locate_result.result_status == enums.ResultStatus.SUCCESS:
                # Get UUIDs from the object
                all_uuids = getattr(locate_result, 'uuids', []) # Use getattr for safety
                print(f"Found {len(all_uuids)} key UUID(s): {all_uuids}")
             else:
                # Handle error object
                status = getattr(locate_result, 'result_status', 'UNKNOWN')
                reason = getattr(locate_result, 'result_reason', 'UNKNOWN')
                message = getattr(locate_result, 'result_message', 'UNKNOWN')
                print(f"Failed to locate keys. Status: {status}")
                print(f"Reason: {reason}")
                print(f"Message: {message}")
                exit(1) # Exit if locate failed
        else:
            # Handle unexpected return type from locate()
            print(f"Unexpected result type from locate: {type(locate_result)}")
            exit(1)


        # 2. Retrieve each key by UUID
        if not all_uuids:
            print("No keys found on the server.")
        else:
            print("\nRetrieving details for each key...")
            for key_uuid in all_uuids:
                print(f"\n--- Retrieving key with UUID: {key_uuid} ---")
                try:
                    # get() returns the object directly on success or raises OperationFailure
                    retrieved_object = kmip_client.get(key_uuid)

                    # Print basic info for any managed object
                    print(f"Retrieved Object Type: {type(retrieved_object)}")
                    # Add more details based on object type if needed
                    if isinstance(retrieved_object, objects.SymmetricKey):
                        print("Object is a Symmetric Key.")
                        # Be cautious printing raw key material
                        print(f"Key Value (hex): {retrieved_object.value.hex() if retrieved_object.value else 'N/A'}")
                    elif isinstance(retrieved_object, objects.PublicKey):
                        print("Object is a Public Key.")
                        # Public keys are generally safe to display
                        print(f"Key Value (hex): {retrieved_object.value.hex() if retrieved_object.value else 'N/A'}")
                    elif isinstance(retrieved_object, objects.PrivateKey):
                        print("Object is a Private Key.")
                        # Avoid printing private key material unless absolutely necessary
                        print("Private key material not displayed for security.")
                    elif isinstance(retrieved_object, objects.Certificate):
                         print("Object is a Certificate.")
                         # Certificate details might be useful
                         print(f"Certificate Type: {retrieved_object.certificate_type}")
                         # print(f"Certificate Value (hex): {retrieved_object.value.hex() if retrieved_object.value else 'N/A'}") # Can be large
                    else:
                        print("Object type is not specifically handled by this script.")
                        # You could potentially access common attributes like activation date etc.
                        # print(f"Activation Date: {getattr(retrieved_object, 'activation_date', 'N/A')}")

                except exceptions.OperationFailure as get_e:
                    print(f"Failed to retrieve key {key_uuid}: {get_e}")
                except Exception as get_e_unexp:
                     print(f"An unexpected error occurred retrieving key {key_uuid}: {get_e_unexp}")

# Correct the exception name
except exceptions.OperationFailure as e:
    print(f"A KMIP operation failed during locate or connection: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # The 'with' statement handles closing the connection automatically
    print("\nConnection closed.")
