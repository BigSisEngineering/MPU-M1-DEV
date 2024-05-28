[Unit]
Description=BigSis Cage System
After=network.target
Wants=time-sync.target

[Service]
ExecStartPre=/bin/sleep 10
ExecStartPre=/home/linaro/check_date.sh
ExecStart=/usr/bin/python3 /home/linaro/Computer/main.py
WorkingDirectory=/home/linaro/Computer
Restart=always
User=linaro
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target