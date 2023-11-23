import os
import subprocess
import tempfile

def get_i2c(reg: str):
    os.system("i2cget 1 0x68 " + reg)

if __name__ == "__main__":

    get_i2c('0x32')

    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(['echo'], stdout=tempf)
        proc.wait()
        tempf.seek(0)
        print(tempf.read())