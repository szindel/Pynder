from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


def get_keyvault_secret(name_secret, name_kv):
    """Utility function to retrieve a secret from a keyvault

    :param secret_name: str
    :param kv_name: str
    :return:
    """
    print(f"Retrieving your secret from {name_kv}")
    assert isinstance(name_secret, str)
    assert isinstance(name_kv, str)

    try:
        cred = DefaultAzureCredential()
        KVUri = f"https://{name_kv}.vault.azure.net"
        client = SecretClient(vault_url=KVUri, credential=cred)
        retrieved_secret = client.get_secret(name_secret)
    except Exception as ex:
        raise Exception(
            f"\n\nFailed to fetch secret: {name_secret} to kv: {name_kv}. "
            f"Complete error stack: \n\n {ex}"
        )
    return retrieved_secret
