import time
from multiprocessing.pool import Pool

import requests
from requests import Response


def get_corpus_list(corpus_list_url: str):
    response: Response = requests.get(corpus_list_url)
    return response.text


corpus_list_url: str = "https://korpling.org/mc-service/mc/api/v1.0/corpora?last_update_time=0"
raw_text_url: str = "https://korpling.org/mc-service/mc/api/v1.0/rawtext?urn=urn:custom:latinLit:proiel.caes-gal.lat:1.1.1-2.1.1"
pool: Pool = Pool(20)
user_count: int = 20
start_time: float = time.time()
corpus_list = pool.map(get_corpus_list, [raw_text_url] * user_count)
print("Duration: {0}s".format(time.time() - start_time))
