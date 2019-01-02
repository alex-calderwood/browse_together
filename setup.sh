# Get and install Chrome
sudo apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo dpkg -i google-chrome*.deb
sudo apt-get install -f

# Install utils
# sudo apt-get install xvfb # Only needed to run chrome in non-headless mode
sudo apt-get install unzip

# Install Chromedriver (should be latest version as of 12/30/18
wget -N http://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod +x chromedriver

sudo mv -f chromedriver /usr/local/share/chromedriver
sudo rm /usr/local/bin/chromedriver /usr/bin/chromedriver 2> /dev/null
sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

# Install the other requirements with pip
pip install -r requirements.txt
