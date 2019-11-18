# NeverScape Auto Build

This is the automated build process for the NeverScape client. It produces three executables: an EXE for Windows, ELF for Linux, and Mach-O for macOS. A local VirtualBox environment running Windows, Linux, and macOS is used to build the cross-platform binaries. [PyInstaller](https://www.pyinstaller.org/) is used to create the NeverScape Python client binary executables. See below for notes about the configuration of the  three virtual machines.

Install CLI:
```
$ python setup.py install --user
```

Config file:
```
$ cat ~/.nsbuild_config
[settings]
windows_ip = 192.168.1.75
linux_ip = 192.168.1.76
macos_ip = 192.168.1.77
```

Usage:
```
$ nsbuild
Zipping neverscape-client...
Creating SSH & SFTP clients...
mac: SFTPing the zip
mac: Unzipping the client
mac: Building client!
mac: SFTPing the binary
linux: SFTPing the zip
linux: Unzipping the client
linux: Building client!
linux: SFTPing the binary
windows: SFTPing the zip
windows: Unzipping the client
windows: Building client!
windows: SFTPing the binary
mac: Cleaning up
linux: Cleaning up
windows: Cleaning up
```

## Windows VM notes

Windows 10 Pro

* Win 10 ISO: https://www.microsoft.com/en-us/software-download/windows10ISO
* Run a Windows update
* Install Python 3.7.x latest: https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe
* Install OpenSSH: https://github.com/PowerShell/Win32-OpenSSH/wiki/Install-Win32-OpenSSH
    * Move OpenSSH folder to "Program Files"
    * Allow 22 on firewall
    * Services -> OpenSSH -> Startup -> Auto
* Install PyInstaller: `python -m pip install pyinstaller` (run as Admin)
* Download UnxUtils: https://sourceforge.net/projects/unxutils/
    * Copy `UnxUtils\usr\local\wbin\unzip.exe` to system32
* pip install client requirements
    * `python -m pip install pyglet sickserv` (run as admin)

## Linux VM notes

Debian 10 Buster

* ISO: https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-10.1.0-amd64-netinst.iso
* Login as root
    * `apt-get update`
    * `apt-get install sudo`
    * `usermod -a -G sudo user`
    * swich to user
* Install pip: `sudo apt-get install python3-pip`
* Install PyInstaller: `sudo pip3 install pyinstaller`
* Install game libs: `pip3 install pyglet sickserv --user`
* Install unzip & tkinter: `sudo apt-get install unzip python3-tk`

## macOS VM notes

* TBD
