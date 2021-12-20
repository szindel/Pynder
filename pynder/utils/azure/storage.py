# standard library
from datetime import datetime
import os

# non standard lib
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError


def test_blob_connection(cnxn_str):
    try:
        assert cnxn_str
        BlobServiceClient.from_connection_string(cnxn_str).get_account_information()
        return True
    except Exception:
        return False


def create_storage_container_client(cnxn_str, container):
    """Function that creates the azure storage container client from connection string

    Mind you: connections are only made when an actual file is uploaded/downloaded.

    Args:
        cnxn_str: str
        container: str

    Returns: azure container client

    """
    return BlobServiceClient.from_connection_string(cnxn_str).get_container_client(
        container
    )


def download_file_from_blob_in_memory(container_client, path_blob):
    """Function that downloads a file from a azure storage container into memory

    Args:
        container_client: azure container client
        path_blob: str

    Returns:
        bytes

    """
    assert path_blob[0] != "/", "path blob file should not start with /"

    try:
        return container_client.download_blob(path_blob).readall()
    except ResourceNotFoundError:
        print("Blobfile not found.")
        return None


def download_file_from_blob(container_client, blobname, target_path):
    """Function that downloads a file from an azure storage container into a local location

    Args:
        container_client: azure container client
        blobname: str
        target_path: str

    Returns: None

    """
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(target_path, "wb") as blob_file:
        download_stream = container_client.download_blob(blobname)
        blob_file.write(download_stream.readall())

    assert os.path.isfile(target_path), f"Download failed - file: {blobname}"
    print(
        f"Info - Download successful - file {blobname} \n"
        f"Info - from {container_client.container_name} \n"
        f"Info - to {target_path}"
    )
    return None


def upload_bytes_to_blob(
    container_client,
    bytes_local,
    file_remote,
    base_path_out="",
    time_in_dirname=False,
    time_in_filename=False,
):
    """Function to upload bytes to azure blob storage

    We didn't add error handeling in this function simply to leverage the add safe
    return decorator and have that catch any error. So let this function crash hard and
    soon.

    :param blob_client: blob client object
    :param container: str container name
    :param bytes_local: str
    :param base_path_out: str
    :param file_remote: str
    :param time_in_dirname: bool
    :param time_in_filename: bool
    :return: None
    """
    assert base_path_out[0] != "/", "No leading /"
    assert base_path_out[-1] != "/", "No trailing /"

    if time_in_dirname:
        base_path_out += "_" + datetime.now().strftime("%Y_%b_%d")

    if time_in_filename:
        file_remote = datetime.now().strftime("%d_%m_%Y_%H_%M") + "_" + file_remote

    path_out = os.path.join(base_path_out, file_remote)

    print(f"Info - Uploading bytes to remote path: {path_out}")

    # Write report to time stamped folder
    container_client.upload_blob(name=path_out, data=bytes_local, overwrite=True)

    print("Info - Finished upload")
    return None


def upload_file(file_local, *args, **kwargs):
    """Function to upload files to azure blob storage

    :param blob_client: blob client object
    :param container: str container name
    :param file_local: str
    :param base_path_out: str
    :param file_remote: str
    :param time_in_dirname: bool
    :param time_in_filename: bool
    :return: None
    """
    try:
        assert os.path.isfile(file_local)
        file = open(file_local, mode="rb")
        _bytes = file.read()
        file.close()
        return upload_bytes(bytes_local=_bytes, *args, **kwargs)
    except Exception as ex:
        print(f"Error - uploading file {file_local}. Complete stack: {ex}")
        return None
