# Kepler Masternode Installation Guide

- **Follow the guide carefully and read everything before you ask any question!**

Follow these instructions or the video guide to setup a masternode.
This guide is for the creation of separate Controller Wallet & Masternode.
For Security reasons, THIS IS THE PREFERRED way to run a Masternode.
Your coins will be safe if the masternode server is hacked.

## Table of Content
* [1. Desktop Wallet Preparation](#1-desktop-wallet-preparation-)
	* [1.1 Desktop Wallet Setup](#11-desktop-wallet-setup-)
* [2. Masternode Setup](#2-masternode-setup-)
	* [2.1 Send the coins to your wallet](#21-send-the-coins-to-your-wallet)
	* [2.2 Automatic Masternode Setup](#23-automatic-masternode-setup)
	* [2.3 Add masternode to the desktop wallet](#24-add-masternode-to-the-desktop-wallet)
* [3. FAQ](#3-faq)

## 1. Desktop Wallet Preparation <a href="https://www.youtube.com/watch?v=" target="_blank"><img src="https://i.imgur.com/"></a>

### 1.1 Desktop Wallet Setup
1. Download the wallet: [kepler.cash](https://kepler.cash/)
1. Start the wallet and select the default data directory. Afterwards close the wallet. (This creates the folder structure)
1. Start the wallet again and wait for synchronization. (2min to 15min)
1. You can optionaly encrypt the wallet (Settings => Encrypt wallet) for security reasons. Do not forget the password or you lose the coins that you have.
1. Backup `%appdata%/KeplerCore/wallet.dat` file. This contains your coins. DO NOT LOSE IT!
	
## 2. Masternode Setup <a href="https://www.youtube.com/watch?v=" target="_blank"><img src="https://i.imgur.com/"></a>

### 2.1 Send the coins to your wallet
1. Create and copy a new receiving address. (File => Receiving address => New)
1. Send exactly 10000 coins to this address. (One transaction, pay attention to the fee)
1. Wait for a confirmation.
1. Save the transaction id and index, `masternode outputs`, and generate and save a new masternode private key `masternode genkey` using the debug console (Tools => Debug Console)

### 2.2 Automatic Masternode Setup
1. Download [putty](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.70-installer.msi)
1. Start putty and login as root user. (Root password and server ip address is in vultr overview tab)
1. Paste this command and follow the instructions:
```
apt-get install -y python ; rm installer.py; wget https://raw.githubusercontent.com/KeplerPay/MasternodeInstall/master/installer.py && python installer.py
```
#### What does the script?
- updates the system
- secure the server (setups a firewall)
- setups swap if server RAM is not enough
- download and install the wallet
- configure the masternode with rpcusername, rpcpassword and mn's private key (the mn is running under mn1 username)
- setup sentinel
- setup cronjob for automated jobs (autostart masternode on system start, run sentinel every minutes, etc...)

### 2.3 Add masternode to the desktop wallet
1. Open `%appdata%/KeplerCore/masternode.conf` and add a new line to it. The line format is:<br> 'AliasName ServerIP:12102 PrivateKey TransactionID TransactionIndex'
1. Open the wallet, wait for synchronization, unlock the wallet
1. Go to Masternodes tab (Setting => Options => Wallet => Show Masternode Tab)
1. Click Start All
1. Wait around 2-10 hour to start receiving coins. Check the masternode address for rewards here: [explorer](http://explorer.kepler.cash/) or use your wallet.

## 3. FAQ

1. What if I restart the server?
	- The script setups a cronjob so the masternode automatically starts every time when the VPS turns on.
1. What is the password for the mn1 account?
	- There is no default password. When you create a user it does not have a password yet, so you cannot login with that username until you create a password. There is one other way to act as a new user without its password. As root type `su - mn1`
	- You need to set a password for the user. Use the passwd command: `passwd mn1`
1. I get the following error: "Could not allocate vin"
	- Make sure your wallet fully synced and UNLOCKED.
	- Make sure the masternode address contains exactly 10000 coins.
1. How many masternodes can I run using one IP/server?
	- You can only use one masternode per IP address.
1. How do I delete the masternode?
 	```
 	userdel -r -f mn1
 	```


	
