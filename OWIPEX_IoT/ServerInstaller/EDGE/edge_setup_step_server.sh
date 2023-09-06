#!/bin/bash

# SSH to the remote server and execute commands
sudo apt-get update
sudo apt-get install -y git sshpass
ls
echo "step 1"
sshpass -p '53K#ZAkUZddk$$T' ssh -o StrictHostKeyChecking=no root@167.99.248.101 <<EOF
cd PipeLineFolder
ls

if [ ! -d things-board-initial-code ]; then
    mkdir things-board-initial-code
    git clone https://gitlab.appunik-team.com/Appunik_Akshay/things-board-initial-code.git
else
    cd things-board-initial-code
    git pull origin main
    cd ..
fi

cd things-board-initial-code
ls
sudo apt-get install maven
mvn clean install -DskipTests -Ddockerfile.skip=true
echo "Setup Done"

cd ..

rsync -va \\things-board-initial-code/application/target/thingsboard.deb \\things-board-initial-code/
EOF

sudo apt install -y curl

# Import the repository signing key
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg

# Add repository contents to your system
RELEASE=$(lsb_release -cs)
echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] https://apt.postgresql.org/pub/repos/apt ${RELEASE}-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Install and launch the postgresql service
sudo apt update
sudo apt -y install postgresql-12
sudo service postgresql start

# Switch to the postgres user and configure PostgreSQL
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'appunik';"
service postgresql restart

# Connect to PostgreSQL and create the 'thingsboard' database
sudo -u postgres psql -d postgres -h localhost -U postgres -W <<EOF
CREATE DATABASE thingsboard_edge15;
\q
EOF
echo "conf file rsync"
rsync -va /root/PipeLineFolder/tb-edge.conf /etc/tb-edge/conf/tb-edge.conf
echo "Database setup"
sshpass -p '53K#ZAkUZddk$$T' ssh -o StrictHostKeyChecking=no root@167.99.248.101 <<EOF
cd ..
sudo /usr/share/tb-edge/bin/install/install.sh
EOF
sudo dpkg -i tb-edge-3.5.1.1.deb
sudo service thingsboard start
echo "service start"