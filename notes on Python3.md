# Notes on getting Python OLA API to work (with Python3)

Install the OLA Python package (ola-python):
```
$ sudo apt update
$ sudo apt install ola-python
```

But... this only installs for Python2.7:
```
$ dpkg -L ola-python
/.
/usr
/usr/lib
/usr/lib/python2.7
/usr/lib/python2.7/dist-packages
/usr/lib/python2.7/dist-packages/ola
/usr/lib/python2.7/dist-packages/ola/ArtNetConfigMessages_pb2.py
.....
```

We might be able to just set up a symlink into the python3 dist-packages folder - suggested here:
https://groups.google.com/g/open-lighting/c/7TuvU0T1CAo/m/X8KeOfI8BgAJ
```
$ sudo ln -s /usr/lib/python2.7/dist-packages/ola/ /usr/lib/python3/dist-packages/
```

Doesn't work - module `google.protobuf` isn't installed...
This message suggests how to install protobuf on Pyhton3:
https://groups.google.com/g/open-lighting/c/7TuvU0T1CAo/m/E2qJDgD3BAAJ
```
$ sudo -H pip3 install protobuf
```

Which does now seem to work! :-)
But user beware - there may be further issues with using python2.7 (OLA) code under python3...
