
# decobayer

Python package decobayer attempts to implement remote protocol for Bayer
Contour Nextlink.


### Resources:
* how to enter command mode: https://github.com/bewest/decoding-bayer/blob/master/complete-pump-nextlink/head-1k.markdown#008458019-in-64
* how to exit command mode: https://github.com/bewest/decoding-bayer/blob/master/complete-pump-nextlink/tail-1k.markdown#250987692-out-64
* glucodump: https://bitbucket.org/iko/glucodump/src/ce8da3e63217098a844a9cdea99f90c5ee5d20c6/glucodump/?at=default

* outdated spec: https://github.com/bewest/diabetes/tree/master/bayer

#### ASTM
* https://github.com/kxepal/python-astm


## Status Quo

Work in progress:

* can get into command mode `python -m decobayer.modem`
* can read talk to pump remotely: `python -m decobayer.remote`
  As a test, this reads `SERIAL` environment variable, and reads that pump's
  model number. (In order for this to work, the comm's need to be initialized
  already, use `openaps` or `mm-send-comm.py` to initialize comms.


### Help needed

* PowerControl
* Sending parameters
* Identifying CRC's, length fields
* Reading long frames, identifying length fields to determine when frames are
  done
