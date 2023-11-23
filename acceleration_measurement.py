import os
import subprocess
import tempfile
import time

def get_i2c(reg: str):
    os.system("i2cget -y 1 0x68 " + reg)

def read_i2c() -> bytes:
    with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(['echo'], stdout=tempf)
            proc.wait()
            tempf.seek(0)
            bytes_arr = tempf.read()
            return bytes_arr[0]

if __name__ == "__main__":

    while True:

        get_i2c('0x3B')

        x1 = read_i2c()

        # time.sleep(0.05)

        get_i2c('0x3C')

        x2 = read_i2c()

        final_value = (x1 << 8) | x2

        print(final_value)

        time.sleep(0.05)


        # get_i2c('0x3D')

        # y1 = read_i2c()

        # time.sleep(0.05)

        # get_i2c('0x3E')

        # y2 = read_i2c()

        # time.sleep(0.05)


        