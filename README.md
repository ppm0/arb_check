# arb_check - crypto arbitrage checker

Simple python script, based on ccxt, for checking current arbitrage opportunity

## Getting Started
#### Prerequisites
Python 3.8+, Pipenv

#### Install dependency && activate shell
```bash
pipenv install && pipenv shell
```

## Use
```bash
python arb_check.py --help
usage: arb_check.py [-h] [--base BASE] [--quote QUOTE] [--skip SKIP] [--ex EX] [--quiet]
                    [--nrl]

optional arguments:
  -h, --help     show this help message and exit
  --base BASE    base token f.e. LTC
  --quote QUOTE  quote token f.e. BTC
  --skip SKIP    comma separated exchange list to skip
  --ex EX        comma separated exchange list to use
  --nrl          disable rate limit (ccxt library has built in requests limiter to be kind and avoid banning)
  --quiet        less descriptive mode 
```

### Examples
query bitbay, bitfinex, binance about LTC/BTC:
```bash
python arb_check.py --base=LTC --quote=BTC --ex=bitbay,bitfinex,binance
```
query all about ETH/BTC:
```bash
python arb_check.py --base=ETH --quote=BTC
```
query all about all pair with NEO
```bash
python arb_check.py --base=NEO
```
query bitfinex,binance about all pairs
```bash
python arb_check.py --ex=bitfinex,binance
```