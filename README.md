# arb_check.py

Simple python script, based on ccxt, for checking current arbitrage opportunity

## Getting Started

Enjoy

### Prerequisites
Python 3.7+
```
pip install -r requirements.txt
```

### Use

```
python arb_check.py --help
usage: arb_check.py [-h] [--base BASE] [--quote QUOTE] [--skip SKIP] [--ex EX]
                    [--nrl]

optional arguments:
  -h, --help     show this help message and exit
  --base BASE    base token f.e. LTC
  --quote QUOTE  quote token f.e. BTC
  --skip SKIP    comma separated exchange list to skip
  --ex EX        comma separated exchange list to use
  --nrl          disable rate limit
```
Example:
```bash
python arb_check.py --base=XRP --quote=BTC --ex=bitbay,bitfinex,binance
```