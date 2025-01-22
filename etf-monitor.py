import os
import requests
import yfinance as yf


ETF_TICKER = os.getenv("ETF_TICKER")
DRAWDOWN = float(os.getenv("DRAWDOWN", 0.3))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_drawdown(last_price, max_price):
    """ Return a tuple containing the current drawdown and if its
        enought or not to call Telegram API """
    drawdown = (max_price - last_price) / max_price
    return (
        f"{drawdown:.2f}",
        True if drawdown >= DRAWDOWN else False
    )

def telegram_request(drawdown, price):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    msg = f"Drawdown del {float(drawdown)*100}% en {ETF_TICKER} -> Precio {price}. ¡¡Compra clara!!"
    headers = {'Content-Type': 'application/json'}
    params = {
        'chat_id': CHAT_ID,
        'text': msg
    }

    response = requests.post(url, headers=headers, params=params)

    if response:
        return response.status_code

def lambda_handler(event, context):
    try:
        ticker = yf.Ticker(ETF_TICKER)
        data_52_weeks = ticker.history(period="1y")
        last_day_price = data_52_weeks['Close'].iloc[-1]
        max_price_52_weeks = data_52_weeks['High'].max()

    except Exception as e:
        return {
            'status_code': 100,
            'body': f"Error: {str(e)}"
        }
    
    body = {
        'last_day_price': f"{last_day_price:.2f}",
        'max_price_52_weeks': f"{max_price_52_weeks:.2f}",
        'telegram_request': False
    }

    body['drawdown'], bigger_than_30 = get_drawdown(last_day_price, max_price_52_weeks)

    if bigger_than_30:
        
        if status_code := telegram_request(body['drawdown'], body['last_day_price']):
            body['telegram_request'] = True
            body['telegram_response'] = status_code
        
        else:
            return {
                'status_code': 101,
                'body': "Error: No response from Telegram API"
            }

    return {
        'status_code': 000,
        'body': body
    }

print(lambda_handler(None, None))