import time
from multiprocessing import Process
import threading
import psutil
import os
try:
    import httplib
except:
    import http.client as httplib


def cpu_usage():
    x = psutil.cpu_percent(interval=1, percpu=True)
    #print(type(x))

    return x[0]


def ram_usage():
    r_usage = psutil.virtual_memory()[2]
    #print('memory % used:', psutil.virtual_memory()[2])

    return r_usage


def disk_space():
    d_usage = psutil.disk_usage('/')[3]
    #print("Free Disk Space % : ", psutil.disk_usage('/')[3])

    return d_usage


def service_status(my_service_name):
    try:
        y = psutil.win_service_get(my_service_name)
        print("Binary path : ", y.binpath())
        print("Service Status : ", y.status())
        r_value = y.status()
    except:
        print("No such service")
        r_value = "No such service"

    return r_value


def critical_path(*args):
    temp_value = recalculate_value(args[1])
    if args[1] == 0:
        while True:
            if temp_value < 80:
                break
            elif time.time() - args[2] > secs_threshold:
                return 1  # critical incident

            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear
    else:
        while temp_value > cpu_threshold:
            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear


def recalculate_value(my_type):
    if my_type == types[0]:
        temp_value = cpu_usage()
    elif my_type == types[1]:
        temp_value = ram_usage()
    else:
        temp_value = disk_space()

    return temp_value


if __name__ == '__main__':
    types = ("cpu", "ram", "disk")
    service_name = 'Dnscache'
    cpu = cpu_usage()
    ram = ram_usage()
    disk = disk_space()
    service = service_status(service_name)

    secs_threshold = 20

    cpu_threshold = 80.0
    ram_threshold = 50.0
    disk_threshold = 80.0
    service_prop_status = "running"

    t1 = threading.Thread()

    while True:
        if cpu > cpu_threshold:
            now_time = time.time()
            call = critical_path(types[0], 0, now_time)  # 0 = Incident, 1 = consolidation
            while call == 1:
                call = critical_path(types[0], 1)
            print("Poli cpu", time.time())
        if ram > ram_threshold:
            now_time = time.time()
            call = critical_path(types[1], 0, now_time)  # 0 = Incident, 1 = consolidation
            while call == 1:
                call = critical_path(types[1], 1)
            print("Poli ram", time.time())
        if disk > disk_threshold:
            now_time = time.time()
            call = critical_path(types[2], 0, now_time)  # 0 = Incident, 1 = consolidation
            while call == 1:
                call = critical_path(types[2], 1)
            print("Poli disk", time.time())

        if service != service_prop_status:
            print("Service down")

        cpu = recalculate_value(types[0])
        ram = recalculate_value(types[1])
        disk = recalculate_value(types[2])

        time.sleep(2)
