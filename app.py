from flask import Flask, render_template, request, redirect, url_for, jsonify
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import os

app = Flask(__name__)

# Diretório para armazenar o arquivo CSV
DATA_DIR = 'data'
CSV_FILE = os.path.join(DATA_DIR, 'stocks_data.csv')

def fetch_stock_data():
    symbols = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'BBAS3.SA', 'B3SA3.SA', 'WEGE3.SA', 'RENT3.SA', 'MGLU3.SA']
    stocks = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1mo')
        
        # Calcular indicador técnico RSI usando pandas_ta
        data['RSI'] = ta.rsi(data['Close'], length=14)
        
        last_price = round(data['Close'].iloc[-1], 2)
        high = round(data['High'].iloc[-1], 2)
        low = round(data['Low'].iloc[-1], 2)
        change_real = round(data['Close'].iloc[-1] - data['Close'].iloc[-2], 2)
        change_percent = round((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100, 2)
        volume = int(data['Volume'].iloc[-1])
        date = data.index[-1].strftime('%Y-%m-%d')
        
        # Dados adicionais
        friendly_name = stock.info.get('shortName', 'N/A')
        market_cap = round(stock.info['marketCap'] / 1e9, 2)  # Valor de mercado em bilhões
        pe_ratio = round(stock.info['trailingPE'], 2) if 'trailingPE' in stock.info else None
        sector = stock.info.get('sector', 'N/A')
        industry = stock.info.get('industry', 'N/A')
        
        stocks.append({
            'symbol': symbol,
            'friendly_name': friendly_name,
            'last_price': last_price,
            'high': high,
            'low': low,
            'change_real': change_real,
            'change_percent': change_percent,
            'volume': volume,
            'date': date,
            'rsi': round(data['RSI'].iloc[-1], 2),
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'sector': sector,
            'industry': industry
        })
    
    df = pd.DataFrame(stocks)
    
    # Criar o diretório se não existir
    os.makedirs(DATA_DIR, exist_ok=True)
    
    df.to_csv(CSV_FILE, index=False)

@app.route('/')
def index():
    if not os.path.exists(CSV_FILE):
        fetch_stock_data()
    
    return render_template('index.html')

@app.route('/update')
def update():
    fetch_stock_data()
    return redirect(url_for('index'))

@app.route('/get_stock_data')
def get_stock_data():
    if not os.path.exists(CSV_FILE):
        fetch_stock_data()
    
    stocks = pd.read_csv(CSV_FILE).to_dict(orient='records')
    return jsonify(stocks=stocks)

if __name__ == '__main__':
    app.run(debug=True)