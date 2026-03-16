"""
OpenClaw Psychology-First Trading Assistant
For Binance x OpenClaw Campaign 2026
Works with any trading pair
"""

import json
import time
from datetime import datetime

class TradingAssistant:
    """
    Trading assistant with psychological guards
    Uses 9-period Weighted Moving Average
    """
    
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.state = self.load_state()
    
    def load_state(self):
        """Load or initialize trading state"""
        try:
            with open(f"state_{self.symbol}.json", 'r') as f:
                return json.load(f)
        except:
            return {
                'entry_price': None,
                'entry_time': None,
                'profit_locked': False,
                'position_size': None,
                'trade_active': False,
                'trades': []
            }
    
    def save_state(self):
        """Save current state"""
        with open(f"state_{self.symbol}.json", 'w') as f:
            json.dump(self.state, f)
    
    def calculate_wma(self, prices, period=9):
        """Weighted Moving Average calculation"""
        if len(prices) < period:
            return None
        prices = prices[-period:]
        weights = list(range(1, period + 1))
        return sum(p * w for p, w in zip(prices, weights)) / sum(weights)
    
    def get_current_price(self):
        """
        Get current price from Binance
        In OpenClaw, this comes from the platform
        """
        # This is a placeholder - OpenClaw provides real price
        return 50000.0
    
    def get_price_history(self):
        """
        Get price history from Binance
        In OpenClaw, this comes from the platform
        """
        # This is a placeholder - OpenClaw provides real data
        return [49800, 49900, 50000, 50100, 50200] * 10
    
    def analyze_trend(self):
        """Analyze market trend using WMA"""
        current_price = self.get_current_price()
        closes = self.get_price_history()
        wma_9 = self.calculate_wma(closes, 9)
        
        if wma_9 is None:
            return None
        
        signals = []
        if current_price > wma_9:
            signals.append("UPTREND")
        else:
            signals.append("DOWNTREND")
        
        return {
            'current_price': current_price,
            'wma_9': wma_9,
            'signals': signals,
            'strength': 'STRONG' if abs(current_price - wma_9) / wma_9 > 0.02 else 'WEAK'
        }
    
    def should_enter(self, analysis):
        """Check if conditions are right to enter"""
        if self.state['trade_active']:
            return False
        
        if not analysis:
            return False
        
        # Simple entry condition: price above 9WMA (uptrend)
        if "UPTREND" in analysis['signals']:
            return True
        
        return False
    
    def should_exit(self, analysis):
        """Check if we should exit position"""
        if not self.state['trade_active'] or not analysis:
            return None
        
        current = analysis['current_price']
        entry = self.state['entry_price']
        
        if entry is None or entry == 0:
            return None
        
        pnl_percent = ((current - entry) / entry) * 100
        
        # Phase 1: Take partial profit at 5%
        if not self.state['profit_locked'] and pnl_percent >= 5:
            return "PARTIAL_PROFIT"
        
        # Phase 2: After profit locked, exit on trend reversal
        if self.state['profit_locked']:
            if "DOWNTREND" in analysis['signals']:
                return "TREND_EXIT"
        
        # Stop loss at -3%
        if pnl_percent <= -3:
            return "STOP_LOSS"
        
        return None
    
    def execute_entry(self, analysis):
        """Execute entry order"""
        price = analysis['current_price']
        
        self.state['trade_active'] = True
        self.state['entry_price'] = price
        self.state['entry_time'] = datetime.now().isoformat()
        self.state['profit_locked'] = False
        self.state['position_size'] = 1.0  # Placeholder
        
        self.save_state()
        
        return f"✅ ENTRY: Bought {self.symbol} at ${price:.2f}"
    
    def execute_partial_profit(self, analysis):
        """Sell 50% of position"""
        price = analysis['current_price']
        entry = self.state['entry_price']
        pnl = ((price - entry) / entry) * 100
        
        self.state['profit_locked'] = True
        self.state['position_size'] = self.state['position_size'] * 0.5
        self.save_state()
        
        return f"🎯 PARTIAL PROFIT: Sold 50% at ${price:.2f} (+{pnl:.2f}%) | Entering Psychology Guard"
    
    def execute_exit(self, analysis, reason):
        """Sell remaining position"""
        price = analysis['current_price']
        entry = self.state['entry_price']
        pnl = ((price - entry) / entry) * 100
        
        # Log the trade
        trade_record = {
            'symbol': self.symbol,
            'entry_price': entry,
            'exit_price': price,
            'entry_time': self.state['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'pnl_percent': pnl,
            'exit_reason': reason
        }
        
        self.state['trades'].append(trade_record)
        
        # Reset state
        self.state['trade_active'] = False
        self.state['entry_price'] = None
        self.state['profit_locked'] = False
        self.state['position_size'] = None
        
        self.save_state()
        
        return f"🔚 EXIT ({reason}): Sold at ${price:.2f} | Final P&L: {pnl:+.2f}%"
    
    def run_cycle(self):
        """Main trading cycle"""
        try:
            analysis = self.analyze_trend()
            if not analysis:
                return "⚠️ Unable to analyze market data"
            
            current = analysis['current_price']
            wma = analysis['wma_9']
            
            # No active trade - look for entry
            if not self.state['trade_active']:
                if self.should_enter(analysis):
                    return self.execute_entry(analysis)
                else:
                    signal = analysis['signals'][0] if analysis['signals'] else 'NEUTRAL'
                    return f"👁️ MONITORING {self.symbol}: ${current:.2f} | 9WMA: ${wma:.2f} | Signal: {signal}"
            
            # Active trade - check for exit
            exit_signal = self.should_exit(analysis)
            
            if exit_signal == "PARTIAL_PROFIT":
                return self.execute_partial_profit(analysis)
            elif exit_signal:
                return self.execute_exit(analysis, exit_signal)
            
            # No exit signal - show position status
            entry = self.state['entry_price']
            pnl = ((current - entry) / entry) * 100
            
            if self.state['profit_locked']:
                return f"🛡️ PSYCHOLOGY GUARD: P&L {pnl:+.2f}% | Price hidden | 9WMA: ${wma:.2f} | Trend: {analysis['signals'][0]}"
            else:
                return f"📊 POSITION ACTIVE: ${current:.2f} | Entry: ${entry:.2f} | P&L: {pnl:+.2f}% | Target: 5%"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"


# Dictionary to store instances for different symbols
_instances = {}

def on_tick(symbol="BTCUSDT"):
    """
    Main entry point called by OpenClaw
    Works with any Binance trading pair
    """
    global _instances
    
    if symbol not in _instances:
        _instances[symbol] = TradingAssistant(symbol)
    
    return _instances[symbol].run_cycle()


# For multi-symbol monitoring
def on_cron():
    """Optional: monitor multiple symbols on schedule"""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
    results = []
    
    for symbol in symbols:
        try:
            if symbol not in _instances:
                _instances[symbol] = TradingAssistant(symbol)
            results.append(f"{symbol}: {_instances[symbol].run_cycle()}")
        except Exception as e:
            results.append(f"{symbol}: Error")
    
    return "\n".join(results)


# Allow running as standalone script for testing
if __name__ == "__main__":
    # Simple test
    assistant = TradingAssistant("BTCUSDT")
    print("=" * 50)
    print("Binance OpenClaw Assistant - Test Mode")
    print("=" * 50)
    print(assistant.run_cycle())
    print("\nAssistant initialized and ready.")
