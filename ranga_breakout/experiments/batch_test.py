from api import Helper
from main import get_params


def exch_token(params):
    try:
        # create list of tokens
        lst = [v for v in params.values()]
        exch = lst[0]["exchange"]
        lst = [dct["token"] for dct in lst]
        return exch, lst
    except Exception as e:
        print(e)


def get_ltp(params):
    try:
        new_dct = {}
        exch, tokens = exch_token(params)

        # Batch the tokens into chunks of 50
        batch_size = 50
        for i in range(0, len(tokens), batch_size):
            token_batch = tokens[i : i + batch_size]
            exch_token_dict = {exch: token_batch}

            # Fetch LTP for the current batch
            resp = Helper.api.obj.getMarketData("LTP", exch_token_dict)
            lst_of_dict = resp["data"]["fetched"]
            print(lst_of_dict)

            # Update the dictionary with the current batch's LTPs
            new_dct.update({dct["symbolToken"]: dct["ltp"] for dct in lst_of_dict})
    except Exception as e:
        print(f"Error while getting LTP: {e}")
    finally:
        return new_dct


def main():
    try:
        Helper.api
        params = get_params()
        print(params)
        resp = get_ltp(params)
        print(resp)
    except Exception as e:
        print(e)


main()
