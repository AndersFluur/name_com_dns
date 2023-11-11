# name_com_dns

A script to run automatic dynamic DNS update of name.com DNS service, using their API.
The external IP address is read from the internet using https://ipinfo.io/ip
Loops forever, polling of external IP address with interval from command line.


# Usage

````
usage: name_com_dns [-h] -n NAME -d DOMAIN [-i INTERVAL] [-t TEST]

Update DNS records with external IP address

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Host name
  -d DOMAIN, --domain DOMAIN
                        Domain name
  -i INTERVAL, --interval INTERVAL
                        Polling interval in seconds
  -t TEST, --test TEST  Test mode. Run loop interval number of times and exit.
````

# Running unit tests

````bash
python -m unittest discover -s name_com_dns
````

# Build Python package

````bash
python3 setup.py bdist_wheel
````


# Install
## Install Python package

````bash
sudo pip3 install dist/name_com_dns-0.1-py3-none-any.whl 
````
## Create User and group

The -r option creates a system user, the -s /bin/false option sets the shell of the user to /bin/false (so nobody can log in as this user), and the -g namecomgroup option adds the user to the namecomgroup group.

````bash
sudo groupadd namecomgroup
sudo useradd -r -s /bin/false -g namecomgroup namecomuser
````

# Ubuntu service

Use the service file, 'name_com_dns.service' from this package

````bash
sudo cp name_com_dns.service /etc/systemd/system/
sudo systemctl daemon-reload                # Reload the systemd manager configuration
sudo systemctl enable name_com_dns.service  # Enable your service to start on boot
sudo systemctl start name_com_dns.service   # Start service
sudo systemctl status name_com_dns.service  # Check status
````
