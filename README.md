# MyEyeFoo
## Introduction
A simple Windows application to lock the screen every a period of time to protect you eyes.
'MyEyeFoo' is inspired by the software 'EyeFoo'. 'EyeFoo' is not supported any longer and does not support Windows 8 and above.

## requirements:
	* PyQt4
	* Python 2.x

## configuration
The file 'config.json' stores the configuration and it is in json format. Here are the meaning of the options.
### options
	* work_time       Time in seconds      MyEyeFoo counts down the time and lock the screen on time out.
	* relax_time      Time in seconds      During relax time, the screen will be locked. You have to manually unlock the screen.
	* lock_one_time   'true' or 'false'    If set 'false', the screen will automatically lock again if the relax time is not over. If set 'true', the screen will only be locked for one time.
	* check_period    Time in seconds      Auto-lock period in seconds during relax time if 'lock_one_time' is set 'false'.
	* beep_start_time Time in seconds      When there are only 'beep_start_time' to relax, beep to remind the user.
	* beep_times      count                Count of beeps.