#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


>!k::
    If WinExist("Kodi")
        WinActivate
    else
        Run "%ProgramFiles%\Kodi\kodi.exe"        
	Return

;爱奇艺
>!a::
	Run, explorer.exe shell:AppsFolder\0C72C7CD.Beta_atj5cpqqdhzyp!App
    ;Run, PowerShell "explorer.exe shell:AppsFolder\$(get-appxpackage -name 0C72C7CD.Beta | select -expandproperty PackageFamilyName)!App"
	Return

>!g::
	Run, explorer.exe shell:AppsFolder\B5504E89.UWP_x4jnea0mfqbwc!App
    ;Run, PowerShell "explorer.exe shell:AppsFolder\$(get-appxpackage -name 0C72C7CD.Beta | select -expandproperty PackageFamilyName)!App"
	Return


>!t::
	Run, explorer.exe shell:AppsFolder\64280.487927C36C6E8_47w5tp4qbz8pg!App
    ;Run, PowerShell "explorer.exe shell:AppsFolder\$(get-appxpackage -name 0C72C7CD.Beta | select -expandproperty PackageFamilyName)!App"
	Return
	
;Hibernate:
>!F10::
    ;Hibernate:
    DllCall("PowrProf\SetSuspendState", "int", 1, "int", 0, "int", 0)
    Return
	
; Sleep/Suspend:
;!F9::
;    ;Sleep/Suspend:
;    DllCall("PowrProf\SetSuspendState", "int", 0, "int", 0, "int", 0)
;    Return
