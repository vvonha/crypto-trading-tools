#!/usr/bin/env python3
"""시장 모니터링 - 가격 알림, 변동성 감지"""
import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from binance.client import Client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Client(
    os.getenv('BINANCE_API_KEY'),
    os.getenv('BINANCE_SECRET_KEY')
)

def get_klines(symbol, interval='1h', limit=24):
    """캔들 데이터 조회"""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    return [{
        'open_time': k[0],
        'open': float(k[1]),
        'high': float(k[2]),
        'low': float(k[3]),
        'close': float(k[4]),
        'volume': float(k[5])
    } for k in klines]

def calculate_volatility(symbol, interval='1h', limit=24):
    """변동성 계산 (표준편차 기반)"""
    klines = get_klines(symbol, interval, limit)
    closes = [k['close'] for k in klines]
    
    mean = sum(closes) / len(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    std = variance ** 0.5
    volatility_pct = (std / mean) * 100
    
    return {
        'symbol': symbol,
        'period': f'{limit} {interval}',
        'mean': mean,
        'std': std,
        'volatility_pct': round(volatility_pct, 2),
        'high': max(closes),
        'low': min(closes),
        'range_pct': round((max(closes) - min(closes)) / mean * 100, 2)
    }

def get_funding_rate(symbol='BTCUSDT'):
    """선물 펀딩비 조회"""
    try:
        info = client.futures_funding_rate(symbol=symbol, limit=1)
        if info:
            return {
                'symbol': symbol,
                'funding_rate': float(info[0]['fundingRate']),
                'funding_time': info[0]['fundingTime']
            }
    except Exception as e:
        return {'error': str(e)}

def scan_top_movers(limit=10):
    """24시간 등락률 상위 종목"""
    tickers = client.get_ticker()
    usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
    
    sorted_up = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:limit]
    sorted_down = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']))[:limit]
    
    return {
        'top_gainers': [{
            'symbol': t['symbol'],
            'change_pct': float(t['priceChangePercent']),
            'volume': float(t['quoteVolume'])
        } for t in sorted_up],
        'top_losers': [{
            'symbol': t['symbol'],
            'change_pct': float(t['priceChangePercent']),
            'volume': float(t['quoteVolume'])
        } for t in sorted_down]
    }

def get_market_summary():
    """시장 요약"""
    btc = calculate_volatility('BTCUSDT')
    eth = calculate_volatility('ETHUSDT')
    funding = get_funding_rate('BTCUSDT')
    movers = scan_top_movers(5)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'btc': btc,
        'eth': eth,
        'btc_funding': funding,
        'top_movers': movers
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: monitor.py [vol SYMBOL | funding SYMBOL | movers | summary]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'vol':
        symbol = sys.argv[2] if len(sys.argv) > 2 else 'BTCUSDT'
        print(json.dumps(calculate_volatility(symbol), indent=2))
    elif cmd == 'funding':
        symbol = sys.argv[2] if len(sys.argv) > 2 else 'BTCUSDT'
        print(json.dumps(get_funding_rate(symbol), indent=2))
    elif cmd == 'movers':
        print(json.dumps(scan_top_movers(), indent=2))
    elif cmd == 'summary':
        print(json.dumps(get_market_summary(), indent=2))
    else:
        print(f"알 수 없는 명령: {cmd}")
