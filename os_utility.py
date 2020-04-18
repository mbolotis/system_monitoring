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


def recalculate_value(my_type):
    if my_type == types[0]:
        temp_value = cpu_usage()
    elif my_type == types[1]:
        temp_value = ram_usage()
    else:
        temp_value = disk_space()

    return temp_value


def critical_path(*args):
    temp_value = recalculate_value(types[1])
    if args[1] == 0:  # Incident mode
        while True:
            if temp_value < args[3]:
                break
            elif time.time() - args[2] > secs_threshold:
                return 1  # critical incident

            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear
    else:
        while temp_value > args[3]:
            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear


def ram_calculation():
    consolidation = False
    ram_value = recalculate_value(types[1])
    if ram_value > ram_threshold:
        now_time = time.time()
        call = critical_path(types[1], 0, now_time, ram_threshold)  # 0 = Incident, 1 = consolidation

        # Consolidation stage
        if call == 1:
            consolidation = True
            print("SEND RAM INCIDENT EMAIL")
            '''SEND INCIDENT EMAIL'''
        while call == 1:
            call = critical_path(types[1], 1, None, ram_threshold)  # recalculates values until becoming clear

        if consolidation:
            print("SEND RAM CLEAR EMAIL")
            '''SEND CLEAR EMAIL'''
        # End of consolidation stage

    print("Ram usage !", ram_value, time.time())
    time.sleep(1)
    ram_calculation()


def cpu_calculation():
    consolidation = False
    cpu_value = recalculate_value(types[0])
    if cpu_value > ram_threshold:
        now_time = time.time()
        call = critical_path(types[0], 0, now_time, cpu_threshold)  # 0 = Incident, 1 = consolidation

        # Consolidation stage
        if call == 1:
            consolidation = True
            print("SEND CPU INCIDENT EMAIL")
            '''SEND INCIDENT EMAIL'''
        while call == 1:
            call = critical_path(types[0], 1, None, cpu_threshold)  # recalculates values until becoming clear

        if consolidation:
            print("SEND CPU CLEAR EMAIL")
            '''SEND CLEAR EMAIL'''
        # End of consolidation stage

    print("Cpu usage !", cpu_value, time.time())
    time.sleep(1)
    cpu_calculation()


if __name__ == '__main__':

    service_name = 'Dnscache'
    service = service_status(service_name)
    service_prop_status = "running"

    types = ("cpu", "ram", "disk")

    secs_threshold = 10
    cpu_threshold = 80.0
    ram_threshold = 45.0
    disk_threshold = 80.0

    cpu_thread = threading.Thread(target=cpu_calculation, args=())
    ram_thread = threading.Thread(target=ram_calculation, args=())

    cpu_thread.start()
    ram_thread.start()

    while True:
        time.sleep(10)


'''    ram_thread = threading.Thread(target=ram_calculation(), daemon=True)
    cpu_thread = threading.Thread(target=cpu_calculation(), daemon=True)

    ram_thread.start()
    cpu_thread.start()'''

'''        if not ram_thread.is_alive():
            ram_thread.start()
            #ram_thread.join(timeout=2)
        if not cpu_thread.is_alive():
            cpu_thread.start()
            #cpu_thread.join(timeout=2)

        ram_thread.join(timeout=2)
        cpu_thread.join(timeout=2)'''
        #time.sleep(2)

        #Process(target=ram_calculation()).start()
        #Process(target=cpu_calculation()).start()
        #ram_calculation()
'''        cpu = recalculate_value(types[0])
        #ram = recalculate_value(types[1])
        disk = recalculate_value(types[2])

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
            print("Service down")'''


# sxolia, threading, emails