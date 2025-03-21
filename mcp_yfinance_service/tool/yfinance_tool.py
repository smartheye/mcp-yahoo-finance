import logging
import yfinance as yf
import requests
from mcp_yfinance_service.config import config, load_requests_proxies

proxies = load_requests_proxies()
session = requests.Session()
if proxies is not None:
    session.proxies = proxies
session.verify = False  # 关闭 SSL 验证

async def get_current_price(symbol:str) -> str:
    stock = yf.Ticker(symbol, session=session)
    try:
        data = stock.history(period="1d")
        if not data.empty:
            fval = data["Close"].iloc[-1]
            return str(fval)
        else:
            fval = stock.info.get("currentPrice", "N/A")
            return str(fval)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    # 测试
    symbols = ["AAPL", "0700.HK", "BTC-USD"]  # 苹果、腾讯、比特币
    for _symbol in symbols:
        price = get_current_price(_symbol)
        print(f"{_symbol}: {price}")