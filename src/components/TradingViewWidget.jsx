import React, { useEffect, useRef } from 'react';

const TradingViewWidget = ({ symbol = 'BINANCE:SOLUSDT', interval = '15' }) => {
  const containerRef = useRef();

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      new window.TradingView.widget({
        autosize: true,
        symbol: symbol,
        interval: interval,
        timezone: 'Etc/UTC',
        theme: 'dark',
        style: '1',
        locale: 'en',
        toolbar_bg: '#131722',
        enable_publishing: false,
        hide_side_toolbar: false,
        allow_symbol_change: true,
        container_id: containerRef.current.id,
      });
    };

    containerRef.current.appendChild(script);
  }, [symbol, interval]);

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden" style={{ height: '500px' }}>
      <div id="tradingview_widget" ref={containerRef} className="h-full w-full" />
    </div>
  );
};

export default TradingViewWidget;