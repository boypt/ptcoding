@ECHO OFF
SET INT=Wired
SET IP="192.168.5x.18"
SET GATE="192.168.5x.1"

IF [%1] == [] GOTO MENU
SET M=%1 
SHIFT
GOTO :ARG

:MENU
netsh interface ip show addresses "%INT%"
SET /P M=Choose 1, 2, 3, 4
GOTO :ARG

:ARG
IF %M%==1 GOTO GW1
IF %M%==2 GOTO GW2
IF %M%==3 GOTO GW3
IF %M%==4 GOTO GW4

:GW1
SET IP=%IP:x=1%
SET GATE=%GATE:x=1%
SET DNS1=221.4.8.1
SET DNS2=210.21.4.130
GOTO END

:GW2
SET IP=%IP:x=2%
SET GATE=%GATE:x=2%
SET DNS1=202.96.128.86
SET DNS2=202.96.128.166
GOTO END

:GW3
SET IP=%IP:x=3%
SET GATE=%GATE:x=3%
SET DNS1=202.96.128.86
SET DNS2=202.96.128.166
GOTO END

:GW4
SET IP=%IP:x=4%
SET GATE=%GATE:x=4%
SET DNS1=101.226.4.6
SET DNS2=180.76.76.76
GOTO END

:END
netsh interface ip delete dnsservers name="%INT%" addr=all
ECHO ===================================================...
netsh interface ip set address "%INT%" static %IP% 255.255.255.0 %GATE% 10
netsh interface ip add dns name="%INT%" addr=%DNS1% index=1
netsh interface ip add dns name="%INT%" addr=%DNS2% index=2
ipconfig /flushdns
nslookup baidu.com
ping baidu.com
pause