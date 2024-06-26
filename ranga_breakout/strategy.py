from __init__ import O_FUTL, S_STOPS
from toolkit.kokoo import timer
from pprint import pprint


def is_values_in_list(lst_orders, args):
    dct = {}
    for i in lst_orders:
        if (
            i["tradingsymbol"] == args["tradingsymbol"]
            and i["transactiontype"] == args["transactiontype"]
            and i["status"] == "complete"
        ):
            return i
    return dct


class Strategy:
    def __init__(self, api):
        self.api = api
        self.lst = []
        if not O_FUTL.is_file_not_2day(S_STOPS):
            self.lst = O_FUTL.read_file(S_STOPS)
        self.is_set = True if any(self.lst) else False

    """
    dct = {
        "variety": "NORMAL",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": 432.05,
        "triggerprice": 432.1,
        "quantity": "1600",
        "disclosedquantity": "0",
        "squareoff": 0.0,
        "stoploss": 0.0,
        "trailingstoploss": 0.0,
        "tradingsymbol": "ITC27JUN24FUT",
        "transactiontype": "SELL",
        "exchange": "NFO",
        "symboltoken": "52178",
        "ordertag": "",
        "instrumenttype": "FUTSTK",
        "strikeprice": -1.0,
        "optiontype": "XX",
        "expirydate": "27JUN2024",
        "lotsize": "1600",
        "cancelsize": "0",
        "averageprice": 432.05,
        "filledshares": "1600",
        "unfilledshares": "0",
        "orderid": "240612000182183",
        "text": "",
        "status": "complete",
        "orderstatus": "complete",
        "updatetime": "12-Jun-2024 09:45:39",
        "exchtime": "12-Jun-2024 09:45:39",
        "exchorderupdatetime": "12-Jun-2024 09:45:39",
        "fillid": "",
        "filltime": "",
        "parentorderid": "",
        "uniqueorderid": "119729f9-1216-4007-b7da-196b630b64dc",
        "exchangeorderid": "2300000017065849",
    }
    """

    def run(self):
        if any(self.lst):
            dct = self.api.orders
            lst_orders = dct["data"]
            # work with the copy of stop orders
            for i in self.lst[:]:
                print(f'{i["side"]} stop order from file for {i["symbol"]}')
                args = {"tradingsymbol": i["symbol"]}
                # shift the side to check for matching entries
                args["transactiontype"] = "SELL" if i["side"] == "BUY" else "BUY"
                # filter the order book containing only this symbol
                lst_of_entries = [
                    j
                    for j in lst_orders
                    if j["tradingsymbol"] == args["tradingsymbol"]
                    and j["transactiontype"] == args["transactiontype"]
                ]
                # do we have any item in the list
                if len(lst_of_entries) > 0:
                    dct_found = is_values_in_list(lst_of_entries, args)
                    if dct_found.get("status", "NOT_COMPLETE") == "complete":
                        print(f"{dct_found=}")
                        resp = self.api.order_place(**i)
                        print(f"placing stop order: {resp=}")
                        self.lst.remove(i)
                # if not remove it from list
                else:
                    print(f'{i["side"]} stop order for {i["symbol"]} has no match')
                    self.lst.remove(i)
            timer(1)
            print(f"{len(self.lst)} stop orders found")
            pprint(self.lst)
        return


if __name__ == "__main__":
    from api import Helper

    Helper.set_token()

    Sgy = Strategy(Helper.api)
    if Sgy.is_set:
        Sgy.run()
