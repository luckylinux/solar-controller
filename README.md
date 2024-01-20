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

## USB Hubs & Experienced Issues
Please be aware when using a Powered USB Hub.

I have experienced very weird issues with the CAN Adapters with USB Powered Hubs (USB Hubs Powered by an AC Adapter).

The CAN Adapter would not throw any error message when executing the Rectifier Python script, but no Packet would be sent/received (could be printed when using `ifconfig` or `ip addr`). And of course, the Rectifier would NOT change the Output Voltage / Current to the requested setting.

This might be combined by the fact that - at the time - the script would NOT properly close the CAN connection.

No amount of reboots would solve the issue.

The only solution was to REMOVE the Power Cable from the USB Adapter. After doing that, and issueing a `reboot`, the system started working as expected.

There might be other solutions (like `usbreset` and similar that trigger a Power Cycle reset on the Requested USB Adapter) that could be worth investigating in the future though.

## Rename CAN Adapters
In case it is desired to use several Chargers, it can be beneficial to properly identify which CAN adapter controls which charger.

Unfortunately, at present, the Emerson R48-3000e has always the same Arbitration ID.

The proposed solution is therefore to rely on the Serial Number of the CAN Adapter.

The following has been tested on a CANAble Pro Adapter (Galvanically Isolated) from https://www.aliexpress.com/item/1005004972158302.html.

You need to Perform this Procedure One Adapter at the time. It is suggested to Properly Mark/Label the Associated CAN Adapter & Emerson Rectifier to avoid MisIdentification in case of e.g. Rewiring, change of USB port, ...

1. Find the Serial Number of your CAN Adapter
```
lsusb -v | grep -i iSerial
  iSerial                 3 002A002D4730511420303650
```

Or to get more information you can also use
```
udevadm info /sys/class/net/can0
P: /devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3:1.0/net/can0
M: can0
R: 0
U: net
I: 3
E: DEVPATH=/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3:1.0/net/can0
E: SUBSYSTEM=net
E: INTERFACE=can0
E: IFINDEX=3
E: USEC_INITIALIZED=16432091
E: ID_BUS=usb
E: ID_MODEL=candleLight_USB_to_CAN_adapter
E: ID_MODEL_ENC=candleLight\x20USB\x20to\x20CAN\x20adapter
E: ID_MODEL_ID=606f
E: ID_SERIAL=bytewerk_candleLight_USB_to_CAN_adapter_002A002D4730511420303650
E: ID_SERIAL_SHORT=002A002D4730511420303650
E: ID_VENDOR=bytewerk
E: ID_VENDOR_ENC=bytewerk
E: ID_VENDOR_ID=1d50
E: ID_REVISION=0000
E: ID_TYPE=generic
E: ID_USB_MODEL=candleLight_USB_to_CAN_adapter
E: ID_USB_MODEL_ENC=candleLight\x20USB\x20to\x20CAN\x20adapter
E: ID_USB_MODEL_ID=606f
E: ID_USB_SERIAL=bytewerk_candleLight_USB_to_CAN_adapter_002A002D4730511420303650
E: ID_USB_SERIAL_SHORT=002A002D4730511420303650
E: ID_USB_VENDOR=bytewerk
E: ID_USB_VENDOR_ENC=bytewerk
E: ID_USB_VENDOR_ID=1d50
E: ID_USB_REVISION=0000
E: ID_USB_TYPE=generic
E: ID_USB_INTERFACES=:ffffff:fe0101:
E: ID_USB_INTERFACE_NUM=00
E: ID_USB_DRIVER=gs_usb
E: ID_VENDOR_FROM_DATABASE=OpenMoko, Inc.
E: ID_MODEL_FROM_DATABASE=Geschwister Schneider CAN adapter
E: ID_MM_CANDIDATE=1
E: ID_PATH=platform-3f980000.usb-usb-0:1.2.3:1.0
E: ID_PATH_TAG=platform-3f980000_usb-usb-0_1_2_3_1_0
E: ID_NET_DRIVER=gs_usb
E: SYSTEMD_ALIAS=/sys/subsystem/net/devices/can0
E: TAGS=:systemd:
E: CURRENT_TAGS=:systemd:
```

```
udevadm info -q all -a /sys/class/net/can0

Udevadm info starts with the device specified by the devpath and then
walks up the chain of parent devices. It prints for every device
found, all possible attributes in the udev rules key format.
A rule to match, can be composed by the attributes of the device
and the attributes from one single parent device.

  looking at device '/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2.3/1-1.2.3:1.0/net/can0':
    KERNEL=="can0"
    SUBSYSTEM=="net"
    DRIVER==""
    ATTR{addr_assign_type}=="0"
    ATTR{addr_len}=="0"
    ATTR{address}==""
    ATTR{broadcast}==""
    ATTR{carrier}=="1"
    ATTR{carrier_changes}=="1"
    ATTR{carrier_down_count}=="0"
    ATTR{carrier_up_count}=="1"
    ATTR{dev_id}=="0x0"
    ATTR{dev_port}=="0"
    ATTR{dormant}=="0"
    ATTR{flags}=="0x40081"
    ATTR{gro_flush_timeout}=="0"
    ATTR{ifalias}==""
    ATTR{ifindex}=="3"
    ATTR{iflink}=="3"
    ATTR{link_mode}=="0"
    ATTR{mtu}=="16"
    ATTR{napi_defer_hard_irqs}=="0"
    ATTR{netdev_group}=="0"
    ATTR{operstate}=="up"
    ATTR{power/control}=="auto"
    ATTR{power/runtime_active_time}=="0"
    ATTR{power/runtime_status}=="unsupported"
    ATTR{power/runtime_suspended_time}=="0"
    ATTR{proto_down}=="0"
    ATTR{queues/rx-0/rps_cpus}=="0"
    ATTR{queues/rx-0/rps_flow_cnt}=="0"
    ATTR{queues/tx-0/byte_queue_limits/hold_time}=="1000"
    ATTR{queues/tx-0/byte_queue_limits/inflight}=="0"
    ATTR{queues/tx-0/byte_queue_limits/limit}=="0"
    ATTR{queues/tx-0/byte_queue_limits/limit_max}=="1879048192"
    ATTR{queues/tx-0/byte_queue_limits/limit_min}=="0"
    ATTR{queues/tx-0/tx_maxrate}=="0"
    ATTR{queues/tx-0/tx_timeout}=="0"
    ATTR{queues/tx-0/xps_rxqs}=="0"
    ATTR{statistics/collisions}=="0"
    ATTR{statistics/multicast}=="0"
    ATTR{statistics/rx_bytes}=="3148904"
    ATTR{statistics/rx_compressed}=="0"
    ATTR{statistics/rx_crc_errors}=="0"
    ATTR{statistics/rx_dropped}=="23"
    ATTR{statistics/rx_errors}=="0"
    ATTR{statistics/rx_fifo_errors}=="0"
    ATTR{statistics/rx_frame_errors}=="0"
    ATTR{statistics/rx_length_errors}=="0"
    ATTR{statistics/rx_missed_errors}=="0"
    ATTR{statistics/rx_nohandler}=="0"
    ATTR{statistics/rx_over_errors}=="0"
    ATTR{statistics/rx_packets}=="393613"
    ATTR{statistics/tx_aborted_errors}=="0"
    ATTR{statistics/tx_bytes}=="78688"
    ATTR{statistics/tx_carrier_errors}=="0"
    ATTR{statistics/tx_compressed}=="0"
    ATTR{statistics/tx_dropped}=="0"
    ATTR{statistics/tx_errors}=="0"
    ATTR{statistics/tx_fifo_errors}=="0"
    ATTR{statistics/tx_heartbeat_errors}=="0"
    ATTR{statistics/tx_packets}=="9836"
    ATTR{statistics/tx_window_errors}=="0"
    ATTR{testing}=="0"
    ATTR{threaded}=="0"
    ATTR{tx_queue_len}=="10"

```

2. Create `/etc/udev/rules.d/99-can-adapters.rules:`
```
SUBSYSTEM=="net", ATTRS{idVendor}=="1d50", ATTRS{serial}=="002A002D4730511420303650", NAME="grid-charger-1"
```

You can rename multiple charges within the same file, simply add one new line for each charger :).

The Attributes that need to be changed are:
- idVendor: found using `lsusb -v | grep -i idVendor` which returns something like `idVendor           0x1d50 OpenMoko, Inc.`
- serial: found using `lsusb -v | grep -i iSerial` which returns something like `  iSerial                 3 002A002D4730511420303650` (note the space between the latest 2 numbers - only the last number is the serial number !)
- NAME: your name of choice (e.g. `grid-charger-0`, `diesel-charger-0`, ...)


3. Apply without Reboot
   On some systems it might be sufficient to run
   ```
   udevadm control --reload-rules && udevadm trigger
   ```

   However on Systemd-based Systems (Ubuntu, Debian, Fedora, ...) this will not be sufficient.
   Instead the associated Systemd Service needs to be restarted
   ```
   systemctl restart systemd-udev-trigger.service
   ```

3. Reboot

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
