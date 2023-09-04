import logging

slogger=logging.getLogger("Reporting Tool Log")
slogger.setLevel(logging.DEBUG)
formatter=logging.Formatter("%(asctime)s|%(lineno)s|%(levelname)s:%(message)s")
sh=logging.StreamHandler()
fh=logging.FileHandler(filename="s1Report.log")
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
    cont=str(sysinfo._getframe(1).f_code.co_name)+"|"+cont
    slogger.debug(cont)


