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
SET /P M=Choose 1, 2, 3, 4; or 0 to ENABLE %INT%:___; w to set lan-wired route: 
GOTO :ARG

:ARG
IF %M%==0 GOTO ENABLE
IF %M%==1 GOTO GW1
IF %M%==2 GOTO GW2
IF %M%==3 GOTO GW3
IF %M%==4 GOTO GW4
IF %M%==w GOTO LANROUTE

:ENABLE
netsh interface show interface "%INT%"
netsh interface set interface name="%INT%" admin=ENABLE
GOTO MENU

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
SET DNS1=114.114.115.115
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
ECHO "Setting IP %IP% Gateway %GATE%"
netsh interface ip set address "%INT%" static %IP% 255.255.255.0 %GATE% 10
ECHO "Setting DNS1 %DNS1%"
netsh interface ip add dns name="%INT%" addr=%DNS1% index=1
ECHO "Setting DNS2 %DNS2%"
netsh interface ip add dns name="%INT%" addr=%DNS2% index=2
ECHO "Flush DNS"
ipconfig /flushdns
ECHO "Resolving baidu.com"
nslookup baidu.com
ECHO "Ping baidu.com"
ping baidu.com
pause

:LANROUTE
SET IP=%IP:x=1%
SET GATE=%GATE:x=1%
netsh interface ip set address "%INT%" static %IP% 255.255.255.0
ping -n 1 127.0.0.1>nul
route add "192.168.0.0" MASK "255.255.0.0" %GATE%
pause