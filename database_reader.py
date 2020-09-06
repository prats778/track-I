######----------- ---- --   Team trac-i  -- ---- ------------######
## files stored in database are in order from latest to oldest
import os
import numpy as np
import time
from datetime import datetime

def get_day(file):
    dayy = file.split("x")[0]
    tym = (file.split("x")[1]).split(".")[0]
    return dayy, tym

def parse_day(net):
    return net.split("-")[2]

# return array of diff
def get_last_ndays(ndays):
    all_files = os.listdir(os.path.join(os.getcwd(),"database"))
    
    blink_count_arr = []      # stores blink count of a day
    on_screen_time_arr = []   # stores on screen time of a day
    date = []                 # stores date yyyy-mm-dd
    start_time_arr = []       # stores starting time of the day
    
    last_day = -1
    
    paused_time = 0
    start_time = 0
    stop_time = 0
    blink_count = 0
    on_screen_time = 0
    
    for file in all_files:
        # file = all_files[1]
        fs = open(os.path.join(os.getcwd(),"database", file), 'r')
        day, tym = get_day(file)
        date.append(day)
        start_time_arr.append(tym)
        
        paused_time = 0
        start_time = 0
        stop_time = 0
        blink_count = 0
        on_screen_time = 0
        
        for lines in fs:
            lines = lines[:-1]
            key = lines.split(" ")[0]
            if(key == "PAUSED"):
                paused_time += int(lines.split(" ")[2])
            elif(key=="STARTED"):
                start_time = float(lines.split(" ")[2])
            elif(key=="STOPPED"):
                stop_time += float(lines.split(" ")[2])
            else:
                on_screen_time = int(lines.split(" ")[0])
                blink_count = int(lines.split(" ")[1])
        on_screen_time_arr.append(on_screen_time)
        blink_count_arr.append(blink_count)
        
        fs.close()
    # print(date)
    # average of previous days calculation
    res = []
    last_dates=[]
    l_d = -1
    for i,day_ in enumerate(date):
        d = parse_day(date[i])
        # print(d,"-------")
        avg = 0
        if(on_screen_time_arr[i]):
            avg = blink_count_arr[i]/on_screen_time_arr[i]
        if(l_d != d):
            last_dates.append(date[i])
            res.append(avg)
        else:
            res[len(res)-1] += avg 
        l_d = d
    # print(res)
    if(ndays<len(res)):
        return res,last_dates
    return res[:ndays],last_dates[:ndays]

    