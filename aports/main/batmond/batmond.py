#!/usr/bin/python3
# -*- python -*-
import os
import time

class Test:
    def read(m, s):
        f = open(s, "r")
        r = f.read()
        f.close()
        return r

class Battery(Test):
    hotkey = "b"
    name = "Battery"
    path = "/sys/class/power_supply"

    def percent(m, v):
        u = 0.0387-(1.4523*(3.7835-v))
        if u < 0:
            return 0
        return (0.1966+math.sqrt(u))*100

    def run(m):
        try:
            # On new kernels
            volt = int(m.read(m.path+"/rx51-battery/voltage_now"))
        except:
            # On 4.1
            volt = int(m.read(m.path+"/n900-battery/voltage_now"))
        volt /= 1000000.
        perc = m.percent(volt)
        
        status = m.read(m.path+"/bq24150a-0/status")[:-1]
        current = int(m.read(m.path+"/bq24150a-0/charge_current"))
        limit = int(m.read(m.path+"/bq24150a-0/current_limit"))

        try:
            charge_now = int(m.read(m.path+"/bq27200-0/charge_now")) / 1000
            charge_full = int(m.read(m.path+"/bq27200-0/charge_full")) / 1000
            #perc2 = int(m.read(m.path+"/bq27200-0/capacity"))
            # Buggy in v4.4
            perc2 = int((charge_now * 100.) / charge_full)
        except:
            # bq27x00-battery 2-0055: battery is not calibrated! ignoring capacity values
            charge_now = 0
            charge_full = 0
            perc2 = 0
        charge_design = int(m.read(m.path+"/bq27200-0/charge_full_design")) / 1000
        volt2 = int(m.read(m.path+"/bq27200-0/voltage_now")) / 1000000.
        current2 = int(m.read(m.path+"/bq27200-0/current_now")) / 1000.

        # http://www.buchmann.ca/Chap9-page3.asp
        # 0.49 ohm is between "poor" and "fail".
        # 0.15 ohm is between "excelent" and "good".
        # at 3.6V.
        resistance = 0.43
        volt3 = volt + (current2 / 1000. * resistance)
        perc3 = m.percent(volt3)

        print("Battery %.2fV %.2fV %.2fV" % (volt, volt2, volt3), \
              "%d%% %d%% %d%%" % (int(perc), int(perc3), perc2), \
              "%d/%d mAh" % (charge_now, charge_full), \
              status, \
              "%d/%d/%d mA" % (int(-current2), current, limit) )
        m.perc = perc
        m.perc2 = perc2
        m.perc3 = perc3
        m.volt = volt
        m.volt2 = volt2
        m.volt3 = volt3
        m.status = status
        m.current = -current2
        m.max_battery_current = current
        m.charger_limit = limit

    def summary(m):
        if m.volt < 3.3:
            return "critical"
        if m.status == "Charging":
            if m.volt2 > 4.100 and m.current > -35 and m.current < 40:
                return "full"
            if m.current > 0:
                return "charging"
            return "discharging"
        if m.perc3 < 30:
            return "low"
        return "ok"

    def fast_charge(m, limit=1800):
        sy("echo %d > /sys/class/power_supply/bq24150a-0/current_limit" % limit)
        print("Fast charge on, %d mA" % limit)

#os.system("setterm -blank 1")

bat = Battery()
while 1:
    bat.run()
    s = bat.summary()
# Battery 2.82V 2.90V 3.04V 0% 0% 5% 91/1797 mAh Not charging -511/650/100 mA
    if bat.volt < 2.95:
        os.system("/sbin/shutdown -h now")
        s = "critical"
    # When transitioning from charger to battery discharge, ampermeter
    # lags behind, and produces < 3.55V for a while
    if bat.volt3 < 3.15:
        os.system("/sbin/shutdown -h now")
        s = "critical"
    time.sleep(30)
