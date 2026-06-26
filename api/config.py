from sentinelhub import SHConfig

config = SHConfig()

config.sh_client_id = "sh-5ba22570-31e3-4d9e-8840-4796b8bb43a2"
config.sh_client_secret = "FOGDX7B5bJQhmSwsFn6K0uY7tU1BtTC3".strip()

config.sh_base_url = "https://sh.dataspace.copernicus.eu"

config.sh_token_url = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

config.instance_id = ""

print("BASE:", config.sh_base_url)
print("TOKEN:", config.sh_token_url)
