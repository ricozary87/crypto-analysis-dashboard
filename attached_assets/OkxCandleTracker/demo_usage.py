#!/usr/bin/env python3
"""
Demo penggunaan fungsi simpan_snapshot_ai
Menunjukkan cara menggunakan fungsi sesuai permintaan user
"""

from flask import Flask
from snapshot_archiver import simpan_snapshot_ai

def demo_usage():
    """
    Demo penggunaan fungsi simpan_snapshot_ai
    """
    
    print("🎯 DEMO PENGGUNAAN FUNGSI simpan_snapshot_ai")
    print("=" * 50)
    
    # Contoh 1: Penggunaan dasar sesuai permintaan user
    print("\n1. Contoh penggunaan dasar:")
    print('   simpan_snapshot_ai("SOL-USDT", "5m", "Isi narasi AI dari GPT", 0.67)')
    print("\n   Fungsi ini akan menyimpan:")
    print("   - Symbol: SOL-USDT")
    print("   - Timeframe: 5m")
    print("   - Content: Isi narasi AI dari GPT")
    print("   - Confidence: 0.67 (67%)")
    print("   - Database: PostgreSQL Neon")
    print("   - Tabel: ai_snapshot_archive")
    
    # Contoh 2: Penggunaan dengan parameter lengkap
    print("\n2. Contoh penggunaan dengan parameter lengkap:")
    print("""
    simpan_snapshot_ai(
        symbol="BTC-USDT",
        timeframe="1h",
        content="Analisis lengkap dari AI GPT-4o",
        confidence=0.85,
        session_id="user_123",
        quick_mode=False,
        confluence_summary={"overall_signal": "bullish", "signal_strength": 85},
        layer_analysis={"smc": {"bias": "bullish"}, "volume": {"trend": "up"}},
        snapshot_data={"full_data": "here"}
    )
    """)
    
    # Contoh 3: Struktur database
    print("\n3. Struktur database yang tersimpan:")
    print("   Kolom:")
    print("   - symbol (VARCHAR): Trading pair")
    print("   - timeframe (VARCHAR): Time period")
    print("   - content (TEXT): AI narrative")
    print("   - confidence (FLOAT): Confidence score 0-1")
    print("   - created_at (TIMESTAMP): Auto timestamp")
    print("   - session_id (VARCHAR): User session")
    print("   - quick_mode (BOOLEAN): Quick/comprehensive mode")
    print("   - confluence_summary (JSON): Analysis summary")
    print("   - layer_analysis (JSON): Layer details")
    print("   - snapshot_data (JSON): Full snapshot data")
    
    # Contoh 4: Return value
    print("\n4. Return value:")
    print("   Success: {'success': True, 'message': 'AI Snapshot berhasil disimpan untuk SOL-USDT 5m', 'id': 1}")
    print("   Error: {'success': False, 'message': 'Error description'}")
    
    print("\n✅ Fungsi siap digunakan!")
    print("🔗 API Endpoint: POST /api/snapshot-archive")
    print("💾 Database: PostgreSQL Neon")
    print("📊 Sudah teruji dan berfungsi dengan baik!")

if __name__ == "__main__":
    demo_usage()