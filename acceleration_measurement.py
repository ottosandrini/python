import os
import subprocess
import tempfile
import time

def get_i2c(reg: str):
    os.system("i2cget 1 0x68 " + reg)

if __name__ == "__main__":

    while True:

        get_i2c('0x3B')

        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(['echo'], stdout=tempf)
            proc.wait()
            tempf.seek(0)
            bytes_arr = tempf.read()
            print(bytes_arr[0])

        time.sleep(0.05)