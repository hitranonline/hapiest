# hapiest
*hapiest* is a GUI that works with the HITRAN API, enabling access
to all sorts of spectrographic data without knowledge of python.

# How to Install
Hapiest currently has no binary packages, but the program itself can be downloaded
with the [install.py](https://github.com/hitranonline/hapiest/blob/master/install.py) script.

*You must have python 3.6 or later to install and use hapiest*.

For windows, mac, or linux, download [install.py](https://raw.githubusercontent.com/hitranonline/hapiest/master/install.py) and run it in the directory you want the hapiest folder to be created.

For mac and linux you can run the following in the terminal, and on windows in the command line:
```bash
wget -O install.py https://raw.githubusercontent.com/hitranonline/hapiest/master/install.py 
&& python install.py 
&& rm -rf install.py
```

This will download and unzip the latest version of hapiest. You may need to manually install packages using pip.

You may have to replace `python` in the above command with `python3` or `python3.6` depending on your specific
configuration.

After you install hapiest, you can start it by calling `run` in a command prompt or terminal. If you are on mac you may
have to edit the `run` file and replace `python` with `python3` or `python3.6`.

# Troubleshooting
*hapiest* is still a very immature piece of software. If you encounter any bugs, you're encouraged to open an issue with
your bug report.

# References
If you use data retreived using hapiest or hapi and use it, please use the following citation if you publish it:

```
R.V. Kochanov, I.E. Gordon, L.S. Rothman, P. Wcislo, C. Hill, J.S. Wilzewski, HITRAN Application Programming Interface
(HAPI): A comprehensive approach to working with spectroscopic data, J. Quant. Spectrosc. Radiat. Transfer 177, 15-30
(2016) [http://www.sciencedirect.com/science/article/pii/S0022407315302466?via%3Dihub].
```
