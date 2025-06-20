#!/bin/bash
sudo yum update -y
sudo yum install -y httpd
sudo systemctl enable --now httpd
echo "<h1>Auto-Healing Lab $(hostname -f)</h1>" | sudo tee /var/www/html/index.html