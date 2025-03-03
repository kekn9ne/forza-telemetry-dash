# Forza Telemetry

A real-time telemetry dashboard for Forza Horizon 5 that displays RPM, gear, and speed information in a simple web interface.

## Features

- Real-time RPM, gear, and speed display
- Shift indicator with customizable settings
- Beautiful UI with circular displays and progress bars
- Production-ready server with proper error handling

## Quick Start (Pre-built Executable)

1. Download the latest release from the [GitHub Releases](https://github.com/kekn9ne/forza-telemetry-dash/releases) page
2. Extract the ZIP file to your desired location
3. Run `forza_telemetry.exe`
4. Follow the Forza Horizon 5 setup instructions below

## Development Setup

### Requirements

- Python 3.x
- Forza Horizon 5 with Data Out enabled
- Web browser (Chrome/Firefox/Edge recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kekn9ne/forza-telemetry-dash.git
cd forza-telemetry
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

### Usage

#### Development Mode

Run the development server:
```bash
python main.py
```

#### Production Mode

Run the production server:
```bash
python server.py
```

#### Building from Source

Create a standalone executable:
```bash
python build.py
```

The executable and required files will be created in the `dist` folder.

## Configuration

Edit `settings.json` to configure:
- Web server port (default: 8080)
- UDP port for Forza data (default: 2048)

```json
{
    "web_server": {
        "host": "0.0.0.0",
        "port": 8080
    },
    "forza": {
        "udp_port": 2048
    }
}
```

## Forza Horizon 5 Setup

1. Open Forza Horizon 5 settings
2. Navigate to HUD AND GAMEPLAY
3. Find "DATA OUT" and set it to ON
4. Set the IP address to your computer's local IP (shown when you start the application)
5. Set the port to 2048 (or the port specified in your settings.json)

## Development

The project structure:
```
forza-telemetry/
├── main.py           # Development server & core functionality
├── server.py         # Production server
├── build.py          # Executable builder
├── settings.json     # Configuration file
├── requirements.txt  # Python dependencies
└── templates/        # Web interface templates
    └── index.html    # Main dashboard
```

## License

MIT License - feel free to use and modify as you like! 