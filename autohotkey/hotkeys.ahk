>!7::Run, cmd /C "ping -t 172.16.192.10"
>!1::Run, cmd /C "ping -t 192.168.1.1"
>!d::Run, cmd /C "ping -t 240c::6666"
>!p::
	InputBox, ipsuf, 192.168.
	If (ipsuf != "")
		Run, cmd /C ping -t 192.168.%ipsuf%
	Return
>!y::
	InputBox, query, Word
	If query != "")
		Run, cmd /K %USERPROFILE%\bin\ydcv.exe %query%
	Return
