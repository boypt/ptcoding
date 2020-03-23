>!7::Run, cmd /C "ping -t 172.16.192.10"
>!1::Run, cmd /C "ping -t 192.168.1.1"
>!d::Run, cmd /C "ping -t 240c::6666"
>!t::Run, cmd /C "torrent2cloud_windows"
>!SPACE::  Winset, Alwaysontop, , A
>!p::
	InputBox, ipsuf, 192.168.
	If (ipsuf != "")
		Run, cmd /C ping -t 192.168.%ipsuf%
	Return
>!y::
	InputBox, query, Word
	If query != "")
		Run, %USERPROFILE%\bin\ydgo.exe %query%
	Return

>!F9::
	regKey := "HKCU\SOFTWARE\Microsoft\InputMethod\Settings\CHS"
	regValue := "Enable Double Pinyin"
	RegRead, DouEnabled, %regKey%, %regValue%
	If (DouEnabled == 0) {
		RegWrite, REG_DWORD, %regKey%, %regValue%, 1
		MsgBox, ˫ƴ
	} else {
		RegWrite, REG_DWORD, %regKey%, %regValue%, 0
		MsgBox, ȫƴ
	}
