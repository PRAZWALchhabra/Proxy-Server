import stat
import time
import datetime
import os
 
def cache_check(filename,lastmodificationTime):
 
    filePath = './'+filename
    
    fileStatsObj = os.stat ( filePath )
    
    modificationTime = time.ctime ( fileStatsObj [ stat.ST_MTIME ] )

    return modificationTime<=lastmodificationTime