import json
import requests
import re
import multiprocessing
import itertools

BASE_URL = "https://uts-ws.nlm.nih.gov/rest/content/current/"


def load_api_key():
    with open("UMLS_API_KEY") as f:
        return f.read().strip(" \n")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class UMLS():
    def __init__(self):
        self.api_key = load_api_key()

        self.TGT = self.get_TGT(self.api_key)
        #print("<" + self.api_key + ">")

    @staticmethod
    def get_TGT(api_key):
        URL = "https://utslogin.nlm.nih.gov/cas/v1/api-key"

        content = {
            "apikey": api_key
        }

        header = {
            "content-type": "application/x-www-form-urlencoded"
        }

        req = requests.post(URL, data=content, headers=header)
        if req.status_code == 201:
            return re.findall(r'v1/api-key/([^"]+)"', req.text)[0]
        else:
            return None

    def get_ticket(self):
        URL = f"https://utslogin.nlm.nih.gov/cas/v1/tickets/{self.TGT}"

        content = {
            "service": "http://umlsks.nlm.nih.gov"
        }
        req = requests.post(URL, data=content)
        return req.text

    def get_relationships(self, CUI):
        URL = BASE_URL + f"CUI/{CUI}/relations"

        ticket = self.get_ticket()

        parameters = {
            "ticket": ticket,
            "pageSize": 25,
        }

        return requests.get(URL, parameters).json()

    def get_information(self, CUI):
        URL = BASE_URL + f"CUI/{CUI}"

        ticket = self.get_ticket()

        parameters = {
            "ticket": ticket,
            "pageSize": 25,
            "supressible": False
        }

        return requests.get(URL, parameters).json()

    def get_atoms(self, CUI):
        URL = BASE_URL + f"/CUI/{CUI}/atoms"

        ticket = self.get_ticket()

        parameters = {
            "ticket": ticket,
            "language": "EN",
            "pageSize": 25
        }

        requests.get(URL, parameters)

    def fetch_batch_information(self, cuis):
        name_map = {}

        size = 8
        pool = multiprocessing.pool.Pool(size)
        cui_chunks = chunks(list(cuis), size)

        for c, chunk in enumerate(cui_chunks):
            if not c % 100:
                print(f">{c}")
            result = pool.map(self.fetch_information, chunk)
            for r in result:
                if r is not None:
                    print(f"Fetching {' - '.join(r)}")
                    name_map[r[0]] = r[1:]

        return name_map

    def fetch_information(self, cui):
        try:
            result = self.get_information(cui)["result"]

        except KeyError:
            return None
        res = (
            cui,
            result["classType"],
            result["name"],
            result["semanticTypes"][0]["name"]
        )
        return res

    def fetch_relationships(self, cui):
        pass


if __name__ == "__main__":

    U = UMLS()
    RES = U.get_information("C0009044")
    print(json.dumps(RES, indent=2))
