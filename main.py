from app import app, socketio, init_scheduler

if __name__ == '__main__':
    # Initialize scheduler only when running as main
    init_scheduler()
    print("🚀 Starting Cryptocurrency Trading AI Platform...")
    print("📡 Server running at http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
