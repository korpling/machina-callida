import requests
import rapidjson as json
from mcserver import Config
from mcserver.app.services import NetworkService


def get(urn: str):
    """ Returns results for a frequency query from ANNIS for a given CTS URN and AQL. """
    url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}" + \
               Config.SERVER_URI_FREQUENCY
    response: requests.Response = requests.get(url, params=dict(urn=urn))
    return NetworkService.make_json_response(json.loads(response.text))
