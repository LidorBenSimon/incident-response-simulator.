#!/bin/bash
echo "[$(date)] User john_doe logged in" >> /var/log/custom/activity.log
sleep 2
echo "[$(date)] Browsing to suspicious website..." >> /var/log/custom/activity.log
curl -s http://attacker_server/fake_login > /dev/null 2>&1
echo "[$(date)] HTTP request to evil-server completed" >> /var/log/custom/activity.log
