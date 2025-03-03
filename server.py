from waitress import serve
from main import app, forza, settings
import threading
import os
import sys
import socket
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
import logging
from waitress.server import create_server

console = Console()

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_local_ip():
    """Get the local IPv4 address"""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'localhost'

def print_welcome_message(web_host, web_port, udp_port, local_ip):
    # Create title
    title = Text("Forza Telemetry Server", style="bold cyan")
    console.print(Panel(title, box=box.DOUBLE))
    
    # Create server info table
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Property", style="bright_white")
    table.add_column("Value", style="green")
    
    table.add_row("Web Server", f"http://{web_host if web_host != '0.0.0.0' else local_ip}:{web_port}")
    table.add_row("Local Access", f"http://{local_ip}:{web_port}")
    table.add_row("Debug Interface", f"http://{local_ip}:{web_port}/debug")
    table.add_row("Forza UDP Port", str(udp_port))
    
    console.print(Panel(table, title="[yellow]Server Information", box=box.ROUNDED))
    
    # Print instructions
    instructions = Text.assemble(
        ("Instructions:", "bold yellow"),
        "\n1. ", ("Make sure Data Out is enabled in Forza Horizon 5 settings", "bright_white"),
        "\n2. ", ("Set the UDP port to ", "bright_white"), 
        (str(udp_port), "green"),
        "\n3. ", ("Open ", "bright_white"),
        (f"http://{local_ip}:{web_port}", "cyan"),
        (" in your web browser", "bright_white")
    )
    console.print(Panel(instructions, title="[yellow]Setup Guide", box=box.ROUNDED))

if __name__ == '__main__':
    # Clear the terminal
    console.clear()
    
    # Start the Forza data listener in a separate thread
    forza_thread = threading.Thread(target=forza.start_listening)
    forza_thread.daemon = True
    forza_thread.start()
    
    web_host = settings['web_server']['host']
    web_port = settings['web_server']['port']
    udp_port = settings['forza']['udp_port']
    local_ip = get_local_ip()
    
    print_welcome_message(web_host, web_port, udp_port, local_ip)
    
    # Disable waitress logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.ERROR)
    
    # Start the server
    console.print("\n[bold yellow]Starting web server...[/bold yellow]")
    server = create_server(app, host=web_host, port=web_port)
    console.print("[bold green]✓ Web server is running![/bold green]")
    
    try:
        server.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
        server.close() 