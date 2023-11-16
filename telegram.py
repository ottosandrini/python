import requests as rq
import time
import subprocess as sp
import json
import threading


def getPIU():
    """
    asks which gpio pin the user wants, activates it, sets it to output and returns it
    could implement:  --check if already active
    """
    want=input("Which gpio pin would you like to use: (e.g: 15)\n") or "15"
    command = "echo " + want + " > /sys/class/gpio/export"
    sp.call(command, shell=True)
    #print(F"gpio pin {want} wurde aktiviert")
    # activate the pin as out
    command = "echo out > /sys/class/gpio/gpio" + want + "/direction"
    sp.call(command, shell=True)
    #print(F"gpio pin {want} was set to output")

    return want

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
        self.last_update_id=0

    def blink(self):
        print("blinking LED in 2 seconds")
        time.sleep(2)
        sp.call(self.on, shell=True)
        time.sleep(0.5)
        sp.call(self.off, shell=True)
        time.sleep(0.5)
        sp.call(self.on, shell=True)
        time.sleep(0.5)
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
    def load_last_update_id(self):
        try:
            with open('last_update_id.txt', 'r') as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError):
            # Return 0 if the file doesn't exist or the value is invalid
           return 0

    def save_last_update_id(self):
        with open('last_update_id.txt', 'w') as file:
            file.write(str(self.last_update_id))
    

    def update(self):   # makes a getUpdate request
        updata = self.request("getUpdates", F"?offset={self.last_update_id + 1}")
        updata = json.loads(updata.text)
        return updata

    def incoming(self, trfa): # checks data from update()
        data = self.update()
        #check if data is empty
        if data['result']!=[]:
            for update in data['result']:
                print(F"last_updat_id:       {self.last_update_id}")
                current_update_id = int(update['update_id'])
                print(F"current_update_id:   {current_update_id}")
                if current_update_id > self.last_update_id:
                    #print(F"handling update with id: {update['update_id']}")
                    self.updates.clear()
                    self.updates.append(update)
                    self.respond(update, trfa)
                self.last_update_id = current_update_id
                #self.save_last_update_id()


    
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
        elif message_text=="s":
            TF[0]=False
            answer="stopping..."
        else:
            answer="Invalid command"
        # sending the sendMessage - request with the paramters answer & chat_id
        self.request("sendMessage", F"?chat_id={chat_id}&text={answer}")

        # saving the last update_id to avoid chaos 
        self.save_last_update_id()


#  defining the two functions for the two threads:      

def ask_input(tf):
    myin=""
    while myin != "s":
        myin = input("Enter 's' to stop!")
    tf[0] = False

def loop(tf, bot):
    while tf[0] == True:
        bot.load_last_update_id()
        bot.incoming(tf)
    


#####  "main function" #####

#  asking which gpio pin should be used
PIU = getPIU();

running=[True]
#  initializing the telbot instance Raspitin, loading the last update id and updating
Raspitin = telbot("RaspitinLED_bot", "6439165721:AAFU3SHmxCVG-4qnQYV0MQuU0PH-Dt__9us", PIU)
Raspitin.load_last_update_id()
Raspitin.blink()
Raspitin.incoming(running)


# Create threads
input_thread = threading.Thread(target=ask_input, args=(running,))
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


Raspitin.save_last_update_id()
sp.call("echo 0 > /sys/class/gpio/gpio15/value", shell=True)
