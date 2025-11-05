from flask import Flask, jsonify
import sys

app = Flask(__name__)
current_port = None

@app.route('/health')
def health():
    return jsonify({
        "status": "OK",
        "message": f"Instance is running on port {current_port}",
        "port": current_port
    })

@app.route('/process')
def process():
    return jsonify({
        "message": "Request processed successfully!",
        "instance_port": current_port
    })

if __name__ == '__main__':
    current_port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=current_port, debug=True, use_reloader=False)