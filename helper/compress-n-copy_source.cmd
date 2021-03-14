REM Hepler Batchfile for converting .py files into compressed .mpy
REM
REM
REM

SET SourceFolder=D:\Dropbox\Development\Github\APRS-Buddy\circuitpython
SET TempFolder=D:\Dropbox\Development\Projects\HAM\APRS_Buddy\Code\CircuitPython\copy_jobs\temp
SET MPYCrossFolder=D:\Dropbox\Development\_electronicparts\_SingleBoardComputers\circuitpython\mpy-cross
SET CircuitPythonBoard=F:

D:
CD %TempFolder%
robocopy %SourceFolder% %TempFolder% /mir /XF code.py
for %%i in (*.py) do %MPYCrossFolder%\mpy-cross.exe %%i
del *.py
copy %SourceFolder%\code.py %TempFolder%
cd lib
for %%i in (*.py) do %MPYCrossFolder%\mpy-cross.exe %%i
del *.py
robocopy %TempFolder% %CircuitPythonBoard% /mir
pause
