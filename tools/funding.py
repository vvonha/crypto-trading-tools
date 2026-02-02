#!/usr/bin/env python3
"""펀딩비 차익거래 모니터"""
import os
import sys
import json
from dotenv import load_dotenv
from binance.client import Client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Client(
    os.getenv('BINANCE_API_KEY'),
    os.getenv('BINANCE_SECRET_KEY')
)

def scan_funding_opportunities(min_rate=0.0005, top_n=10):
    """펀딩비 차익 기회 스캔
    
    Args:
        min_rate: 최소 펀딩비 (0.0005 = 0.05%)
        top_n: 상위 N개 반환
    """
    try:
        # 모든 선물 펀딩비 조회
        funding_info = client.futures_funding_rate()
        
        # 심볼별 최신 펀딩비만 추출
        latest = {}
        for f in funding_info:
            symbol = f['symbol']
            if symbol not in latest or f['fundingTime'] > latest[symbol]['fundingTime']:
                latest[symbol] = f
        
        # 필터링 및 정렬
        opportunities = []
        for symbol, info in latest.items():
            rate = float(info['fundingRate'])
            if abs(rate) >= min_rate:
                apr = rate * 3 * 365 * 100  # 8시간 3회/일 * 365일
                opportunities.append({
                    'symbol': symbol,
                    'funding_rate': rate,
                    'funding_rate_pct': round(rate * 100, 4),
                    'estimated_apr': round(apr, 2),
                    'direction': 'SHORT 유리' if rate > 0 else 'LONG 유리'
                })
        
        # APR 기준 정렬
        opportunities.sort(key=lambda x: abs(x['estimated_apr']), reverse=True)
        
        return opportunities[:top_n]
    
    except Exception as e:
        return {'error': str(e)}

def calculate_funding_profit(position_size, funding_rate, days=30):
    """펀딩비 수익 계산"""
    daily_funding = funding_rate * 3  # 8시간마다 3회
    total_funding = daily_funding * days
    profit = position_size * total_funding
    
    return {
        'position_size': position_size,
        'funding_rate': funding_rate,
        'daily_funding_pct': round(daily_funding * 100, 4),
        'period_days': days,
        'total_funding_pct': round(total_funding * 100, 2),
        'estimated_profit': round(profit, 2)
    }

def get_funding_rate(symbol='BTCUSDT'):
    """특정 심볼 펀딩비 조회"""
    try:
        info = client.futures_funding_rate(symbol=symbol, limit=1)
        if info:
            return {
                'symbol': symbol,
                'funding_rate': float(info[0]['fundingRate']),
                'funding_time': info[0]['fundingTime']
            }
        return {'error': 'no data'}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법:")
        print("  funding.py scan [MIN_RATE]")
        print("  funding.py calc POSITION_SIZE FUNDING_RATE [DAYS]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'scan':
        min_rate = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0005
        result = scan_funding_opportunities(min_rate)
        print(json.dumps(result, indent=2))
    elif cmd == 'calc':
        pos = float(sys.argv[2])
        rate = float(sys.argv[3])
        days = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        result = calculate_funding_profit(pos, rate, days)
        print(json.dumps(result, indent=2))
