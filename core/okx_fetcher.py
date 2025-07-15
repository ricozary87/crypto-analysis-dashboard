"""
OKX API data fetcher with rate limiting and caching
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import time
import os
import hmac
import hashlib
import base64

logger = logging.getLogger(__name__)

class OKXAPIManager:
    """OKX API manager with rate limiting and caching"""
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 0.05  # 50ms between requests
        
        # Load API credentials
        self.api_key = os.environ.get('OKX_API_KEY')
        self.secret_key = os.environ.get('OKX_SECRET_KEY')
        self.passphrase = os.environ.get('OKX_PASSPHRASE')
        
        # Check if credentials are available for authenticated requests
        self.has_credentials = all([self.api_key, self.secret_key, self.passphrase])
        
        if self.has_credentials:
            logger.info("OKX API initialized with authentication credentials")
        else:
            logger.warning("OKX API initialized without authentication credentials (public endpoints only)")
        
    def get_candles(self, symbol: str, timeframe: str = '1H', limit: int = 100) -> Optional[pd.DataFrame]:
        """Get candlestick data from OKX API"""
        
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        # Check cache first
        if self._is_cached(cache_key):
            logger.debug(f"Returning cached data for {symbol}")
            return self.cache[cache_key]['data']
        
        try:
            # Rate limiting
            self._rate_limit()
            
            # Map timeframe to OKX format
            tf_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1H': '1H',
                '4H': '4H',
                '1D': '1D'
            }
            
            okx_timeframe = tf_map.get(timeframe, '1H')
            
            # Build request URL
            url = f"{self.base_url}/api/v5/market/candles"
            params = {
                'instId': symbol,
                'bar': okx_timeframe,
                'limit': str(limit)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                # Convert to DataFrame
                df = pd.DataFrame(data['data'], columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'volCcy', 'volCcyQuote', 'confirm'
                ])
                
                # Process data with proper timestamp handling
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # Sort by timestamp
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': df,
                    'timestamp': datetime.now()
                }
                
                logger.debug(f"Fetched {len(df)} candles for {symbol}")
                return df
                
            else:
                logger.error(f"OKX API error for {symbol}: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            return None
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
            
        cached_time = self.cache[cache_key]['timestamp']
        if datetime.now() - cached_time > timedelta(seconds=self.cache_ttl):
            del self.cache[cache_key]
            return False
            
        return True
    
    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker data for a symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/ticker"
            params = {'instId': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Ticker API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_orderbook(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook data for a symbol"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/api/v5/market/books"
            params = {
                'instId': symbol,
                'sz': min(depth, 400)  # Max 400 levels
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                orderbook_data = data['data'][0]
                return {
                    'bids': orderbook_data.get('bids', []),
                    'asks': orderbook_data.get('asks', []),
                    'ts': orderbook_data.get('ts', None)
                }
            else:
                logger.error(f"Orderbook API error for {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return None
    
    def _generate_signature(self, method: str, path: str, body: str = '') -> tuple:
        """Generate OKX API signature for authenticated requests"""
        # Generate ISO timestamp
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        # Create message to sign
        message = timestamp + method + path + body
        
        # Create signature
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        return timestamp, signature
    
    def _get_auth_headers(self, method: str, path: str, body: str = '') -> Dict[str, str]:
        """Generate authentication headers for OKX API"""
        if not self.has_credentials:
            return {}
        
        timestamp, signature = self._generate_signature(method, path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get account balance: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/balance'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Account balance API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            return None
    
    def get_account_config(self) -> Optional[Dict[str, Any]]:
        """Get account configuration (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get account config: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/config'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0' and data.get('data'):
                return data['data'][0]
            else:
                logger.error(f"Account config API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching account config: {e}")
            return None
    
    def get_positions(self) -> Optional[list]:
        """Get account positions (authenticated endpoint)"""
        if not self.has_credentials:
            logger.warning("Cannot get positions: No credentials provided")
            return None
            
        try:
            self._rate_limit()
            
            method = 'GET'
            path = '/api/v5/account/positions'
            headers = self._get_auth_headers(method, path)
            
            url = f"{self.base_url}{path}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '0':
                return data.get('data', [])
            else:
                logger.error(f"Positions API error: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return None
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        if not self.has_credentials:
            logger.warning("Cannot test authentication: No credentials provided")
            return False
            
        try:
            config = self.get_account_config()
            return config is not None
            
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False