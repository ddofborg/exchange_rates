'''

Get a list of exchange rates for a given currency on a given date. Data is download from
the European Central Bank history zipfile.

>>> get_exchange_rates('USD', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01')
{'EUR': 0.9496676163342831, 'CAD': 1.3613485280151947, 'USD': 1.0}
>>> get_exchange_rates('EUR', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01')
{'EUR': 1.0, 'CAD': 1.4335, 'USD': 1.053}

Note, rates are not cached. Each request will download the data again. 

'''


from datetime import datetime
import logging

import requests
import zipfile
import io
import csv
import sys

LOG = logging.getLogger(__name__)

SOURCE_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip'

def get_exchange_rates(base_currency: str,
                       target_currencies: list | tuple | set = None,
                       *,
                       on_date: str = None, within_days=3,
                       continue_on_error=True):
    '''
        Returns the rates for `target_currencies` relative to the `base_currency`
        for `on_date`.

        If `on_date` is `None`, then the current date is used.

        If there is no exact date match with the data, then the closest match to
        `on_date` within `within_days` is returned.

        `target_currencies` can be a list of currency symbols to return. If empty,
        all symbols are returned.

        Returns: `{ CUR1: rate1, CUR2: rate2, ... }`.
    '''

    assert isinstance(target_currencies, (list, tuple, set, type(None)))

    # Default to current date
    if on_date is None:
        on_date = datetime.now().strftime('%Y-%m-%d')

    on_date_date = datetime.strptime(on_date, '%Y-%m-%d').date()

    # Downlaod ZIP with CSV data from Erupean Central Bank
    response = requests.get(SOURCE_URL)

    # Read exchange rates CSV data from the ZIP
    z = zipfile.ZipFile(io.BytesIO(response.content))
    csv_filename = z.namelist()[0]
    csv_data = z.read(csv_filename)

    # Parse the CSV data
    csv_reader = csv.DictReader(csv_data.decode('utf-8').splitlines(), delimiter=',')

    # Find the closest date to `on_date`
    best_row = {'Within_Days': sys.maxsize}
    for row in csv_reader:
        # Convert date to datetime object
        row['Date_Str'] = row['Date']
        row['Date'] = datetime.strptime(row['Date'], '%Y-%m-%d').date()
        row['Within_Days'] = abs((row['Date'] - on_date_date).days)

        # Exact date match
        if row['Date'] == on_date_date:
            best_row = row
            break

        # Keep closest date
        if row['Within_Days'] < best_row['Within_Days']:
            best_row = row

    # Return all currencies if target_currencies is None
    if target_currencies is None:
        target_currencies = set(best_row.keys()) - set(['Date', 'Date_Str', 'Within_Days'])

    # Return exchange rates if within_days is less than the best match
    if best_row['Within_Days'] < within_days:
        ret = {}
        best_row['EUR'] = 1.0
        for cur in target_currencies:
            try:
                ret[cur] = float(best_row[cur]) / float(best_row[base_currency])
            except ValueError:
                LOG.debug(f'Could not convert `{cur}` with value `{best_row[cur]}` to float.')
                if not continue_on_error:
                    raise
            except KeyError:
                LOG.debug(f'Could not find exchange rate for `{cur}` on {on_date}.')
                if not continue_on_error:
                    raise

        return ret

    raise RuntimeError(f'No exchange rates found for {base_currency} on {on_date} within {within_days} days.')


if __name__ == '__main__':

    print(f'Testing exchange_rates.py:\n')
    rate = get_exchange_rates('USD', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01')
    print(f'- USD on 2023-10-01 => {rate}\n')
    rate = get_exchange_rates('EUR', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01')
    print(f'- EUR on 2023-10-01 => {rate}\n')
    rate = get_exchange_rates('USD')
    print(f'- USD on 2023-10-01 => {rate}\n')
    rate = get_exchange_rates('CAD', ['EUR', 'GBP'])
    print(f'- CAD on 2023-10-01 => {rate}\n')
    rate = get_exchange_rates('EUR', target_currencies=['XXX'], continue_on_error=False)
    print(f'- EUR on 2023-10-01 => {rate}\n')
