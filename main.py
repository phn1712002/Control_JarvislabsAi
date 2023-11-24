import time, psutil, subprocess
from Tools.Gmail import sendEmail
from Tools.Json import loadJson
from jlclient import jarvisclient
from jlclient.jarvisclient import *
from  Tools.CMD import clearCMD

# Environment Variables
PATH_CONFIG = './config.json'
NAME_HOST = 'JarvislabsAi'
STR_SEND_STOP = 'PID STOP RUN!'

# Execute 'ps -ef' command on a Linux terminal
clearCMD()
processes = subprocess.run(['ps', '-ef'], stdout=subprocess.PIPE, text=True)
print(processes.stdout)  # Display the list of running processes

# Get configuration details
config = loadJson(PATH_CONFIG)

if not config == None:
    # Check for required keys in the configuration file
    keys_to_check = ['Jarvislabs', 'Gmail']
    if all(key in config for key in keys_to_check):
        config_jarvislabs = config['Jarvislabs']
        config_gmail = config['Gmail']
    else:
        raise RuntimeError("Error in configuration file")

run_check = True
while run_check:
    # Enter the PID to check
    print("-"*100)
    pid_to_check = input("Enter PID: ")
    print("-"*100)

    # Checking
    try:
        pid_to_check = int(pid_to_check)
    except ValueError:
        print("PID must be an integer.")
        clearCMD()
    else:
        run_check = False
        # Continuously monitor the entered PID
        while True:
            if psutil.pid_exists(pid_to_check):
                # Retrieve information about the process with the provided PID
                process = psutil.Process(pid_to_check)
                time_now = time.strftime("%d/%m/%Y, %H:%M:%S")
                str_print = f"PID {pid_to_check} is running at time {time_now}"
                print(str_print)
                try:
                    sendEmail(config_gmail['sender_email'], 
                            config_gmail['sender_password'], 
                            config_gmail['receiver_email'], 
                            NAME_HOST, 
                            str_print)
                except Exception as e:
                    print(f"Failed to send email: {e}")
                time.sleep(config_gmail['sleep_duration'])
            else:
                # If the provided PID is not running, pause the Jarvis instance
                try:
                    sendEmail(config_jarvislabs['sender_email'], 
                            config_jarvislabs['sender_password'], 
                            config_jarvislabs['receiver_email'], 
                            NAME_HOST, 
                            STR_SEND_STOP)
                    jarvisclient.token = config_jarvislabs['token']
                    jarvisclient.user_id = config_jarvislabs['user_id']
                    instance = User.get_instances()[0]
                    instance.pause()  # Pause Jarvis instance
                except Exception as e:
                    print(f"Failed to pause Jarvis instance: {e}")
                break  # Exit the loop