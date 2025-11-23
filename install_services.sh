#!/bin/bash
# Install systemd services for auto-start on Raspberry Pi

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create backend service
cat > /etc/systemd/system/nownextboard-backend.service << EOF
[Unit]
Description=Now-Next Board Backend API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create display service
cat > /etc/systemd/system/nownextboard-display.service << EOF
[Unit]
Description=Now-Next Board Display
After=network.target nownextboard-backend.service
Wants=nownextboard-backend.service

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/display
Environment=DISPLAY=:0
ExecStart=$PROJECT_DIR/display/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable nownextboard-backend.service
systemctl enable nownextboard-display.service

echo "Services installed successfully!"
echo ""
echo "To start the services now:"
echo "  sudo systemctl start nownextboard-backend"
echo "  sudo systemctl start nownextboard-display"
echo ""
echo "To check status:"
echo "  sudo systemctl status nownextboard-backend"
echo "  sudo systemctl status nownextboard-display"
echo ""
echo "Services will auto-start on boot."
