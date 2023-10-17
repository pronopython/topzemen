@echo off

WHERE printModuleDir_topzemen
IF %ERRORLEVEL% NEQ 0 (
	ECHO installing topzemen module via pip
	pip install .
)

for /f %%i in ('printModuleDir_topzemen') do set INSTALLDIR=%%i
echo topzemen module installed in: %INSTALLDIR%

set SENDTODIR=%AppData%\Microsoft\Windows\SendTo

call:link_module_direct topzemen_no_cli open-in-topzemen
call:link_module_direct zemenspawner_no_cli crawl-in-zemenspawner

pause

goto:eof

:link_module_direct
create_shortcut_windows.vbs "%SENDTODIR%\%~2.lnk" "%~1"
exit /B
