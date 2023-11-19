# -- GNU PPLv3 --

import requests as rq
import time
import subprocess as sp
import json
import threading


def getPIU():
    """
    asks which gpio pin the user wants, activates it, sets it to output and returns it
    """

    want=input("Which gpio pin would you like to use: (e.g: 15)\n") or "15"
    
    command = "ls /sys/class/gpio/ | grep gpio" + want
    test = str(sp.run(command, capture_output=True, shell=True).stdout)
    teststring = "gpio" + want

    if teststring in test:
        command = "echo out > /sys/class/gpio/gpio" +want+ "/direction"
        sp.call(command, shell=True)

    else:
        command = "echo " + want + " > /sys/class/gpio/export"
        sp.call(command, shell=True)
        time.sleep(2)
        command = "echo out > /sys/class/gpio/gpio" + want + "/direction"
        sp.call(command, shell=True)
    
    return want

def get_last_update_id():
    try:
        with open('last_update_id.txt', 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        f = open("last_update_id.txt", "x")
        return 0

def save_last_update_id(lui):
    with open('last_update_id.txt', 'w') as file:
        file.write(str(lui))

class telbot():
    """
    telegramm bot class:
        status=True --> active
        status=False --> inactive
        change status using activate() or deactivate()
        
    """
    def __init__(self, name, api_key, pin):
        self.name=name
        self.api_key=api_key
        self.pin=pin
        self.on = "echo 1 > /sys/class/gpio/gpio" + pin + "/value"
        self.off = "echo 0 > /sys/class/gpio/gpio" + pin + "/value"
        self.last_update_id=get_last_update_id()

    def blink(self, speed):
        time.sleep(speed)
        sp.call(self.on, shell=True)
        time.sleep(speed)
        sp.call(self.off, shell=True)
        time.sleep(speed)
        sp.call(self.on, shell=True)
        time.sleep(speed)
        sp.call(self.off, shell=True)
    updates=[]
    def request(self, method, param):
        url = "https://api.telegram.org/bot" + self.api_key + "/" + method + param
        #print(F"making a request @ {url}")
        resp=rq.get(url)
        #print(resp.status_code)
        return resp
    def methods():
        print("The available request methods are:")
        print("getME")
        print("sendMessage:")
        print("")
    

    """
    last_update_id is needed to avoid responding to all messages. They need to be stored in a file
    for when the programm stops running
    """
    

    def update(self):   # makes a getUpdate request
        updata = self.request("getUpdates", F"?offset={self.last_update_id + 1}")
        updata = json.loads(updata.text)
        return updata

    def incoming(self, trfa): # checks data from update()
        data = self.update()
        #check if data is empty
        if data['result']!=[]:
            for update in data['result']:
                #print(F"last_updat_id:       {self.last_update_id}")
                current_update_id = int(update['update_id'])
                #print(F"current_update_id:   {current_update_id}")
                if current_update_id > self.last_update_id:
                    #print(F"handling update with id: {update['update_id']}")
                    self.updates.clear()
                    self.updates.append(update)
                    self.respond(update, trfa)
                self.last_update_id = current_update_id


    
    def respond(self, thing, TF):   #does something on message

        # first get values that are important for a response
        chat_id = thing['message']['chat']['id']
        message_text = thing['message']['text'].lower()

        # check the pin value
        pinadd = "/sys/class/gpio/gpio" + self.pin + "/value"
        gpio_val = int(sp.run(['cat', pinadd], capture_output=True, text=True).stdout)

        # message logic
        if message_text=="on":
            if gpio_val==1:
                answer="LED already on!"
            else:
                answer="turning LED on"
                sp.call(self.on, shell=True)
        elif message_text=="off":
            if gpio_val==0:
                answer="LED already off"
            else:
                answer="turning LED off"
                sp.call(self.off, shell=True)
        elif message_text=="blink":
            answer=";)"
            self.blink(0.2)
        elif message_text=="clear":
            answer="what?"
        elif message_text=="s":
            TF[0]=False
            myin="s"
            answer="stopping..."
        else:
            answer="Invalid command"
        # sending the sendMessage - request with the paramters answer & chat_id
        self.request("sendMessage", F"?chat_id={chat_id}&text={answer}")

        # saving the last update_id to avoid chaos 
        save_last_update_id(self.last_update_id)


#  defining the two functions for the two threads:      
def ask_input(myin, tf):
    while myin != "s":
        myin = input("Enter 's' to stop! \n")
    tf[0] = False

def loop(tf, bot):
    while tf[0] == True:
        #get_last_update_id(bot.last_update_id)
        bot.incoming(tf)
    


#####  "main function" #####

#  asking which gpio pin should be used
PIU = getPIU();
myin=""
running=[True]

def gettoken():
    try:
        with open('token.txt', 'r') as file:
            return str(file.read().strip())
    except:
        print("Failed to get token!")
token=gettoken()

#  initializing the telbot instance Raspitin, loading the last update id and updating
Raspitin = telbot("RaspitinLED_bot", token, PIU)
#get_last_update_id(Raspitin.last_update_id)
Raspitin.blink(0.5)
Raspitin.incoming(running)


# Create threads
input_thread = threading.Thread(target=ask_input, args=(myin, running,))
bot_thread = threading.Thread(target=loop, args=(running, Raspitin))

# Start threads
input_thread.start()
bot_thread.start()

# check if loop finished before input_thread
#if bot_thread.is_alive()==False:
#    input_thread._stop()

# Wait for both threads to finish
input_thread.join()
bot_thread.join()


save_last_update_id(Raspitin.last_update_id)
sp.call("echo 0 > /sys/class/gpio/gpio15/value", shell=True)
