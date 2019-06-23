#! /usr/bin/env python
from subprocess import Popen,PIPE,STDOUT
import collections
import os
import sys
import time
import math
import os
import time
from urllib2 import urlopen
from random import randint

BOOTSTRAP_URL = "" #TODO
SENTINEL_GIT_URL = "https://github.com/KeplerPay/sentinel.git"

MN_USERNAME = "MN1"
MN_PORT = 12102
MN_RPCPORT = 12101
MN_NODELIST = ""

MN_LFOLDER = ".keplercore"
MN_WFOLDER = "KeplerCore"
MN_CONFIGFILE = "kepler.conf"
MN_DAEMON = "keplerd"
MN_CLI = "kepler-cli"
MN_EXPLORER = "http://explorer.kepler.cash/"

MN_SWAPSIZE = "2G"
SERVER_IP = urlopen('http://ip.42.pl/raw').read()
DEFAULT_COLOR = "\x1b[0m"
PRIVATE_KEY = ""

def print_info(message):
    BLUE = '\033[94m'
    print(BLUE + "[*] " + str(message) + DEFAULT_COLOR)
    time.sleep(1)

def print_warning(message):
    YELLOW = '\033[93m'
    print(YELLOW + "[*] " + str(message) + DEFAULT_COLOR)
    time.sleep(1)

def print_error(message):
    RED = '\033[91m'
    print(RED + "[*] " + str(message) + DEFAULT_COLOR)
    time.sleep(1)

def get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h
    
def remove_lines(lines):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    for l in lines:
        sys.stdout.write(CURSOR_UP_ONE + '\r' + ERASE_LINE)
        sys.stdout.flush()

def run_command_as(user, command):
    run_command('su - {} -c "{}" '.format(user, command))

def run_command(command):
    out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
    lines = []
    
    while True:
        line = out.stdout.readline()
        if (line == ""):
            break
        
        # remove previous lines     
        remove_lines(lines)
        
        w, h = get_terminal_size()
        lines.append(line.strip().encode('string_escape')[:w-3] + "\n")
        if(len(lines) >= 9):
            del lines[0]

        # print lines again
        for l in lines:
            sys.stdout.write('\r')
            sys.stdout.write(l)
        sys.stdout.flush()

    remove_lines(lines) 
    out.wait()

def run_command_with_output(command):
    out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
    lines = []
    while True:
        line = out.stdout.readline()
        if (line == ""):
            break
        lines.append(line.strip().encode('string_escape'))
    out.wait()
    return lines
                               
def print_welcome():
    os.system('clear')
    PURPLE = '\033[35m'
    print(PURPLE + "  _  ________ _____  _      ______ _____  " + DEFAULT_COLOR)
    print(PURPLE + " | |/ /  ____|  __ \| |    |  ____|  __ \ " + DEFAULT_COLOR)
    print(PURPLE + " | ' /| |__  | |__) | |    | |__  | |__) |" + DEFAULT_COLOR)
    print(PURPLE + " |  < |  __| |  ___/| |    |  __| |  _  / " + DEFAULT_COLOR)
    print(PURPLE + " | . \| |____| |    | |____| |____| | \ \ " + DEFAULT_COLOR)
    print(PURPLE + " |_|\_\______|_|    |______|______|_|  \_\ " + DEFAULT_COLOR)
    print(PURPLE + "                                           " + DEFAULT_COLOR)
    print_info("Kepler masternode installer v1.0")

def update_system():
    print_info("Updating the system...")
    run_command("apt-get update")
    run_command("apt-get upgrade -y")
    #run_command("apt-get dist-upgrade -y")

def check_root():
    print_info("Check root privileges")
    user = os.getuid()
    if user != 0:
        print_error("This program requires root privileges.  Run as root user.")
        sys.exit(-1)

def secure_server():
    print_info("Securing server...")
    run_command("apt-get --assume-yes install ufw")
    run_command("ufw allow OpenSSH")
    run_command("ufw allow {}".format(MN_PORT))
    run_command("ufw default deny incoming")
    run_command("ufw default allow outgoing")
    run_command("ufw --force enable")

def setup_wallet():
    server_ram = run_command_with_output("free -g|awk '/^Mem:/{print $2}' ")[0]
    if server_ram < 2:
        print_warning("Server RAM is lower than 2GB, allocating swap...")
        print_info("Allocating swap...")
        run_command("fallocate -l {} /swapfile".format(MN_SWAPSIZE))
        run_command("chmod 600 /swapfile")
        run_command("mkswap /swapfile")
        run_command("swapon /swapfile")

        f = open('/etc/fstab','r+b')
        line = '/swapfile   none    swap    sw    0   0 \n'
        lines = f.readlines()
        if (lines[-1] != line):
            f.write(line)
            f.close()
    else:
        print_info("Your server has at least 2GB of RAM, skipping swap creation")

    print_info("Installing useful programs...")
    run_command("apt-get -y --assume-yes install git unzip iptables htop nano")
    print_info("Installing wallet dependencies...")
    run_command("apt-get -y install software-properties-common")
    run_command("add-apt-repository ppa:bitcoin/bitcoin -y")
    run_command("apt-get update")
    run_command("apt-get --assume-yes install libboost-program-options-dev libboost-test-dev libdb4.8-dev "
                "libdb4.8++-dev libminiupnpc-dev libevent-dev libzmq3-dev libboost-filesystem1.58.0 libdb4.8++ "
                "libevent-2.0-5 libevent-core-2.0-5 libevent-pthreads-2.0-5 libminiupnpc10 libsodium18 "
                "libboost-system1.58.0 libboost-thread1.58.0 libevent-2.0-5 libzmq5 libboost-chrono1.58.0")

    print_info("Downloading wallet...")
    run_command("wget https://kepler.cash/upload/keplerd-latest -O /usr/local/bin/{}".format(MN_DAEMON))
    run_command("chmod +x /usr/local/bin/{}".format(MN_DAEMON))
    run_command("wget https://kepler.cash/upload/kepler-cli-latest -O /usr/local/bin/{}".format(MN_CLI))
    run_command("chmod +x /usr/local/bin/{}".format(MN_CLI))

def setup_masternode():
    print_info("Setting up masternode...")
    #masternode_alias = raw_input("alias: ")
    #global MN_USERNAME
    #MN_USERNAME = masternode_alias
    #SERVER_IP = raw_input("IP to use: ")
    #MN_RPCPORT = raw_input("RPC port: ")
    run_command("useradd --create-home -G sudo {}".format(MN_USERNAME))
    
    rpc_username = "MN{}".format(randint(0, 999))
    rpc_password = run_command_with_output("head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16 ; echo '' ")[0]
    print_info("Generated a random rpcuser and rpcpassword\n Save it just in case:\n\trpcuser=[{}]\n\trpcpassword=[{}]".format(rpc_username, rpc_password))
    print_info("Open your wallet console (Tools => Debug Console) and create a new masternode private key: masternode genkey")
    masternode_priv_key = raw_input("masternodeprivkey: ")
    global PRIVATE_KEY
    PRIVATE_KEY = masternode_priv_key
    
    config = """rpcuser={}
rpcpassword={}
rpcallowip=127.0.0.1
rpcport={}
port={}
server=1
listen=1
daemon=1
logtimestamps=1
mnconflock=1
masternode=1
externalip={}:{}
masternodeprivkey={}
{}""".format(rpc_username, rpc_password, MN_RPCPORT, MN_PORT, SERVER_IP, MN_PORT, masternode_priv_key, MN_NODELIST)
# bind= SERVER_IP
    # creates folder structure
    run_command_as(MN_USERNAME, "mkdir -p /home/{}/{}/".format(MN_USERNAME, MN_LFOLDER))
    run_command_as(MN_USERNAME, "touch /home/{}/{}/{}".format(MN_USERNAME, MN_LFOLDER, MN_CONFIGFILE))
    
    print_info("Saving config file...")
    with open('/home/{}/{}/{}'.format(MN_USERNAME, MN_LFOLDER, MN_CONFIGFILE), 'w') as f:
        f.write(config)
        
    #print_info("Downloading blockchain file...")#TODO
    run_command("apt-get --assume-yes install megatools")
    #filename = "blockchain.rar"
    #run_command_as(MN_USERNAME, "cd && megadl '{}' --path {}".format(BOOTSTRAP_URL, filename))
    
    #print_info("Unzipping the file...")
    run_command("apt-get --assume-yes install unrar")    
    #run_command_as(MN_USERNAME, "cd && unrar x -u {} {}".format(filename, MN_LFOLDER))
       
    os.system('su - {} -c "{}" '.format(MN_USERNAME, MN_DAEMON + ' -daemon'))
    print_warning("Masternode started syncing in the background...")

def crontab(job):
    p = Popen("crontab -l -u {} 2> /dev/null".format(MN_USERNAME), stderr=STDOUT, stdout=PIPE, shell=True)
    p.wait()
    lines = p.stdout.readlines()
    if job not in lines:
        print_info("Cron job doesn't exist yet, adding it to crontab")
        lines.append(job)
        p = Popen('echo "{}" | crontab -u {} -'.format(''.join(lines), MN_USERNAME), stderr=STDOUT, stdout=PIPE, shell=True)
        p.wait()


def autostart_masternode():
    job = "@reboot /usr/local/bin/{}\n".format(MN_DAEMON)
    crontab(job)
    

def setup_sentinel():
    # no sentinel support
    if SENTINEL_GIT_URL == "":
        return
    
    print_info("Setting up Sentinel (/home/{}/{}/sentinel)...".format(MN_USERNAME, MN_LFOLDER))

    # install dependencies
    run_command("apt-get -y install python-virtualenv git virtualenv")

    # download and install sentinel
    run_command_as(MN_USERNAME, "git clone {} /home/{}/{}/sentinel".format(SENTINEL_GIT_URL, MN_USERNAME, MN_LFOLDER))
    run_command_as(MN_USERNAME, "cd /home/{}/{}/sentinel && virtualenv ./venv ".format(MN_USERNAME, MN_LFOLDER))
    run_command_as(MN_USERNAME, "cd /home/{}/{}/sentinel && ./venv/bin/pip install -r requirements.txt".format(MN_USERNAME, MN_LFOLDER))

    # run sentinel every minutes
    job = "* * * * * cd /home/{}/{}/sentinel && SENTINEL_DEBUG=1 ./venv/bin/python bin/sentinel.py >> sentinel.log 2>&1".format(MN_USERNAME, MN_LFOLDER)
    crontab(job)

    # try to update sentinel every week
    job = "* * 7 * * cd /home/{}/{}/sentinel && git pull https://github.com/KeplerPay/sentinel.git".format(MN_USERNAME, MN_LFOLDER)
    crontab(job)
    
def end():

    mn_base_data = """
    Alias: {}
    IP: {}
    Private key: {}
    Transaction ID: [The transaction id of the deposit. 'masternode outputs']
    Transaction index: [The transaction index of the deposit. 'masternode outputs']
    --------------------------------------------------
"""

    mn_data = mn_base_data.format(MN_USERNAME,SERVER_IP + ":" + str(MN_PORT), PRIVATE_KEY)

    print('')
    print_info(
"""Masternodes setup finished!
    Wait until the masternode is fully synced. To check the progress login the 
    masternode account (su {}) and run the '{} getinfo' command to get
    the actual block number. Go to {} website to check 
    the latest block number or use your wallet. After the syncronization is done 
    add your masternode to your desktop wallet.
Masternode data:""".format(MN_USERNAME, MN_CLI, MN_EXPLORER) + mn_data)

def main():
    print_welcome()
    check_root()
    update_system()
    secure_server()
    setup_wallet()
    setup_masternode()
    autostart_masternode()
    setup_sentinel()
    end()

if __name__ == "__main__":
    main()
