# ARR
A RSS-Reader with GUI. Tested to work with Debian 12, Windows 10 and 11 and macOS 12.

# Installing
debian-packages required: python3-tk python3-venv. In windows and macOS there is no need to install anything.

```console
foo@bar:~$ sudo apt install python3-tk python3-venv
```

Then clone this repo and:

```console
foo@bar:~$ git clone https://github.com/SamuelKos/ARR
foo@bar:~$ cd ARR
In Linux and macOS:
foo@bar:~/ARR$ ./make
In Windows:
> py win_install_rss.py
```

# About Python dependencies:
Only one library outside standard is used: [html2text](https://github.com/Alir3z4/html2text/)
which is installed with pip. Interesting fact is that it is forked from repo
owned by [Aaron Swartz](https://en.wikipedia.org/wiki/Aaron_Swartz),
who was involved in RSS-format developing and more. Check it out!
 

# Running

```console
foo@bar:~$ rss
```

# Uninstalling
Just remove the ARR -folder and rss-script in home/bin, or from sys.base_prefix if in Windows.
To remove git and tkinter:

```console
foo@bar:~$ sudo apt remove python3-tk git
```

# Licence
This project is licensed under the terms of the GNU General Public License v3.0.
