import os
import subprocess
import tempfile
import time

def get_i2c(reg: str):
    os.system("i2cget -y 1 0x68 " + reg)

def read_i2c(reg) -> bytes:
    with tempfile.TemporaryFile() as tempf:
            # proc = subprocess.Popen(['i2cget -y 1 0x68', reg], stdout=tempf)
            # proc.wait()
            # tempf.seek(0)
            # bytes_arr = tempf.read()
            result = subprocess.run(['i2cget -y 1 0x68', reg], stdout=subprocess.PIPE)
            result.stdout
            print(f"tempf read {bytes_arr}")
            return bytes_arr

if __name__ == "__main__":

    i = 0

    while True:
        # get_i2c('0x3B')
        x1 = read_i2c('0x3B')

        # get_i2c('0x3C')
        x2 = read_i2c('0x3C')

        # final_value = (x1 << 8) | x2

        print(f"Output x1 - {x1}, x2 - {x2}")

        time.sleep(0.1)

        i+=1
        if i > 10:
            break


        # get_i2c('0x3D')

        # y1 = read_i2c()

        # time.sleep(0.05)

        # get_i2c('0x3E')

        # y2 = read_i2c()

        # time.sleep(0.05)


        