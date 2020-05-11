# PiFanController
Regulate the RPM of your Raspberry Pi's cooling fan to reduce noise, 
with a chosen temperature set-point.
Connect fan with circuit similar to [RPi_fan_ctrl_schem.png](https://github.com/hekland/PiFanController/blob/master/RPi_fan_ctrl_schem.png), using some standard
npn-transistor like 2N2222.
Test how the fan responds by using the Python command line:

```
from gpiozero import PWMOutputDevice
fanPwm = PWMOutputDevice(pin=18)
fanPwm.frequency = 10 
fanPwm.value = 0
fanPwm.value = 0.4
```
Set value first to 0, then to some low number and see how low of a duty
cycle that still can start the fan. The frequency can be adjusted to 
a value which makes less noise. Typically higher frequencies make the
fan hum more.

To install as a service on the Pi:
1. Adjust parameters in piFanCtrl.py and copy it to /usr/local/bin/
2. Copy pifanctrl.service to /lib/systemd/system/
3. Run `sudo systemctl enable pifanctrl.service` to enable at boot
4. Run `sudo systemctl start pifanctrl.service` to start service
5. Run `sudo systemctl status pifanctrl.service` to check service
6. Test by running `stress -c 4` or something similar and verify that the
   fan spins up when CPU temp rises above the t_set in piFanCtrl.py
