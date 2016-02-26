import logging
import subprocess
   
# idempotent mysql create db
def createDB(user, passw, dbname):
    dbfound = False
    dblist = subprocess.check_output(['mysql','-u',user,'-p' + passw,'-e',"show databases;",'-B','--disable-column-names'])
    for db in dblist.splitlines():
        if db == dbname:
            logging.info('database "' + dbname + '" already exists')
            dbfound = True
            break
        
    if not dbfound:
        subprocess.check_call(['mysql','-u',user,'-p' + passw,'-e',"create database " + dbname + ";"])
        logging.info('created database "' + dbname + '"')

def createLocalUserWithAllPrivilegesOnDB(user, passw, newuser, newpass, targetDBName):
    subprocess.check_call(['mysql','-u',user,'-p' + passw,'-e',"grant all privileges on " + targetDBName + ".* to '" + newuser + "'@'localhost' identified by '" + newpass + "';"])
    logging.info('granted privileges on "' + targetDBName + '" to "' + newuser + '"')
