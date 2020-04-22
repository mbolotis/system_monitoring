import smtplib, ssl
import time
import threading
import psutil
import os
from getpass import getpass


def cpu_usage():
    x = psutil.cpu_percent(interval=1, percpu=True)

    return x[0]


def ram_usage():
    r_usage = psutil.virtual_memory()[2]

    return r_usage


def disk_space():
    d_usage = psutil.disk_usage('/')[3]  # free space

    return d_usage


def service_status(my_service_name):
    '''
    :return: The current status for the given service
    '''
    try:
        y = psutil.win_service_get(my_service_name)
        r_value = y.status()
    except psutil.NoSuchProcess:
        print("No such service \n")
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
    '''
    In Incident mode, it recalculates component value until
        either exceeds given secs_threshold and returns 1 (=Incident)
        or it does not exceed given secs_threshold and returns 0 (=Clear)
    In Consolidation mode (meaning that is has already sent Incident notification),
    it recalculates component value until becoming less than given threshold and returns 0 (=Clear)
    '''
    temp_value = recalculate_value(args[0])
    if args[1] == 0:  # Incident mode
        while True:
            if temp_value < args[3]:
                break
            elif time.time() - args[2] > secs_threshold:
                return 1  # critical incident

            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear
    else:  # Consolidation mode
        while temp_value > args[3]:
            time.sleep(1)
            temp_value = recalculate_value(args[0])

        return 0  # clear


def ram_calculation():
    '''
    This function executes by RAM thread and monitors RAM space every 1 second.
    When RAM uses more resources than given ram_threshold, it enters in the critical path for incident and if this fact continues for more than
    the given secs_threshold it sends an Incident email end enters in the critical path for consolidation, and recalculates the value
    until becoming less than ram_threshold and sends a Clear email.
    '''
    consolidation = False
    ram_value = recalculate_value(types[1])
    if ram_value > ram_threshold:
        now_time = time.time()
        call = critical_path(types[1], 0, now_time, ram_threshold)  # 0 = Incident, 1 = consolidation

        # Consolidation stage
        if call == 1:
            consolidation = True
            email_execution(ram_template_incident)
            '''SEND INCIDENT EMAIL'''
        while call == 1:
            call = critical_path(types[1], 1, None, ram_threshold)  # recalculates values until becoming clear

        if consolidation:
            email_execution(ram_template_clear)
            '''SEND CLEAR EMAIL'''
        # End of consolidation stage

    time.sleep(1)
    ram_calculation()


def cpu_calculation():
    '''
    This function executes by CPU thread and monitors CPU usage every 1 second.
    When CPU uses more resources than given cpu__threshold, it enters in the critical path for incident and if this fact continues for more than
    the given secs_threshold it sends an Incident email end enters in the critical path for consolidation, and recalculates the value
    until becoming less than cpu__threshold and sends a Clear email.
    '''
    consolidation = False
    cpu_value = recalculate_value(types[0])
    if cpu_value > ram_threshold:
        now_time = time.time()
        call = critical_path(types[0], 0, now_time, cpu_threshold)  # 0 = Incident, 1 = consolidation

        # Consolidation stage
        if call == 1:
            consolidation = True
            email_execution(cpu_template_incident)
            '''SEND INCIDENT EMAIL'''
        while call == 1:
            call = critical_path(types[0], 1, None, cpu_threshold)  # recalculates values until becoming clear

        if consolidation:
            email_execution(cpu_template_clear)
            '''SEND CLEAR EMAIL'''
        # End of consolidation stage

    time.sleep(1)
    cpu_calculation()


def disk_calculation():
    '''
    This function executes by disk thread and monitors disk space every 1 second.
    When disk uses more resources than given disk_threshold, it enters in the critical path for incident and if this fact continues for more than
    the given secs_threshold it sends an Incident email end enters in the critical path for consolidation, and recalculates the value
    until becoming less than disk_threshold and sends a Clear email.
    '''
    consolidation = False
    disk_value = recalculate_value(types[2])
    if disk_value > disk_threshold:
        now_time = time.time()
        call = critical_path(types[2], 0, now_time, disk_threshold)  # 0 = Incident, 1 = consolidation

        # Consolidation stage
        if call == 1:
            consolidation = True
            email_execution(disk_template_incident)
            '''SEND INCIDENT EMAIL'''
        while call == 1:
            call = critical_path(types[2], 1, None, disk_threshold)  # recalculates values until becoming clear

        if consolidation:
            email_execution(disk_template_clear)
            '''SEND CLEAR EMAIL'''
        # End of consolidation stage

    time.sleep(1)
    disk_calculation()


def service_check(my_service_name):
    '''
    Checking the status for a given Windows Service
        if the value is not equal to the proper values
            sends an Incident email and enters in consolidation stage until the value becomes equal to the proper_value
        else
            re-checking the values after 1 second
    '''
    consolidation = False
    temp_value = service_status(my_service_name)

    if temp_value != service_prop_status:
        start_time = time.time()
        while temp_value != service_prop_status:
            temp_value = service_status(my_service_name)
            if time.time() - start_time < secs_threshold:
                consolidation = True
                email_execution(service_template_incident)
                break

    # consolidation stage
    if temp_value != service_prop_status and consolidation:
        while temp_value != service_prop_status:
            time.sleep(1)
            temp_value = service_status(my_service_name)

        email_execution(service_template_clear)

    time.sleep(1)
    service_check(service_name)


def email_execution(template):
    try:
        print("Starting to send email", time.ctime(time.time()))
        server_ssl.login(sender, passw)
        server_ssl.sendmail(sender, receiver_1, template)
        print("Email sent '{}' {}".format(template, time.ctime(time.time())))
    except smtplib.SMTPDataError:
        time.sleep(1)
        email_execution(template)
    except smtplib.SMTPAuthenticationError:
        time.sleep(1)
        email_execution(template)


if __name__ == '__main__':
    os.system("pip install psutil==5.6.7")

    # User configuration starts
    confirmed = "N"
    while confirmed != "Y" and confirmed != "y":
        try:
            server_name = str(input("Please define a name for this system : "))
            cpu_threshold = float(input("Give me CPU threshold percentage %: "))
            ram_threshold = float(input("Give me RAM threshold percentage %: "))
            disk_threshold = float(input("Give me Disk threshold percentage %: "))
            secs_threshold = int(input("After how many seconds of exceeding, would you like to be notified? "))

            if 1 <= cpu_threshold < 100 and 1 <= ram_threshold < 100 and 1 <= disk_threshold < 100:
                confirmed = input("Do you want to confirm the above configuration ? [Y/N] : ")
            else:
                print("Percentages should be between 1 and 100!")
                confirmed = "N"
        except ValueError:
            print("Give me numbers!")

    types = ("CPU", "RAM", "DISK")

    add_service = str(input('Do you want to monitor a Windows Service ? [Y/N] : '))
    service_name = None

    while add_service == "Y" or add_service == "y":
        service_name_temp = str(input("Give me a service to monitor : "))  # MongoDB
        try:
            psutil.win_service_get(service_name_temp)
            service_name = service_name_temp
            service_prop_status = "running"
            add_service = "N"
        except psutil.NoSuchProcess:
            print("No such service \n")
            add_service = str(input("Do you want to monitor a service ? [Y/N] : "))
        except AttributeError:
            add_service = "N"
            print("This functionality is available only on Windows OS")

    # Email configuration starts

    login_completed = False
    while not login_completed:
        sender = input("Give me the email account from which the notification emails will be sent : ")
        passw = getpass("Password : ")
        try:
            port = 465
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", port)
            server_ssl.login(sender, passw)
            print("you have logged in!")
            login_completed = True
        except smtplib.SMTPAuthenticationError:
            login_failure_reasons = """
            You did not manage to login to this email for 1 (or more) of the following reasons:\n
            - You gave invalid credentials
            - You do not have enabled the following value  https://myaccount.google.com/lesssecureapps?pli=1
            - You are using two-factor authentication to login to this email account 
            """
            print(login_failure_reasons)

    receiver_1 = input("Give me the email address that will be notified : ")
    receiver_2 = input("Confirm the receiver address : ")
    while receiver_1 != receiver_2:
        receiver_1 = input("Give me the email address that will be notified : ")
        receiver_2 = input("Confirm the receiver address : ")

    # Define the email templates
    cpu_template_incident = 'Subject: Monitor Notification: INCIDENT Server {} {} Usage\n\nServer {}, {} using more than {}% of its resources for more than {} seconds!'.format(server_name, types[0], server_name, types[0], int(cpu_threshold), secs_threshold)
    ram_template_incident = 'Subject: Monitor Notification: INCIDENT Server {} {} Usage\n\nServer {}, {} using more than {}% of its resources for more than {} seconds!'.format(server_name, types[1], server_name, types[1], int(ram_threshold), secs_threshold)
    disk_template_incident = 'Subject: Monitor Notification: INCIDENT Server {} {} Usage\n\nServer {}, {} using more than {}% of its resources for more than {} seconds!'.format(server_name, types[2], server_name, types[2], int(disk_threshold), secs_threshold)
    service_template_incident = 'Subject: Monitor Notification: INCIDENT Server {} Service {} has stopped\n\nServer {} Service {} has stopped!'.format(server_name, service_name, server_name, service_name)

    cpu_template_clear = 'Subject: Monitor Notification: CLEAR Server {} {} Usage\n\nServer {}, {} is not using more than {}% of its resources, anymore!'.format(server_name, types[0], server_name, types[0], int(cpu_threshold))
    ram_template_clear = 'Subject: Monitor Notification: CLEAR Server {} {} Usage\n\nServer {}, {} is not using more than {}% of its resources, anymore!'.format(server_name, types[1], server_name, types[1], int(ram_threshold))
    disk_template_clear = 'Subject: Monitor Notification: CLEAR Server {} {} Usage\n\nServer {}, {} is not using more than {}% of its resources, anymore!'.format(server_name, types[2], server_name, types[2], int(disk_threshold))
    service_template_clear = 'Subject: Monitor Notification: CLEAR Server {} Service {} is running\n\nServer {} Service {} is running!'.format(server_name, service_name, server_name, service_name)
    # End email configuration

    print("Program has started to run")

    if service_name is not None:
        service_thread = threading.Thread(target=service_check, args=(service_name,))
        service_thread.start()

    cpu_thread = threading.Thread(target=cpu_calculation, args=())
    ram_thread = threading.Thread(target=ram_calculation, args=())
    disk_thread = threading.Thread(target=disk_calculation, args=())

    cpu_thread.start()
    ram_thread.start()
    disk_thread.start()
