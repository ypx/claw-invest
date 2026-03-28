#!/bin/bash
cd /Users/nn/WorkBuddy/Claw
pkill -f "node.*server.js" 2>/dev/null
sleep 1
nohup node backend/src/server.js > /tmp/server.log 2>&1 &
echo "Server restarted"
