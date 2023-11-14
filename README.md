# namecom_dns

A script to run automatic dynamic DNS update of name.com DNS service, using their API.
The external IP address is read from the internet using https://ipinfo.io/ip
Loops forever, polling of external IP address with interval read from command line.


# Usage

```
usage: namecom_dns [-h] -n NAME -d DOMAIN [-i INTERVAL] [-t TEST] [-l LOG] [--logdir LOGDIR]

Update DNS records with external IP address

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Host name
  -d DOMAIN, --domain DOMAIN
                        Domain name
  -i INTERVAL, --interval INTERVAL
                        Polling interval in seconds
  -t TEST, --test TEST  Test mode. Run loop interval number of times and exit.
  -l LOG, --log LOG     Log to namecom_dns.log
  --logdir LOGDIR       Log to namecom_dns.log in the specvified directory
```

# Running unit tests

```bash
python -m unittest discover -s namecom_dns
```

# Build Python package {#build}

```bash
# Make sure python is installed!

python3 setup.py bdist_wheel
```
The package is stored as a versioned file: ```./dist/namecom_dns-${MAJOR}.${MINOR}-py3-none-any.whl```

# Install

## Configure Environment file

These are the required settings in *namecom_dns.cfg*:

NAMECOM_REPO="location of namecom_dns repo"
NAMECOM_DOMAIN=YOUR_DOMAIN
NAMECOM_HOSTNAME=YOUR_HOSTNAME
NAMECOM_APIUSERNAME=YOUR_APIUSERNAME
NAMECOM_APITOKEN=YOUR_APITOKEN

Set NAMECOM_HOSTNAME=@ for the apex domain (A record for example.com)

Edit the environment file:
```bash

sudo mkdir -p /etc/namecom/ && sudo cp namecom_dns.cfg /etc/namecom/
sudo chown -R namecomuser.namecomgroup /etc/namecom/
sudo chmod -R ug+rx,o-rwx /etc/namecom/
sudo nano /etc/namecom/namecom_dns.cfg                                # Edit as commented above!
```
## Install Python package

Use Python package built [before](#build)
```bash

# Make sure Python VENV is available:
sudo apt install -y python3.10-venv

# Create a venv (replace 'venv_name' with the desired name)
python3 -m venv venv

# Activate the venv
source venv/bin/activate

pip3 install dist/namecom_dns-0.1-py3-none-any.whl

```
## Create User and group

The -r option creates a system user, the -s /bin/false option sets the shell of the user to /bin/false (so nobody can log in as this user), and the -g namecomgroup option adds the user to the namecomgroup group.

```bash
sudo groupadd namecomgroup
sudo useradd -r -s /bin/false -g namecomgroup namecomuser
```

# Ubuntu service

Use the service file, 'namecom_dns.service.org' from this package. Copy it and and modify the copy to include API USER and TOKEN ans environment variables and domain and host as arguments.

(Make sure the venv from above is sourced)

```bash

sudo cp namecom_dns.service /etc/systemd/system/
sudo systemctl enable namecom_dns.service  # Enable your service to start on boot
sudo systemctl daemon-reload               # Reload the systemd manager configuration
sudo systemctl start namecom_dns.service   # Start service
sudo systemctl status namecom_dns.service  # Check status

# View log from service
sudo journalctl -u namecom_dns.service

# Show params of the service
sudo systemctl show namecom_dns.service

# Restore from the sourced VENV
deactivate
```
