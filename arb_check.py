import time
from argparse import ArgumentParser
from threading import Thread, Lock

import ccxt

# checked_currencies = {'BTC', 'LTC', 'NEO', 'ETH',ą 'ETC', 'CLO', 'XVG', 'NMC', 'PPC', 'LSK', 'XRB', 'WAVES', 'EOS',
#                       'ADA', 'XLM', 'IOTA', 'XMR', 'NEM', 'DASH', 'TRX', 'BTM'}

fiat_token = {'PLN', 'USD', 'RUB', 'EUR', 'BRL', 'CNY', 'USDT', 'EURT', 'JPY'}
skiped_token = fiat_token
# checked_Atoken = {'BTC'}
# fucked_up = {'braziliex', 'bxinth', 'ice3x', 'yunbi', 'okcoinusd', 'huobicny', 'coolcoin', 'bitfinex', 'allcoin',
#              'cointiger', 'coingi', 'lbank'}
fucked_up = {'wex'}

exchanges = {}
all_markets = {}
global_lock = Lock()
min_market_instances = 10
args = None
ei_threads = []


class ExchangeInitThread(Thread):
    def __init__(self, cls):
        Thread.__init__(self)
        self._cls = cls
        self.exchange = None
        self.exchange_supported = False
        self.markets = None
        self.end_init = None

    def run(self):
        t0 = time.time()
        self.exchange = self._cls({'enableRateLimit': False if args.nrl else True})
        self.exchange.timeout = 20000
        self.exchange_supported = self.exchange.has['publicAPI'] and self.exchange.has['privateAPI'] and \
                                  self.exchange.has['fetchOrderBook'] and self.exchange.has['cancelOrder'] and \
                                  self.exchange.has['createLimitOrder']
        if self.exchange_supported:
            try:
                self.markets = self.exchange.load_markets()
            except Exception as exception:
                # print('{} error'.format(self.exchange.id))
                pass
        self.end_init = time.time() - t0


def init_exchanges():
    global ei_threads
    ei_threads = []
    skipped_exchanges = []
    only_exchanges = []
    if args.skip:
        skipped_exchanges = args.skip.split(',')
    if args.ex:
        only_exchanges = args.ex.split(',')
    for es in ccxt.exchanges:
        if es not in fucked_up and es not in skipped_exchanges and (len(only_exchanges) == 0 or es in only_exchanges):
            exchange_class = getattr(ccxt, es)
            ei_threads.append(ExchangeInitThread(exchange_class))
    print('ei start')
    t0 = time.time()
    for thread in ei_threads:
        thread.start()

    while any(thread.isAlive() for thread in ei_threads):
        time.sleep(0.1)

    t1 = time.time() - t0
    print('ei time:{:.3f}s'.format(t1))


markets = set()


def narrow_markets():
    global markets
    for thread in ei_threads:
        if thread.exchange.markets:
            for symbol, market in thread.exchange.markets.items():
                if '/' in symbol and \
                        market['base'] and market['quote'] and \
                        ((args.base or market['base']) == market['base']) and \
                        ((args.quote or market['quote']) == market['quote']):
                    markets |= {symbol}


class ExchangeOrderBookThread(Thread):
    def __init__(self, exchange, market):
        Thread.__init__(self)
        self.exchange = exchange
        self.market = market
        self.order_book = None

    def run(self):
        try:
            self.order_book = self.exchange.fetchOrderBook(symbol=self.market, limit=50)
        except:
            pass


def check(market: str):
    eob_threads = []
    for thread in ei_threads:
        if thread.exchange_supported and thread.exchange.markets and market in thread.exchange.markets:
            eob_threads.append(ExchangeOrderBookThread(thread.exchange, market))

    if len(eob_threads) == 0:
        print('no {} exchanges'.format(market))
        return

    print('market {} start quering {} exchanges:{}'.format(market, len(eob_threads), ''.join(s.exchange.id + ',' for s in eob_threads)))
    t0 = time.time()
    for thread in eob_threads:
        thread.start()

    while any(thread.isAlive() for thread in eob_threads):
        time.sleep(0.1)

    t1 = time.time() - t0
    print('eob time:{:.3f}s'.format(time.time() - t0))

    min_ask = None
    max_bid = None
    max_bid_ex = None
    min_ask_ex = None
    for thread in eob_threads:
        if thread.order_book:
            asks = thread.order_book['asks']
            ask = (asks or [None])[0]
            ask = (ask or [None])[0]
            bids = thread.order_book['bids']
            bid = (bids or [None])[0]
            bid = (bid or [None])[0]
            if min_ask:
                if ask and ask < min_ask:
                    min_ask = ask
                    min_ask_ex = thread.exchange
            else:
                min_ask = ask
                min_ask_ex = thread.exchange

            if max_bid:
                if bid and bid > max_bid:
                    max_bid = bid
                    max_bid_ex = thread.exchange
            else:
                max_bid = bid
                max_bid_ex = thread.exchange

    if max_bid and min_ask and max_bid > min_ask:
        print(
            'best {} bid:{}@{:012.8f} ask:{}@{:012.8f} {:012.8f}'.format(market, max_bid_ex.id, max_bid, min_ask_ex.id,
                                                                         min_ask,
                                                                         max_bid - min_ask))
    else:
        print('without opportunity')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--base')
    parser.add_argument('--quote')
    parser.add_argument('--skip')
    parser.add_argument('--ex')
    parser.add_argument('--nrl', dest='nrl', action='store_true', help="disable rate limit")
    args = parser.parse_args()
    init_exchanges()
    narrow_markets()
    for market in markets:
        check(market)
        print('')