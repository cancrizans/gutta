# Installation

The following instructions are for tech-illiterate Windows users. Linux users should not need much guidance.

## Installing Python 3.10

Install **Python 3.10**. Go [here](https://www.python.org/downloads/release/python-3108/), select Windows installer, download and install.

## Install git and git-bash

Install **git for Windows** including **git-bash**.  Go [here](https://gitforwindows.org/), download and install.

To test your progress so far, when you right-click in empty space in a folder, you should see the entries "Git GUI Here", "Git Bash Here". Select "Git Bash Here". The window that opens is the **git-bash** shell. Type `python --version` in the shell and press enter. If `Python 3.10.xxx` is printed, everything so far is installed correctly.

## Install gutta

If you closed the git-bash shell, reopen it. Type

```bash
pip install gutta
```

and enter. This will install the latest release of gutta. The command `pip show gutta` instead will let you know whether gutta is correctly installed and which version. If you have gutta already installed but you want to ensure you have the latest version available, run `pip install --upgrade gutta`.

Finally, to test everything, just run:

```bash
gutta
```

If gutta's usage information is printed, everything is correctly installed. You're done.
