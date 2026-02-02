#!/usr/bin/env python3
"""리스크 관리 - 포지션 사이징, 손익비 계산"""
import math

def calculate_position_size(capital, risk_pct, entry, stop_loss):
    """포지션 크기 계산 (켈리 기준 간소화)
    
    Args:
        capital: 총 자본
        risk_pct: 1회 거래 리스크 % (권장: 1-2%)
        entry: 진입가
        stop_loss: 손절가
    
    Returns:
        포지션 크기 및 관련 정보
    """
    risk_amount = capital * (risk_pct / 100)
    price_risk = abs(entry - stop_loss)
    price_risk_pct = (price_risk / entry) * 100
    
    position_size = risk_amount / price_risk
    position_value = position_size * entry
    
    return {
        'capital': capital,
        'risk_pct': risk_pct,
        'risk_amount': round(risk_amount, 2),
        'entry': entry,
        'stop_loss': stop_loss,
        'price_risk_pct': round(price_risk_pct, 2),
        'position_size': round(position_size, 6),
        'position_value': round(position_value, 2),
        'leverage_if_full': round(position_value / capital, 2)
    }

def calculate_rr_ratio(entry, stop_loss, take_profit):
    """손익비 계산
    
    Returns:
        손익비 (Risk-Reward Ratio)
        1:2 미만이면 진입 금지
    """
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    
    if risk == 0:
        return {'error': 'risk is zero'}
    
    rr = reward / risk
    
    return {
        'entry': entry,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk': round(risk, 2),
        'reward': round(reward, 2),
        'rr_ratio': round(rr, 2),
        'verdict': '✅ 진입 가능' if rr >= 2 else '❌ 진입 금지 (RR < 2)'
    }

def kelly_criterion(win_rate, avg_win, avg_loss):
    """켈리 기준 최적 베팅 비율
    
    Args:
        win_rate: 승률 (0-1)
        avg_win: 평균 수익
        avg_loss: 평균 손실 (양수로 입력)
    """
    if avg_loss == 0:
        return {'error': 'avg_loss is zero'}
    
    b = avg_win / avg_loss  # 승/패 비율
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    
    # 풀 켈리는 위험하므로 반켈리 권장
    return {
        'win_rate': win_rate,
        'win_loss_ratio': round(b, 2),
        'full_kelly': round(kelly * 100, 2),
        'half_kelly': round(kelly * 50, 2),
        'quarter_kelly': round(kelly * 25, 2),
        'recommendation': f"자본의 {round(kelly * 25, 1)}% 권장 (1/4 켈리)"
    }

def calculate_sharpe(returns, risk_free_rate=0.04):
    """샤프 비율 계산
    
    Args:
        returns: 수익률 리스트 (예: [0.02, -0.01, 0.03, ...])
        risk_free_rate: 무위험 수익률 (연간)
    """
    if len(returns) < 2:
        return {'error': 'need at least 2 returns'}
    
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    
    if std == 0:
        return {'error': 'std is zero'}
    
    # 일간 데이터 가정, 연간화
    annual_return = mean_return * 252
    annual_std = std * math.sqrt(252)
    
    sharpe = (annual_return - risk_free_rate) / annual_std
    
    return {
        'mean_daily_return': round(mean_return * 100, 4),
        'daily_std': round(std * 100, 4),
        'annual_return': round(annual_return * 100, 2),
        'annual_std': round(annual_std * 100, 2),
        'sharpe_ratio': round(sharpe, 2),
        'grade': '🏆 우수' if sharpe > 2 else '✅ 양호' if sharpe > 1 else '⚠️ 보통' if sharpe > 0 else '❌ 부진'
    }

if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  risk.py size CAPITAL RISK_PCT ENTRY STOP")
        print("  risk.py rr ENTRY STOP TP")
        print("  risk.py kelly WIN_RATE AVG_WIN AVG_LOSS")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'size':
        result = calculate_position_size(
            float(sys.argv[2]), float(sys.argv[3]),
            float(sys.argv[4]), float(sys.argv[5])
        )
        print(json.dumps(result, indent=2))
    elif cmd == 'rr':
        result = calculate_rr_ratio(
            float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
        )
        print(json.dumps(result, indent=2))
    elif cmd == 'kelly':
        result = kelly_criterion(
            float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
        )
        print(json.dumps(result, indent=2))
