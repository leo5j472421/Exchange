from binance.websockets import BinanceSocketManager


def process_message(msg):
    print(msg)

bm = BinanceSocketManager('')
conn_key = bm.start_ticker_socket(process_message)

bm.start()

