import os
import glob
import subprocess

def run(self,cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

path='C:\\Program Files\\SentinelOne\\'
path_s1=os.listdir(path)
print(path_s1) # 경로 여러개일 수도 있음
fullpath=path+str(path_s1[1])
filepath = glob.glob(fullpath+'\\SentinelCtl.exe', recursive=True) 
print(filepath)