#!/bin/env python3
"""
A simple PID-regulator to control the cooling fan
via the PWM pin of the RPi.
The regulator will try to keep the temperature
at the desired t_set centigrades.
"""
from gpiozero import CPUTemperature, PWMOutputDevice
from time import sleep

#==Adjustable params===
t_max = 80.0
t_set = 65.0 # Desired set-point for CPU temperature in celcius
PIN_PWM = 18
PWM_MIN_HZ = 10 # Adjust to frequency with lowest fan whine
PWM_MIN_DC = 0.4 # Set this to the lowest duty cycle that is able to start fan
PWM_MAX_DC = 1.0 # continuously on
#======================

cpu = CPUTemperature()
fanPwm = PWMOutputDevice(pin=PIN_PWM)
fanPwm.frequency = PWM_MIN_HZ 
fanPwm.value = 0

Kp     = 1/(1*(t_max-t_set)) # Coefficient for P term
T_iter = 0.5 # PID loop time step
Ti     = 10*T_iter # Integration time for I-term
Td     = 2*T_iter # Derivative time for D-term
Nint   = int( Ti / T_iter )
Nder   = int( Td / T_iter )
Nmax   = max(Nint, Nder)

errors = [] # for keeping Nmax last error terms. errors[0] is oldest term

def calc_error(temp_meas):
    """ Update error relative to t_set and store in errors for integration & derivation """
    if len(errors) == Nmax:
        errors.pop(0)
    err = temp_meas - t_set
    errors.append(err)

def clip_pwm(pwm_val):
    """ Clamp PID's output to 0 below PWM_MIN_DC (i.e. stop the fan when reaching set point),
        and to 1 above PWM_MAX_DC.
    """
    if pwm_val < PWM_MIN_DC:
        return 0
    elif pwm_val > PWM_MAX_DC:
        return 1
    else:
        return pwm_val
    
def get_integration_term():
    """ Integration term of PID """
    L = len(errors)
    N = min(L, Nint)
    I = 1/Ti*sum(errors[L-N:])
    return I

def get_diff_term():
    """ Derivative term of PID """
    L = len(errors)
    N = min(L, Nder)
    D = Td*( errors[-1] - errors[-1+(L-N)] )
    return D

try:
    while True:
        temp = cpu.temperature
        calc_error( temp )
        # output = Proportional + Integral + Derivative 
        U = Kp*(errors[-1] + get_integration_term() + get_diff_term())
        #print("U-value=%f" % U)
        fanPwm.value = clip_pwm( U )
        sleep(T_iter)
except KeyboardInterrupt:
    print("Ctrl-C pressed. Exiting.")
    fanPwm.value = 0
