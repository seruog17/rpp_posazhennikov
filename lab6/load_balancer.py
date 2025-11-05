from flask import Flask, request, jsonify, redirect, render_template_string
import requests
import threading
import time

app = Flask(__name__)

INSTANCE_POOL = [
    {"ip": "127.0.0.1", "port": 5001, "active": True},
    {"ip": "127.0.0.1", "port": 5002, "active": True},
    {"ip": "127.0.0.1", "port": 5003, "active": True}
]

current_index = 0
pool_lock = threading.Lock()

def check_instance_health(instance):
    try:
        url = f"http://{instance['ip']}:{instance['port']}/health"
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except:
        return False

def health_check_loop():
    while True:
        with pool_lock:
            for instance in INSTANCE_POOL:
                is_healthy = check_instance_health(instance)
                instance['active'] = is_healthy
        time.sleep(5)

def get_next_instance():
    global current_index
    with pool_lock:
        active_instances = [inst for inst in INSTANCE_POOL if inst['active']]
        if not active_instances:
            return None
        for i in range(len(INSTANCE_POOL)):
            calculated_index = (current_index + i) % len(INSTANCE_POOL)
            candidate_instance = INSTANCE_POOL[calculated_index]
            if candidate_instance['active']:
                current_index = (calculated_index + 1) % len(INSTANCE_POOL)
                return candidate_instance
    return None

@app.route('/health')
def lb_health():
    with pool_lock:
        instances_info = []
        for instance in INSTANCE_POOL:
            instances_info.append({
                "ip": instance['ip'],
                "port": instance['port'],
                "active": instance['active']
            })
    return jsonify({"instance_pool": instances_info})

@app.route('/process')
def lb_process():
    target_instance = get_next_instance()
    if not target_instance:
        return jsonify({"error": "Нет доступных серверов"}), 503
    try:
        target_url = f"http://{target_instance['ip']}:{target_instance['port']}/process"
        response = requests.get(target_url, timeout=5)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Сервер недоступен: {str(e)}"}), 502

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Балансировщик нагрузки</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; }
        .form-group { margin: 15px 0; }
        input { padding: 8px; width: 200px; margin-right: 10px; border: 1px solid #ccc; }
        button { padding: 8px 15px; border: 1px solid #ccc; background: white; }
        .server-list { margin-top: 20px; }
        .server-item { padding: 10px; margin: 5px 0; border: 1px solid #ccc; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Балансировщик нагрузки</h1>
        
        <div class="form-group">
            <h3>Добавить сервер</h3>
            <form action="/add_instance" method="post">
                <input type="text" name="ip" placeholder="IP адрес" value="127.0.0.1" required>
                <input type="number" name="port" placeholder="Порт" required>
                <button type="submit">Добавить</button>
            </form>
        </div>

        <div class="server-list">
            <h3>Список серверов</h3>
            {% for instance in instances %}
            <div class="server-item">
                <div>
                    <strong>{{ instance.ip }}:{{ instance.port }}</strong>
                    <span style="margin-left: 10px;">
                        {{ 'Активен' if instance.active else 'Неактивен' }}
                    </span>
                </div>
                <form action="/remove_instance" method="post" style="display:inline;">
                    <input type="hidden" name="index" value="{{ loop.index0 }}">
                    <button type="submit">Удалить</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def control_panel():
    with pool_lock:
        return render_template_string(HTML_TEMPLATE, instances=INSTANCE_POOL)

@app.route('/add_instance', methods=['POST'])
def add_instance():
    ip = request.form['ip']
    port = int(request.form['port'])
    with pool_lock:
        INSTANCE_POOL.append({"ip": ip, "port": port, "active": True})
    return redirect('/')

@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index = int(request.form['index'])
    with pool_lock:
        if 0 <= index < len(INSTANCE_POOL):
            INSTANCE_POOL.pop(index)
    return redirect('/')

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    target_instance = get_next_instance()
    if not target_instance:
        return jsonify({"error": "Нет доступных серверов"}), 503
    try:
        target_url = f"http://{target_instance['ip']}:{target_instance['port']}/{path}"
        if request.method == 'GET':
            response = requests.get(target_url, timeout=5)
        else:
            response = requests.post(target_url, data=request.form, timeout=5)
        return response.content, response.status_code, response.headers.items()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Сервер недоступен: {str(e)}"}), 502

if __name__ == '__main__':
    health_thread = threading.Thread(target=health_check_loop)
    health_thread.daemon = True
    health_thread.start()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)