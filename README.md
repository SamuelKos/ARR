# ARR
A RSS-Reader with GUI. Tested to work with Debian 12, Windows 10 and 11 and macOS 12.

# Installing
Windows: there is no need to install anything besides Python and Git.

Linux: debian-packages required: python3-tk python3-venv:

```console
In Linux:
foo@bar:~$ sudo apt install python3-tk python3-venv
```

MacOS: install Python and tkinter with [Homebrew](https://brew.sh). You need first to
install Command Line [Tools](https://docs.brew.sh/Installation) with:

```console
In macOS:
foo@bar:~$ xcode-select --install
```

Then download the [.pkg -installer](https://github.com/Homebrew/brew/releases) from Github and
use it to install Homebrew. After you have installed Homebrew you can use it to install Python and
Tkinter and Git. You may need to restart your shell in between, not sure about that:

```console
In macOS:
foo@bar:~$ brew install python
foo@bar:~$ brew install python-tk
foo@bar:~$ brew install git
```


Now you have Git and Python working, then clone this repo and:

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
To remove Git and Tkinter:

```console
In Linux:
foo@bar:~$ sudo apt remove python3-tk git
In macOS:
foo@bar:~$ brew rm python-tk
foo@bar:~$ brew rm python
foo@bar:~$ brew rm git
```

# Licence
This project is licensed under the terms of the GNU General Public License v3.0.
