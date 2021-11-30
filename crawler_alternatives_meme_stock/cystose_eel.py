from microprediction import MicroWriter
from microprediction.bespoke.meme_stock import decode_meme_stock
from collections import Counter
from pprint import pprint
import numpy as np
import time

# Example script that submits predictions of the next hour's meme stock
# To use this, first create your WRITE_KEY as explained at https://www.microprediction.com/python-1
# Then schedule it to run once an hour.

NAME = 'meme-stock-of-the-hour.json'


def values_from_lagged(lagged_values:[float], num_predictions=225)->[float]:
    """
        Produce 225 guesses of the next number based on lagged values
    """
    values = list()

    # Use empirical transition but start with least common
    s_current = lagged_values[0]
    transition = Counter([s for s,s_prev in zip(lagged_values,lagged_values[1:]) if (s_prev==s_current) or (np.random.rand()<0.1)]).most_common()
    for val,cnt in reversed(transition):
        for _ in range(cnt):
            values.append(val+0.000000001*np.random.randn())

    # Pad with most common meme stocks as needed
    if len(values)<num_predictions:
        common = Counter(lagged_values).most_common()
        for val,cnt in common:
            for _ in range(cnt):
                values.append(val+0.000000001*np.random.randn())

    return sorted(values[:num_predictions])


def submit_predictions():
    """
        Example of creating and submitting predictions for the next meme stock
    """
    mw = MicroWriter(write_key=WRITE_KEY)
    mw.set_repository('https://github.com/microprediction/microprediction/blob/master/crawler_alternatives/cystose_eel.py')
    lagged_values = mw.get_lagged_values(name=NAME)
    values = values_from_lagged(lagged_values=lagged_values, num_predictions=mw.num_predictions)
    for delay in mw.DELAYS:
        res = mw.submit(name=NAME,values=values,delay=delay)
        pprint(res)
        time.sleep(0.5)

    # Barf the interpretation of what we submitted
    tickers = Counter([ decode_meme_stock(int(v)) for v in values ]).most_common()
    pprint(tickers)


if __name__=='__main__':
    WRITE_KEY = "put your write key here"
    if WRITE_KEY=="put your write key here":
        WRITE_KEY=None
    mw = MicroWriter(write_key=WRITE_KEY)

    # Assumes this script will be run hourly
    for _ in range(7):
        submit_predictions()
        time.sleep(60*8)
