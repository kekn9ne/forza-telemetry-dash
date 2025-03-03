from flask import Flask, Response, render_template
import socket
import struct
import json
import threading
import time
from datetime import datetime
import os
import sys
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich import print as rprint

console = Console()

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Load settings
settings_path = get_resource_path('settings.json')
with open(settings_path, 'r') as f:
    settings = json.load(f)

app = Flask(__name__, 
           template_folder=get_resource_path('templates'))

class ForzaData:
    def __init__(self):
        self.current_rpm = 0
        self.max_rpm = 0
        self.gear = 0
        self.speed = 0
        self.throttle = 0
        self.last_rpm = 0
        self.last_few_rpms = []
        self.rev_limiter_rpm = 0
        self.debug_values = {}
        self.running = True
        self.connected = False
        self.last_data_time = 0
        self.sock = None
        
    def log_message(self, message):
        rprint(message)
        
    def parse_data(self, data):
        self.last_data_time = time.time()
        self.connected = True
        
        self.max_rpm = struct.unpack('f', data[8:12])[0]
        self.current_rpm = struct.unpack('f', data[16:20])[0]
        self.gear = data[319]
        
        speed_ms = struct.unpack('f', data[40:44])[0]
        self.speed = abs(speed_ms) * 3.6
        
        self.throttle = data[315] / 255.0
        
        if len(data) >= 320:
            self.debug_values = {
                'throttle': self.throttle,
                'current_rpm': self.current_rpm,
                'max_rpm': self.max_rpm,
                'gear': self.gear,
                'speed': self.speed
            }

    def start_listening(self):
        rprint("[yellow]Waiting for Forza Horizon 5 data...[/yellow]")
        
        # Initialize socket
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', settings['forza']['udp_port']))
        
        connection_notified = False
        disconnection_notified = False
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.parse_data(data)
                
                if not connection_notified:
                    rprint("[bold green]Connected to Forza Horizon 5![/bold green]")
                    connection_notified = True
                    disconnection_notified = False
                    
            except Exception as e:
                rprint(f"[red]Error: {e}[/red]")
                self.connected = False
                if not disconnection_notified:
                    rprint("[red]Lost connection to Forza Horizon 5[/red]")
                    disconnection_notified = True
                    connection_notified = False
                continue
            
            if time.time() - self.last_data_time > 5:
                self.connected = False
                if not disconnection_notified:
                    rprint("[red]Lost connection to Forza Horizon 5[/red]")
                    disconnection_notified = True
                    connection_notified = False

# Create global ForzaData instance
forza = ForzaData()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def generate():
        last_connection_state = None
        while True:
            # Send connection status if it changed
            if last_connection_state != forza.connected:
                status_data = {
                    'type': 'connection_status',
                    'connected': forza.connected,
                    'message': 'Connected to Forza Horizon 5' if forza.connected else 'Waiting for Forza Horizon 5 data...'
                }
                yield f"data: {json.dumps(status_data)}\n\n"
                last_connection_state = forza.connected
            
            # Send regular telemetry data
            data = {
                'type': 'telemetry',
                'current_rpm': forza.current_rpm,
                'max_rpm': forza.max_rpm,
                'gear': forza.gear,
                'speed': forza.speed,
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.016)  # ~60Hz update rate
            
    return Response(generate(), mimetype='text/event-stream')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/debug_stream')
def debug_stream():
    def generate():
        while True:
            data = {
                'debug_values': {
                    'throttle': forza.throttle,
                    'rpm_change': forza.current_rpm - forza.last_rpm,
                    'rev_limiter': forza.rev_limiter_rpm,
                    'current_rpm': forza.current_rpm,
                    'max_rpm': forza.max_rpm,
                    'gear': forza.gear,
                    'last_rpms': forza.last_few_rpms,
                    'rpm_range': max(forza.last_few_rpms) - min(forza.last_few_rpms) if forza.last_few_rpms else 0,
                    'avg_rpm': sum(forza.last_few_rpms) / len(forza.last_few_rpms) if forza.last_few_rpms else 0,
                    'rpm_percent': (forza.current_rpm / forza.max_rpm * 100) if forza.max_rpm else 0,
                    'at_limiter': (forza.throttle > 0.9 and 
                                 forza.current_rpm > 0.97 * forza.max_rpm and 
                                 (max(forza.last_few_rpms) - min(forza.last_few_rpms)) < 200)
                }
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.016)  # ~60Hz update rate
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    # Start the Forza data listener in a separate thread
    forza_thread = threading.Thread(target=forza.start_listening)
    forza_thread.daemon = True
    forza_thread.start()
    
    rprint("[bold cyan]Starting Forza Telemetry Server (Development Mode)[/bold cyan]")
    rprint("[yellow]Make sure Data Out is enabled in Forza Horizon 5 settings![/yellow]")
    rprint(f"[green]Open http://localhost:5000 in your web browser[/green]")
    rprint(f"[blue]For gear debugging, open http://localhost:5000/debug[/blue]")
    
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)
    
    rprint("[bold green]✓ Web server is running![/bold green]")
