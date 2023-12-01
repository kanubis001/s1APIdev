import logging
import psutil
import os

slogger=logging.getLogger("Comsys Tool Log")
slogger.setLevel(logging.DEBUG)
formatter=logging.Formatter("%(asctime)s|%(lineno)s|%(levelname)s:%(message)s")
sh=logging.StreamHandler()
tk_dir=os.path.expanduser('~')
fh=logging.FileHandler(filename=tk_dir+"\\s1reportingtool.log")
fh.setFormatter(formatter)        
sh.setFormatter(formatter)
slogger.addHandler(sh)
slogger.addHandler(fh)

def log_write(file,func,cont):
    cont=str(file)+"|"+str(func)+"|"+cont
    slogger.debug(cont)

def log_simple(cont):
    slogger.debug(cont)       
    
def log_write2(sysinfo,cont):
    strplus=str(sysinfo._getframe(1).f_code.co_name)
    cont=f'{strplus}|{cont}'
    # str(sysinfo._getframe(1).f_code.co_name)+"|"+cont
    slogger.debug(cont)

def memoryFollow(cont):
    p=psutil.Process()
    rss_mb=p.memory_info().rss/2 ** 20 # Bytes to MB
    print(f"[{cont}] memory usage: {rss_mb: 10.5f} MB")

