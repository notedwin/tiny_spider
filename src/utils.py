from dotenv import dotenv_values
from infisical_sdk import InfisicalSDKClient

c = dotenv_values(".env")
client = InfisicalSDKClient(host="http://192.168.0.200:8080")

client.auth.universal_auth.login(
    client_id=c["id"],
    client_secret=c["secret"],
)


def get_secret(name):
    return client.secrets.get_secret_by_name(
        secret_name=name,
        project_id="c80e4993-adcd-4360-a378-4e6476dd75e9",
        environment_slug="prod",
        secret_path="/",
    ).secret.secret_value
