Get a list of exchange rates for a given currency on a given date. Data is download from
the European Central Bank history zipfile.

Usage:

```python
>>> from exchange_rates import get_exchange_rates
>>> print( get_exchange_rates('USD', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01') )
{'EUR': 0.9496676163342831, 'CAD': 1.3613485280151947, 'USD': 1.0}
>>> print( get_exchange_rates('EUR', target_currencies=['EUR', 'CAD', 'USD'], on_date='2023-10-01') )
{'EUR': 1.0, 'CAD': 1.4335, 'USD': 1.053}
```

Idea is based on @Andrewnolan13 comment: https://github.com/MicroPyramid/forex-python/issues/149#issuecomment-1787050118
