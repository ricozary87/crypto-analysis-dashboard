"""
Snapshot Archiver - AI Snapshot Archive Management
Menyimpan dan mengelola arsip AI snapshot ke database PostgreSQL Neon
"""
import logging
import uuid
from datetime import datetime
from flask import session
from models import db, AISnapshotArchive

logger = logging.getLogger(__name__)

def simpan_snapshot_ai(symbol: str, timeframe: str, content: str, confidence: float, 
                       session_id: str = None, quick_mode: bool = False, 
                       confluence_summary: dict = None, layer_analysis: dict = None,
                       snapshot_data: dict = None):
    """
    Simpan hasil AI snapshot ke database PostgreSQL Neon
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'SOL-USDT')
        timeframe (str): Timeframe (e.g., '5m', '1h')
        content (str): AI narrative content dari GPT
        confidence (float): Confidence score (0-1)
        session_id (str, optional): Session ID pengguna
        quick_mode (bool, optional): Apakah menggunakan quick mode
        confluence_summary (dict, optional): Ringkasan confluence analysis
        layer_analysis (dict, optional): Detail layer analysis
        snapshot_data (dict, optional): Full snapshot data
    
    Returns:
        dict: {'success': bool, 'message': str, 'id': int}
    """
    try:
        # Generate session_id if not provided
        if not session_id:
            if 'user_id' in session:
                session_id = session['user_id']
            else:
                session_id = str(uuid.uuid4())
        
        # Validate inputs
        if not symbol or not timeframe or not content:
            return {
                'success': False,
                'message': 'Symbol, timeframe, dan content wajib diisi'
            }
        
        if confidence < 0 or confidence > 1:
            return {
                'success': False,
                'message': 'Confidence harus antara 0 dan 1'
            }
        
        # Create new AI snapshot archive entry
        ai_snapshot = AISnapshotArchive(
            session_id=session_id,
            symbol=symbol.upper(),
            timeframe=timeframe,
            quick_mode=quick_mode,
            ai_narrative=content,
            confluence_summary=confluence_summary,
            layer_analysis=layer_analysis,
            snapshot_data=snapshot_data,
            confidence=confidence,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(ai_snapshot)
        db.session.commit()
        
        logger.info(f"AI Snapshot saved successfully: {symbol} {timeframe} (ID: {ai_snapshot.id})")
        
        return {
            'success': True,
            'message': f'AI Snapshot berhasil disimpan untuk {symbol} {timeframe}',
            'id': ai_snapshot.id
        }
        
    except Exception as e:
        logger.error(f"Error saving AI snapshot: {str(e)}")
        db.session.rollback()
        return {
            'success': False,
            'message': f'Gagal menyimpan AI snapshot: {str(e)}'
        }

def get_snapshot_archive(session_id: str = None, symbol: str = None, 
                        timeframe: str = None, limit: int = 100):
    """
    Ambil arsip AI snapshot dari database
    
    Args:
        session_id (str, optional): Filter by session ID
        symbol (str, optional): Filter by symbol
        timeframe (str, optional): Filter by timeframe
        limit (int): Batas maksimal hasil
    
    Returns:
        list: List of AI snapshot archives
    """
    try:
        query = AISnapshotArchive.query
        
        if session_id:
            query = query.filter(AISnapshotArchive.session_id == session_id)
        
        if symbol:
            query = query.filter(AISnapshotArchive.symbol == symbol.upper())
        
        if timeframe:
            query = query.filter(AISnapshotArchive.timeframe == timeframe)
        
        # Order by created_at descending (terbaru dulu)
        query = query.order_by(AISnapshotArchive.created_at.desc())
        
        # Apply limit
        snapshots = query.limit(limit).all()
        
        return [snapshot.to_dict() for snapshot in snapshots]
        
    except Exception as e:
        logger.error(f"Error retrieving snapshot archive: {str(e)}")
        return []

def get_snapshot_by_id(snapshot_id: int):
    """
    Ambil AI snapshot berdasarkan ID
    
    Args:
        snapshot_id (int): ID snapshot
    
    Returns:
        dict: Snapshot data atau None jika tidak ditemukan
    """
    try:
        snapshot = AISnapshotArchive.query.get(snapshot_id)
        if snapshot:
            return snapshot.to_dict()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving snapshot by ID {snapshot_id}: {str(e)}")
        return None

def delete_snapshot(snapshot_id: int, session_id: str = None):
    """
    Hapus AI snapshot dari database
    
    Args:
        snapshot_id (int): ID snapshot yang akan dihapus
        session_id (str, optional): Validasi session ID untuk keamanan
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        query = AISnapshotArchive.query.filter(AISnapshotArchive.id == snapshot_id)
        
        # Validasi session_id untuk keamanan
        if session_id:
            query = query.filter(AISnapshotArchive.session_id == session_id)
        
        snapshot = query.first()
        
        if not snapshot:
            return {
                'success': False,
                'message': 'Snapshot tidak ditemukan atau tidak memiliki akses'
            }
        
        db.session.delete(snapshot)
        db.session.commit()
        
        logger.info(f"AI Snapshot deleted successfully: ID {snapshot_id}")
        
        return {
            'success': True,
            'message': 'Snapshot berhasil dihapus'
        }
        
    except Exception as e:
        logger.error(f"Error deleting snapshot {snapshot_id}: {str(e)}")
        db.session.rollback()
        return {
            'success': False,
            'message': f'Gagal menghapus snapshot: {str(e)}'
        }

def get_snapshot_statistics(session_id: str = None):
    """
    Dapatkan statistik AI snapshot
    
    Args:
        session_id (str, optional): Filter by session ID
    
    Returns:
        dict: Statistics data
    """
    try:
        query = AISnapshotArchive.query
        
        if session_id:
            query = query.filter(AISnapshotArchive.session_id == session_id)
        
        total_snapshots = query.count()
        
        # Count by symbol
        symbol_counts = {}
        snapshots = query.all()
        
        for snapshot in snapshots:
            symbol = snapshot.symbol
            if symbol not in symbol_counts:
                symbol_counts[symbol] = 0
            symbol_counts[symbol] += 1
        
        # Average confidence
        confidences = [s.confidence for s in snapshots if s.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'total_snapshots': total_snapshots,
            'symbol_counts': symbol_counts,
            'avg_confidence': avg_confidence,
            'quick_mode_count': query.filter(AISnapshotArchive.quick_mode == True).count(),
            'comprehensive_mode_count': query.filter(AISnapshotArchive.quick_mode == False).count()
        }
        
    except Exception as e:
        logger.error(f"Error getting snapshot statistics: {str(e)}")
        return {
            'total_snapshots': 0,
            'symbol_counts': {},
            'avg_confidence': 0,
            'quick_mode_count': 0,
            'comprehensive_mode_count': 0
        }