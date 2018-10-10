
def generateCustomID(lencustomID):
    #Generate a random series of chars upper/lower + numbers
    import string, random

    upper = list(string.ascii_uppercase)
    lower = list(string.ascii_lowercase)
    numbers = list(string.digits)
    allcharli = upper + lower + numbers
    customIDli = []
    for _ in range(lencustomID):
        customIDli.append(random.choice(allcharli))
    customID = ''.join(customIDli)
    return customID


def generateID():
    from fup.utils.jsoninfo import configInfo
    import uuid
    from datetime import datetime
    config = configInfo()
    genbigID = config["generateBigID"].strip().upper()
    gencustomID = config["generateCustomID"].strip().upper()
    lencustomID = int(config["customIDlentgh"].strip())
    #print(genbigID, gencustomID, lencustomID)
    if genbigID == "YES":
        bigID = datetime.now().strftime('%Y-%m-%d-%H-%M') +'-'+ str(uuid.uuid4())
        return bigID
    elif gencustomID == "YES":
        return generateCustomID(lencustomID)
    else:
        return generateCustomID(6)


def listifyString(astring, delimiter=','):
    #get a list from a string
    strListifyed = astring.split(delimiter)
    astringListifyed = [s.strip() for s in strListifyed]
    return astringListifyed



def getfilespath_from(root_path):
    #Walk thru a start path and return a list of paths to files
    import os
    allfiles = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            path_tofile = os.path.join(root, file)
            allfiles.append(path_tofile)
    return allfiles


def current_date():
    #Get current date in day-month-year format
    from datetime import datetime
    date = datetime.now().strftime('%d-%m-%Y')
    return date


def copytree(src, dst, symlinks=False, ignore=None):
    #Copy dirs and it's items from src to dst
    import os, shutil
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)



def deletetree(apath):
    import shutil
    try:
        shutil.rmtree(apath) #delete folders, subfolders and files
        return True
    except:
        shutil.rmtree(apath, ignore_errors=True) #delete files that are not opened
        response = "Could not remove folder {}, because some files are opened! Please delete them manually...".format(apath)
        return response



def validate(args, paramdict):
    #check if not empty return a dict {idx:val}

    validateddict = {}
    for arg in args:
        if len(paramdict[arg]) != 0:
            validateddict[arg] = paramdict[arg]

    return validateddict


def cleanDict(adict):
    cleaneddict = {}
    for k, v in adict.items():
        try:
            if len(v) != 0:
                cleaneddict[k] = v
        except:
            if v != 0:
                cleaneddict[k] = v

    return cleaneddict




def delPunctuationMarks(astring):
    import string
    punct_marks = list(str(string.punctuation)) + [' ']
    compactli = []
    for c in list(astring):
        if c not in punct_marks:
            compactli.append(c)

    compact_string = ''.join(compactli)

    return compact_string



def delElemFromList(elem, alist):
    try:
        alist.remove(elem)
        return alist
    except:
        return False


def getDirs(pathsli):
    import os
    onlydirsli = []
    for path in pathsli:
        if os.path.isdir(path):
            onlydirsli.append(path)

    return onlydirsli


def movetobin(tobinli):
    import shutil
    from fup.helpers.batch import batchExists
    from fup.utils.commun import deletetree

    dirsnotmoved = []
    for d in tobinli:
        src = d['source']
        dst = d['destination']
        bid = dst.split("\\")[-1]
        try:
            if batchExists(bid):
                print('movetobin- ', src, dst, bid)
                shutil.move(src, dst)
        except:
            dirsnotmoved.append(d)
            pass
    
    for d in dirsnotmoved:
        #[{'source': 'E:\\working_python\\Followup v0.59\\DC BATCHES IN WORK\\0 NEW\\ASD 300', 'destination': 'E:\\working_python\\Followup v0.59\\bin\\LvHDKI'}]
        src = d['source']
        deletetree(src)

    if len(dirsnotmoved) == 0:
        #print('\nfiles moved to bin')
        return True
    else:
        #print(dirsnotmoved)
        return dirsnotmoved


def list_duplicates(seq):
    #Check for duplicates
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list(seen_twice)


def uniquelist(seq):
    #return a uniques list but peserve order
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def cleanPath(apath):
    li = apath.split('\\')
    li = list(filter(None, li))
    cleanedPath = '\\'.join(li)
    return cleanedPath


def createDirsifNotExists():
    #Create the working directories if doesn't exist
    import os
    cwd = os.getcwd()
    root_path = os.path.join(cwd, 'DC BATCHES IN WORK')

    sub_folders = ['0 NEW',
                   '1 UNASSIGNED',
                   '2 PREPARED FILES',
                   '3 ASSIGNED',
                   '4 TO BE CHECKED',
                   '5 TO BE IMPORTED',
                   '6 FINISHED',
                   '7 IN STANDBY',
                   '8 UNRECORDABLE']

    extraDirs = [root_path, 'excels exported', 'excels to be imported', 'FUDB', 'bin']

    for extradir in extraDirs:
        try:
            os.mkdir(extradir)
        except:
            pass

    for adir in sub_folders:
        subdir = os.path.join(root_path, adir)
        try:
            os.mkdir(subdir)
        except:
            pass



def xllook(xlfilepath, colsrange, close=False):
    #Change the look of the excel
    import xlwings as xw
    import pythoncom
    pythoncom.CoInitialize()  
    import time
    time.sleep(3)
    xl = xw.Book(xlfilepath)
    sht = xl.sheets[0]
    sht.range(colsrange).columns.autofit()
    sht.range(colsrange).color = (51,153,255)# blue
    xl.save()
    if close:
        xl.close()



# Regula 3 simpla simpli
# def ruleOfTree(if_for_x, i_have_y, then_for_val, roundnr=2):
#     # if_for_x ............. i_have_y
#     # then_for_val ............ result
#     result = round(((float(then_for_val) * float(i_have_y))/float(if_for_x)), roundnr)
#
#     return result
#
#
# def convertBytestoKB(size):
#     from fup.utils.commun import ruleOfTree
#     return ruleOfTree(1024, 1, size, 3)




















#
