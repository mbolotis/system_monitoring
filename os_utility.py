import time
import threading
import psutil
import os
try:
    import httplib
except:
    import http.client as httplib


def cpu_usage():
    x = psutil.cpu_percent(interval=1, percpu=True)
    print(type(x))

    return x[0]

def ram_usage():
    r_usage = psutil.virtual_memory()[2]
    print('memory % used:', psutil.virtual_memory()[2])

    return r_usage


def disk_space():
    d_usage = psutil.disk_usage('/')[3]
    print("Free Disk Space % : ", psutil.disk_usage('/')[3])

    return d_usage


def service_status(service_name):
    try:
        y = psutil.win_service_get(service_name)
        print("Binary path : ", y.binpath())
        print("Service Status : ", y.status())
        r_value = y.status()
    except:
        print("No such service")
        r_value = "No such service"

    return r_value


if __name__ == '__main__':
    service_name = 'Dnscache'
    cpu = cpu_usage()
    ram = ram_usage()
    disk = disk_space()
    service = service_status(service_name)

    cpu_threshold = 80
    ram_threshold = 50
    disk_threshold = 80
    service_prop_status = "running"

    conditions = ("Clear", "Incident")

    t1 = threading.Thread()

    while True:
        if cpu > cpu_threshold:
            print("Poli cpu")
        if ram > ram_threshold:
            print("Poli ram")
        if disk > disk_threshold:
            print("Poli disk")
        if service != service_prop_status:
            print("Service down")
