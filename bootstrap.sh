#!/usr/bin/env bash

# Install Heroku Toolbelt
#wget https://toolbelt.heroku.com/install-ubuntu.sh
#bash install-ubuntu.sh

# Install Chromium Browser
#sudo apt-get install chromium-browser

# Install Pycharm
#wget -c http://download.jetbrains.com/python/pycharm-2.7.3.tar.gz
#tar -xvf pycharm-2.7.3.tar.gz

# Install Git
#sudo apt-get install git

# Install make and libslite3-dev
sudo apt-get install -y make libsqlite3-dev

# Install Python3.3.3, setuptools, pip, bottle and create a virtual enve in home
sudo apt-get build-dep python3.2

sudo apt-get install -y libreadline-dev libncurses5-dev libssl1.0.0 tk8.5-dev zlib1g-dev liblzma-dev

wget http://python.org/ftp/python/3.3.3/Python-3.3.3.tgz
tar xvfz Python-3.3.3.tgz
cd Python-3.3.3
sudo ./configure --prefix=/opt/python3.3
make
sudo make install
/opt/python3.3/bin/pyvenv ~/python3.3
source ~/python3.3/bin/activate
wget http://python-distribute.org/distribute_setup.py
python distribute_setup.py
easy_install pip

# Install Java Ambient
#sudo add-apt-repository ppa:webupd8team/java
#sudo apt-get update
#sudo apt-get install oracle-java7-installer

