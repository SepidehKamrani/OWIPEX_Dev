#!/bin/bash

# SSH to the remote server and execute commands
sudo apt-get update
sudo apt-get install -y git sshpass
ls
echo "step 1"
sshpass -p '78WDQEuz' ssh -o StrictHostKeyChecking=no root@167.172.189.151 <<EOF
cd PipeLineFolder
ls

if [ ! -d edge_initial_code ]; then
    mkdir edge_initial_code
    git clone https://gitlab.appunik-team.com/Appunik_Akshay/edge_initial_code.git
else
    cd edge_initial_code
    git pull origin main
    cd ..
fi

cd edge_initial_code
ls
sudo apt-get install -y maven
mvn clean install -DskipTests -Ddockerfile.skip=true
echo "Setup Done"

cd ..

rsync -va /root/PipeLineFolder/edge_initial_code/application/target/tb-edge.deb /root/PipeLineFolder/edge_initial_code/
rsync -va /root/PipeLineFolder/edge_initial_code/tb-edge.conf /etc/tb-edge/conf/tb-edge.conf
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
CREATE DATABASE ;
\q
EOF
echo "conf file rsync"
rsync -va /root/PipeLineFolder/tb-edge.conf /etc/tb-edge/conf/tb-edge.conf
echo "Database setup"
sshpass -p '78WDQEuz' ssh -o StrictHostKeyChecking=no root@167.172.189.151 <<EOF
cd ..
sudo /usr/share/tb-edge/bin/install/install.sh
EOF
cd PipeLineFolder/edge_initial_code/
sudo dpkg -i tb-edge.deb
sudo service tb-edge restart
sudo service tb-edge start
echo "service start"