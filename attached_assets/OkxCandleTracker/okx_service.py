import requests
import json
import logging
from datetime import datetime, timezone
import time

class OKXService:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OKX-Market-Data-Client/1.0'
        })
        
    def _make_request(self, endpoint, params=None):
        """Make HTTP request to OKX API with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            logging.debug(f"Making request to: {url} with params: {params}")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != '0':
                logging.error(f"OKX API error: {data.get('msg', 'Unknown error')}")
                return None
                
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return None

    def get_candlestick_data(self, symbol, timeframe, limit=100):
        """Get candlestick (OHLCV) data for a symbol"""
        # Map timeframe to OKX format
        timeframe_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        
        okx_timeframe = timeframe_map.get(timeframe, '1H')
        
        params = {
            'instId': symbol,
            'bar': okx_timeframe,
            'limit': min(limit, 300)  # OKX max limit is 300
        }
        
        data = self._make_request('/api/v5/market/candles', params)
        
        if not data:
            return None
            
        # Format data for frontend
        formatted_data = []
        for candle in data:
            try:
                # Ensure consistent data types
                timestamp = int(candle[0]) if candle[0] else 0
                formatted_data.append({
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp/1000, timezone.utc).isoformat(),
                    'open': float(candle[1]) if candle[1] else 0.0,
                    'high': float(candle[2]) if candle[2] else 0.0,
                    'low': float(candle[3]) if candle[3] else 0.0,
                    'close': float(candle[4]) if candle[4] else 0.0,
                    'volume': float(candle[5]) if candle[5] else 0.0,
                    'volume_currency': float(candle[6]) if candle[6] else 0.0
                })
            except (ValueError, IndexError, TypeError) as e:
                logging.warning(f"Error parsing candle data: {e}")
                continue
                
        # Sort by timestamp (oldest first)
        formatted_data.sort(key=lambda x: x['timestamp'])
        
        return formatted_data

    def get_orderbook_data(self, symbol, depth=50):
        """Get orderbook data for a symbol"""
        params = {
            'instId': symbol,
            'sz': min(depth, 400)  # OKX max depth is 400
        }
        
        data = self._make_request('/api/v5/market/books', params)
        
        if not data or not data[0]:
            return None
            
        orderbook = data[0]
        
        # Format orderbook data
        formatted_data = {
            'timestamp': int(orderbook.get('ts', 0)),
            'datetime': datetime.fromtimestamp(int(orderbook.get('ts', 0))/1000, timezone.utc).isoformat(),
            'bids': [],
            'asks': []
        }
        
        # Process bids (buyers)
        for bid in orderbook.get('bids', []):
            try:
                formatted_data['bids'].append({
                    'price': float(bid[0]),
                    'size': float(bid[1]),
                    'orders': int(bid[2]) if len(bid) > 2 else 0
                })
            except (ValueError, IndexError) as e:
                logging.warning(f"Error parsing bid data: {e}")
                continue
        
        # Process asks (sellers)
        for ask in orderbook.get('asks', []):
            try:
                formatted_data['asks'].append({
                    'price': float(ask[0]),
                    'size': float(ask[1]),
                    'orders': int(ask[2]) if len(ask) > 2 else 0
                })
            except (ValueError, IndexError) as e:
                logging.warning(f"Error parsing ask data: {e}")
                continue
        
        return formatted_data

    def get_open_interest_data(self, symbol):
        """Get open interest data for a symbol"""
        # Convert spot symbols to futures symbols for open interest
        if symbol.endswith('-USDT'):
            futures_symbol = symbol + '-SWAP'
        else:
            futures_symbol = symbol
            
        params = {
            'instId': futures_symbol
        }
        
        data = self._make_request('/api/v5/public/open-interest', params)
        
        if not data or not data[0]:
            return None
            
        oi_data = data[0]
        
        # Format open interest data
        formatted_data = {
            'timestamp': int(oi_data.get('ts', 0)),
            'datetime': datetime.fromtimestamp(int(oi_data.get('ts', 0))/1000, timezone.utc).isoformat(),
            'open_interest': float(oi_data.get('oi', 0)),
            'open_interest_currency': float(oi_data.get('oiCcy', 0))
        }
        
        return formatted_data

    def get_ticker_data(self, symbol):
        """Get ticker data for a symbol"""
        params = {
            'instId': symbol
        }
        
        data = self._make_request('/api/v5/market/ticker', params)
        
        if not data or not data[0]:
            return None
            
        ticker = data[0]
        
        # Format ticker data
        formatted_data = {
            'timestamp': int(ticker.get('ts', 0)),
            'datetime': datetime.fromtimestamp(int(ticker.get('ts', 0))/1000, timezone.utc).isoformat(),
            'last_price': float(ticker.get('last', 0)),
            'best_bid': float(ticker.get('bidPx', 0)),
            'best_ask': float(ticker.get('askPx', 0)),
            'volume_24h': float(ticker.get('vol24h', 0)),
            'volume_currency_24h': float(ticker.get('volCcy24h', 0)),
            'high_24h': float(ticker.get('high24h', 0)),
            'low_24h': float(ticker.get('low24h', 0)),
            'change_24h': float(ticker.get('chg24h', 0)),
            'change_percent_24h': float(ticker.get('chgPct24h', 0))
        }
        
        return formatted_data

    def get_ticker_data(self, symbol):
        """Get ticker data for a symbol"""
        params = {'instId': symbol}
        data = self._make_request('/api/v5/market/ticker', params)
        
        if not data:
            return None
            
        try:
            ticker = data[0]
            formatted_data = {
                'symbol': ticker.get('instId', ''),
                'last_price': float(ticker.get('last', 0)),
                'bid_price': float(ticker.get('bidPx', 0)),
                'ask_price': float(ticker.get('askPx', 0)),
                'bid_size': float(ticker.get('bidSz', 0)),
                'ask_size': float(ticker.get('askSz', 0)),
                'volume_24h': float(ticker.get('vol24h', 0)),
                'volume_currency_24h': float(ticker.get('volCcy24h', 0)),
                'open_24h': float(ticker.get('open24h', 0)),
                'high_24h': float(ticker.get('high24h', 0)),
                'low_24h': float(ticker.get('low24h', 0)),
                'change_24h': float(ticker.get('chg24h', 0)),
                'change_percent_24h': float(ticker.get('chgPct24h', 0)),
                'timestamp': int(ticker.get('ts', 0)),
                'datetime': datetime.fromtimestamp(int(ticker.get('ts', 0))/1000, timezone.utc).isoformat()
            }
            return formatted_data
        except Exception as e:
            logging.error(f"Error formatting ticker data: {e}")
            return None

    def get_trades_data(self, symbol, limit=100):
        """Get recent trades data for a symbol"""
        params = {
            'instId': symbol,
            'limit': min(limit, 500)  # OKX max limit is 500
        }
        data = self._make_request('/api/v5/market/trades', params)
        
        if not data:
            return None
            
        formatted_data = []
        for trade in data:
            try:
                formatted_data.append({
                    'trade_id': trade.get('tradeId', ''),
                    'price': float(trade.get('px', 0)),
                    'size': float(trade.get('sz', 0)),
                    'side': trade.get('side', ''),  # 'buy' or 'sell'
                    'timestamp': int(trade.get('ts', 0)),
                    'datetime': datetime.fromtimestamp(int(trade.get('ts', 0))/1000, timezone.utc).isoformat()
                })
            except Exception as e:
                logging.warning(f"Error parsing trade data: {e}")
                continue
        
        return formatted_data

    def get_index_tickers(self, symbol):
        """Get index price tickers for a symbol"""
        params = {'instId': symbol}
        data = self._make_request('/api/v5/market/index-tickers', params)
        
        if not data:
            return None
            
        try:
            ticker = data[0]
            formatted_data = {
                'symbol': ticker.get('instId', ''),
                'index_price': float(ticker.get('idxPx', 0)),
                'high_24h': float(ticker.get('high24h', 0)),
                'low_24h': float(ticker.get('low24h', 0)),
                'open_24h': float(ticker.get('open24h', 0)),
                'change_24h': float(ticker.get('chg24h', 0)),
                'change_percent_24h': float(ticker.get('chgPct24h', 0)),
                'timestamp': int(ticker.get('ts', 0)),
                'datetime': datetime.fromtimestamp(int(ticker.get('ts', 0))/1000, timezone.utc).isoformat()
            }
            return formatted_data
        except Exception as e:
            logging.error(f"Error formatting index ticker data: {e}")
            return None

    def get_mark_price(self, symbol):
        """Get mark price for a symbol (futures)"""
        params = {'instId': symbol}
        data = self._make_request('/api/v5/public/mark-price', params)
        
        if not data:
            return None
            
        try:
            mark_data = data[0]
            formatted_data = {
                'symbol': mark_data.get('instId', ''),
                'mark_price': float(mark_data.get('markPx', 0)),
                'timestamp': int(mark_data.get('ts', 0)),
                'datetime': datetime.fromtimestamp(int(mark_data.get('ts', 0))/1000, timezone.utc).isoformat()
            }
            return formatted_data
        except Exception as e:
            logging.error(f"Error formatting mark price data: {e}")
            return None

    def get_funding_rate(self, symbol):
        """Get funding rate for a symbol (futures)"""
        params = {'instId': symbol}
        data = self._make_request('/api/v5/public/funding-rate', params)
        
        if not data:
            return None
            
        try:
            funding_data = data[0]
            formatted_data = {
                'symbol': funding_data.get('instId', ''),
                'funding_rate': float(funding_data.get('fundingRate', 0)),
                'next_funding_time': int(funding_data.get('nextFundingTime', 0)),
                'next_funding_datetime': datetime.fromtimestamp(int(funding_data.get('nextFundingTime', 0))/1000, timezone.utc).isoformat(),
                'timestamp': int(funding_data.get('ts', 0)),
                'datetime': datetime.fromtimestamp(int(funding_data.get('ts', 0))/1000, timezone.utc).isoformat()
            }
            return formatted_data
        except Exception as e:
            logging.error(f"Error formatting funding rate data: {e}")
            return None

    def get_all_instruments(self, inst_type=None):
        """Get list of all instruments (spot, futures, options)"""
        if inst_type:
            params = {'instType': inst_type}
        else:
            params = {}
        
        data = self._make_request('/api/v5/public/instruments', params)
        
        if not data:
            return []
        
        formatted_instruments = []
        for instrument in data:
            try:
                formatted_instruments.append({
                    'symbol': instrument.get('instId', ''),
                    'base_currency': instrument.get('baseCcy', ''),
                    'quote_currency': instrument.get('quoteCcy', ''),
                    'instrument_type': instrument.get('instType', ''),
                    'state': instrument.get('state', ''),
                    'tick_size': float(instrument.get('tickSz', 0)),
                    'lot_size': float(instrument.get('lotSz', 0)),
                    'min_size': float(instrument.get('minSz', 0)),
                    'contract_value': float(instrument.get('ctVal', 0)) if instrument.get('ctVal') else None,
                    'contract_type': instrument.get('ctType', ''),
                    'settlement_currency': instrument.get('settleCcy', ''),
                    'listing_time': int(instrument.get('listTime', 0)),
                    'listing_datetime': datetime.fromtimestamp(int(instrument.get('listTime', 0))/1000, timezone.utc).isoformat() if instrument.get('listTime') else None,
                    'expiry_time': int(instrument.get('expTime', 0)) if instrument.get('expTime') else None,
                    'expiry_datetime': datetime.fromtimestamp(int(instrument.get('expTime', 0))/1000, timezone.utc).isoformat() if instrument.get('expTime') else None
                })
            except Exception as e:
                logging.warning(f"Error parsing instrument data: {e}")
                continue
        
        return formatted_instruments

    def get_delivery_exercise_history(self, underlying=None, inst_type='FUTURES'):
        """Get delivery/exercise history for futures"""
        params = {'instType': inst_type}
        
        if underlying:
            params['uly'] = underlying
        
        data = self._make_request('/api/v5/public/delivery-exercise-history', params)
        
        if not data:
            return []
        
        formatted_history = []
        for item in data:
            try:
                details = item.get('details', [])
                for detail in details:
                    formatted_history.append({
                        'symbol': detail.get('insId', ''),
                        'delivery_price': float(detail.get('px', 0)),
                        'delivery_time': int(item.get('ts', 0)),
                        'delivery_datetime': datetime.fromtimestamp(int(item.get('ts', 0))/1000, timezone.utc).isoformat(),
                        'delivery_type': detail.get('type', ''),
                        'underlying': underlying or 'N/A'
                    })
            except Exception as e:
                logging.warning(f"Error parsing delivery history data: {e}")
                continue
        
        return formatted_history

    def get_estimated_funding_rate(self, symbol):
        """Get estimated funding rate for next period"""
        params = {'instId': symbol}
        data = self._make_request('/api/v5/public/funding-rate', params)
        
        if not data:
            return None
        
        try:
            funding_data = data[0]
            formatted_data = {
                'symbol': funding_data.get('instId', ''),
                'funding_rate': float(funding_data.get('fundingRate', 0)),
                'realized_rate': float(funding_data.get('realizedRate', 0)),
                'next_funding_time': int(funding_data.get('nextFundingTime', 0)),
                'next_funding_datetime': datetime.fromtimestamp(int(funding_data.get('nextFundingTime', 0))/1000, timezone.utc).isoformat(),
                'funding_interval': funding_data.get('fundingInterval', ''),
                'timestamp': int(funding_data.get('ts', 0)),
                'datetime': datetime.fromtimestamp(int(funding_data.get('ts', 0))/1000, timezone.utc).isoformat()
            }
            return formatted_data
        except Exception as e:
            logging.error(f"Error formatting estimated funding rate data: {e}")
            return None

    def get_available_symbols(self):
        """Get list of available trading symbols"""
        spot_data = self._make_request('/api/v5/public/instruments', {'instType': 'SPOT'})
        
        if not spot_data:
            # Return default symbols if API fails
            return [
                {'symbol': 'BTC-USDT', 'name': 'Bitcoin / Tether', 'type': 'SPOT'},
                {'symbol': 'ETH-USDT', 'name': 'Ethereum / Tether', 'type': 'SPOT'},
                {'symbol': 'BNB-USDT', 'name': 'Binance Coin / Tether', 'type': 'SPOT'},
                {'symbol': 'ADA-USDT', 'name': 'Cardano / Tether', 'type': 'SPOT'},
                {'symbol': 'SOL-USDT', 'name': 'Solana / Tether', 'type': 'SPOT'},
                {'symbol': 'DOT-USDT', 'name': 'Polkadot / Tether', 'type': 'SPOT'},
                {'symbol': 'MATIC-USDT', 'name': 'Polygon / Tether', 'type': 'SPOT'},
                {'symbol': 'AVAX-USDT', 'name': 'Avalanche / Tether', 'type': 'SPOT'}
            ]
        
        # Format symbols data
        formatted_symbols = []
        for instrument in spot_data[:30]:  # Limit to top 30 symbols
            try:
                if instrument.get('state') == 'live':
                    formatted_symbols.append({
                        'symbol': instrument.get('instId', ''),
                        'name': f"{instrument.get('baseCcy', '')} / {instrument.get('quoteCcy', '')}",
                        'type': 'SPOT'
                    })
            except Exception as e:
                logging.warning(f"Error parsing instrument data: {e}")
                continue
        
        return formatted_symbols

# Standalone function for direct usage
def get_candlesticks(instId, bar="1H", limit=100):
    """Standalone function to get candlestick data"""
    okx_service = OKXService()
    return okx_service.get_candlestick_data(instId, bar, limit)
