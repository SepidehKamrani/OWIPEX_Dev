#!/bin/bash

# SSH to the remote server and execute commands
sudo apt-get update
sudo apt-get install -y git sshpass
ls
echo "step 1"
sshpass -p '78WDQEuz' ssh -o StrictHostKeyChecking=no root@134.209.227.43 <<EOF
cd PipeLineFolder
ls

if [ ! -d things-board-folder ]; then
    mkdir things-board-folder
    git clone https://gitlab.appunik-team.com/Appunik_Akshay/things-board-folder.git
else
    cd things-board-folder
    git pull origin main
    cd ..
fi

if [ ! -d things-board-initial-code ]; then
    mkdir things-board-initial-code
    git clone https://gitlab.appunik-team.com/Appunik_Akshay/things-board-initial-code.git
else
    cd things-board-initial-code
    git pull origin main
    cd ..
fi
rsync -va /root/PipeLineFolder/things-board-folder/src/* /root/PipeLineFolder/things-board-initial-code/ui-ngx/src/
rsync -va /root/PipeLineFolder/things-board-folder/thingsboard.conf /etc/thingsboard/conf/thingsboard.conf

echo rsync done

cd things-board-initial-code
ls
sudo apt-get install -y maven
# mvn clean install -DskipTests -Ddockerfile.skip=true
# wget https://github.com/thingsboard/thingsboard/releases/download/v3.5.1/thingsboard-3.5.1.deb
echo "Setup Done"

# sudo dpkg -i thingsboard-3.5.1.deb

cd ..

rsync -va /root/PipeLineFolder/things-board-initial-code/application/target/thingsboard.deb /root/PipeLineFolder/things-board-initial-code/
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
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '123456';"
service postgresql restart

# Connect to PostgreSQL and create the 'thingsboard' database
sudo -u postgres psql -d postgres -h localhost -U postgres -W <<EOF
CREATE DATABASE owipex-sql;
\q
EOF
echo "conf file rsync"
rsync -va /root/PipeLineFolder/thingsboard.conf /etc/thingsboard/conf/thingsboard.conf
echo "Database setup"
sshpass -p '78WDQEuz' ssh -o StrictHostKeyChecking=no root@134.209.227.43 <<EOF
cd ..
sudo /usr/share/thingsboard/bin/install/install.sh --loadDemo
EOF
cd PipeLineFolder/things-board-initial-code/
sudo dpkg -i thingsboard.deb
sudo service thingsboard start
echo "service start"
