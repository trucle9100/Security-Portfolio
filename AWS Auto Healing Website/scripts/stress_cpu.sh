# SSH into instance (or use SSM)
sudo amazon-linux-extras install epel -y
sudo yum install stress -y
stress --cpu 2 --timeout 300  # Simulate 100% CPU for 5 mins