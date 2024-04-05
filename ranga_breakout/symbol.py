from __init__ import O_FUTL, S_DUMP, logging
from requests import get


class Symbol:

    def __init__(self):
        self._data = self.data

    @property
    def data(self):
        if O_FUTL.is_file_not_2day(S_DUMP):
            headers = {
                "Host": "angelbroking.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            resp = get(url, headers=headers)
            with open(S_DUMP, "w") as json_file:
                json_file.write(resp.text)
        return O_FUTL.read_file(S_DUMP)

    def get_tkn_fm_sym(self, sym, exch):
        for i in self.data:
            if (i['symbol'] == sym) and (i['exch_seg'] == exch):
                return i['token']
        logging.error(f"token not found for {sym=} {exch=}")
        return "0"
