# solar-controller
Solar Controller Tools designed to control a custom-made Solar Setup.

Primarily intended to be installed on a SBC (e.g. Raspberry PI 2/3/4), but in theory should also work in a Virtual Machine (e.g. KVM) or any Generic X86/AMD64 Computer.

# Setup
## Install Dependencies
```
apt-get install git libopenblas-dev
```

Details:
- `git` is required in order to checkout the repository, fork and contribute to the project
- `libopenblas-dev` is required for `numpy` (installed in the `venv` via `pip`) to work properly


## Clone Repository
```
cd /opt
git clone https://github.com/luckylinux/solar-controller.git 
```

## Create Virtual Environment
```
python -m venv /opt/solar-controller/venv/
```

## Activate Environment
Refer to https://docs.python.org/3/library/venv.html ("How venvs work").

- Bash / ZSH: `source /opt/solar-controller/bin/activate`
- Fish: `source /opt/solar-controller/bin/activate.fish`
- CSH/TCSH: `source /opt/solar-controller/bin/activate.csh`


## Install Requirements
```
/opt/solar-controller/venv/bin/pip install -r ./requirements.txt
```

## Put tmp on RAMdisk (Reccomended)
In order to reduce disk write cycles & prevent Data Corruption, it is suggested to put the tmp folder on tmpfs / ramdisk.

Add to /etc/fstab
```
tmpfs		/opt/solar-controller/tmp         tmpfs   auto,rw,nodev,nosuid,size=512M          0		0
```

Suggest you also do
```
chattr +i /opt/solar-controller/tmp
```

In order to prevent writing to that folder UNLESS the tmpfs is correctly mounted.

## Setup CRON for Scheduled Operations
Put in `/etc/cron.d/solar-controller` so that the tool can periodically execute itself every minute
```
SHELL=/bin/bash
*/1 * * * * <username> source /opt/solar-controller/venv/bin/activate && python /opt/solar-controller/strategy/strategy.py
```

Note: in the future this might be replaced / complemented by a Systemd Service !

## Setup Systemd Service
Create the file `/lib/systemd/system/shellscript.service` and include the contents as follows

```
[Unit]
Description=Solar Controller Main Script

[Service]
ExecStart=/bin/bash -c 'cd /opt/solar-controller && ./start.sh'
ExecStop=/bin/bash -c 'cd /opt/solar-controller && ./stop.sh'

[Install]
WantedBy=multi-user.target
```

# Charger
## Introduction
The Charger control is based on the Emerson R48-300e0e3 script from https://github.com/PurpleAlien/R48_Rectifier.

## R48_Rectifier
CAN control of an Emerson/Vertiv R48 Rectifier, such as an R48-3000e3. These kinds of rectifiers are used in telecom equipment etc., but can be repurposed to serve as a cheap LiFePO4 battery charger in for example a 16s cell configuration. These kinds of devices are used for this purpose in the popular 'Chargeverter' from Signature Solar.

A used and pre-configured R48-3000e3 (3kW) with adapter interface can be found e.g. on Aliexpress for under €100 shipping included: https://s.click.aliexpress.com/e/_DeSzqo9

# Inverter Interface
## Deye
https://github.com/klatremis/esphome-for-deye

# Battery Interface
## JK BMS
https://github.com/syssi/esphome-jk-bms

# Utility & Distribution
# Denmark
### Data
This can Fetch your Electricity Consumption & Costs.

- eloverblik-utilities
     - Code: https://github.com/helmstedt/eloverblik-utilities
     - Description: https://helmstedt.dk/2023/05/hent-data-om-dit-elforbrug-fra-eloverblik-dk/
- pyeloverblik
     - Code: https://github.com/JonasPed/pyeloverblik

### Prices
- Elspot & Elbas Electricity Prices: https://github.com/kipe/nordpool

# Solar
#
