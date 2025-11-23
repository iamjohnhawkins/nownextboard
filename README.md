# Now-Next Board

A Raspberry Pi application that displays current and upcoming activities on a HyperPixel 4 touchscreen, helping children understand what they should be doing now and what's coming next.

## Features

- **Visual Display**: Pygame-based interface showing "Now" and "Next" activities
- **Timer Ring**: Visual progress indicator showing time remaining on current activity
- **Web UI**: React-based schedule management interface
- **REST API**: Flask backend for schedule management
- **Multiple Schedules**: Create and manage different daily routines
- **Customizable Activities**: Set activity names, times, durations, colors, and emoji icons

## Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- HyperPixel 4 Square touchscreen (800x480)
- Power supply
- SD card (16GB+ recommended)

## Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.9+
- Node.js 16+ (for React frontend development)

## Project Structure

```
nownextboard/
├── backend/              # Flask API server
│   ├── app.py           # Main Flask application
│   ├── models.py        # Data models for schedules
│   ├── requirements.txt # Python dependencies
│   └── run.sh          # Helper script to run backend
├── display/             # Pygame display application
│   ├── main.py         # Main display application
│   ├── renderer.py     # Rendering logic
│   ├── config.py       # Display configuration
│   ├── requirements.txt # Python dependencies
│   └── run.sh          # Helper script to run display
├── frontend/            # React web UI
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── ...
│   ├── package.json
│   └── public/
├── data/                # Schedule data storage
│   └── schedules.json  # JSON file with schedules
└── install_services.sh  # Install systemd services
```

## Installation

### 1. Setup Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pygame python3-pip python3-venv git

# Install HyperPixel 4 drivers (if not already installed)
curl https://get.pimoroni.com/hyperpixel4 | bash
```

### 2. Clone and Setup Project

```bash
# Clone or copy the project to your Pi
cd ~
# If using git:
# git clone <your-repo-url> nownextboard
# Otherwise, copy files to ~/nownextboard

cd nownextboard
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the backend
python app.py
```

The backend should now be running on `http://localhost:5001`

### 4. Setup Display Application

Open a new terminal:

```bash
cd ~/nownextboard/display

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the display (make sure backend is running first)
python main.py
```

Press `ESC` or `Q` to exit the display application.

### 5. Setup Web UI (Optional - for development)

The backend serves a pre-built React app. To develop the frontend:

```bash
cd ~/nownextboard/frontend

# Install Node.js if not already installed
# curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
# sudo apt install -y nodejs

# Install dependencies
npm install

# Run development server
npm start
```

To build for production:

```bash
npm run build
```

The built files will be served by the Flask backend.

### 6. Install as System Services (Auto-start on boot)

```bash
cd ~/nownextboard

# Make scripts executable
chmod +x backend/run.sh
chmod +x display/run.sh
chmod +x install_services.sh

# Install services (requires sudo)
sudo ./install_services.sh

# Start services
sudo systemctl start nownextboard-backend
sudo systemctl start nownextboard-display

# Check status
sudo systemctl status nownextboard-backend
sudo systemctl status nownextboard-display
```

## Usage

### Creating Schedules

1. **Access the Web UI**: Open a browser and go to `http://<raspberry-pi-ip>:5001`

2. **Create a Schedule**:
   - Click "Create New Schedule"
   - Enter a schedule name (e.g., "Morning Routine")
   - Add activities with the "Add Activity" button

3. **Configure Activities**:
   - **Name**: What the activity is (e.g., "Breakfast")
   - **Icon**: Emoji to display (e.g., 🍳) - optional, not displayed on cards
   - **Start Time**: When the activity begins (24-hour format)
   - **Duration**: How long it lasts (in minutes)
   - **Color**: Color for visual identification
   - **Background Image**: Optional URL to a calming stock photo
     - If left empty, the system will automatically select a relevant image based on the activity name
     - Supports Unsplash URLs for royalty-free images
     - Images are displayed at 30% opacity for a subtle, calming effect

4. **Activate Schedule**: Click "Activate" on a schedule to make it the current one

### Display Controls

- **ESC** or **Q**: Exit the display application
- **R**: Refresh data from API immediately

### API Endpoints

- `GET /api/schedules` - Get all schedules
- `POST /api/schedules` - Create a new schedule
- `GET /api/schedules/{id}` - Get specific schedule
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule
- `POST /api/schedules/{id}/activate` - Set schedule as active
- `GET /api/current` - Get current and next activities

## Configuration

### Display Settings

Edit [display/config.py](display/config.py):

```python
# Display resolution (HyperPixel 4)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Fullscreen mode
FULLSCREEN = True  # Set False for windowed mode

# API URL
API_URL = "http://localhost:5001"

# Poll interval (seconds)
POLL_INTERVAL = 5

# Colors and fonts can be customized
```

### Backend Settings

Edit [backend/app.py](backend/app.py):

```python
# Server configuration
app.run(host='0.0.0.0', port=5001, debug=True)
```

For production, set `debug=False`.

## Troubleshooting

### Display not showing

1. Check if backend is running:
   ```bash
   curl http://localhost:5001/api/current
   ```

2. Check display logs:
   ```bash
   sudo journalctl -u nownextboard-display -f
   ```

3. Verify HyperPixel drivers are installed:
   ```bash
   ls /dev/fb*
   ```

### No activities showing

1. Make sure a schedule is marked as "active"
2. Check if current time falls within any activity time range
3. Verify schedule times are in 24-hour format (HH:MM)

### Web UI not accessible

1. Check backend is running: `sudo systemctl status nownextboard-backend`
2. Check firewall settings
3. Try accessing from Pi itself: `http://localhost:5001`

### Timer ring not updating

The display polls every 5 seconds by default. The ring updates in real-time based on elapsed time.

## Development

### Running in Development Mode

**Backend**:
```bash
cd backend
source venv/bin/activate
python app.py
```

**Display** (in windowed mode):
```bash
cd display
# Edit config.py: FULLSCREEN = False
source venv/bin/activate
python main.py
```

**Frontend**:
```bash
cd frontend
npm start
```

### Testing on macOS/Linux

The display application can run in windowed mode for testing:

1. Install pygame: `pip install pygame`
2. Edit `display/config.py`: Set `FULLSCREEN = False`
3. Run: `python display/main.py`

## Sample Schedule

A sample "Morning Routine" schedule is included in [data/schedules.json](data/schedules.json) with activities like:
- Wake Up & Get Dressed (7:00 AM)
- Breakfast (7:15 AM)
- Brush Teeth (7:35 AM)
- Pack School Bag (7:40 AM)
- Shoes & Jacket (7:50 AM)
- Leave for School (7:55 AM)

## Future Enhancements

Potential features to add:
- Sound notifications when activities change
- Multiple schedule support (weekday/weekend)
- Reward system for completing activities on time
- Touch interface for basic controls
- Parent dashboard with completion tracking
- Image support for activities (in addition to emojis)

## License

This project is open source and available for personal use.

## Credits

Built with:
- Python & Pygame for display rendering
- Flask for the backend API
- React for the web interface
- HyperPixel 4 by Pimoroni
