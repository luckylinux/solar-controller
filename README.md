# solar-controller
Solar Controller Tools designed to control a custom-made Solar Setup.

Primarily intended to be installed on a SBC (e.g. Raspberry PI 2/3/4), but in theory should also work in a Virtual Machine (e.g. KVM) or any Generic X86/AMD64 Computer.

# Setup
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
pip install -r ./requirements.txt
```

# Charger
## Introduction
The Charger control is based on the Emerson R48-300e0e3 script from https://github.com/PurpleAlien/R48_Rectifier.

## R48_Rectifier
CAN control of an Emerson/Vertiv R48 Rectifier, such as an R48-3000e3. These kinds of rectifiers are used in telecom equipment etc., but can be repurposed to serve as a cheap LiFePO4 battery charger in for example a 16s cell configuration. These kinds of devices are used for this purpose in the popular 'Chargeverter' from Signature Solar.

A used and pre-configured R48-3000e3 (3kW) with adapter interface can be found e.g. on Aliexpress for under €100 shipping included: https://s.click.aliexpress.com/e/_DeSzqo9

