Set WshShell = CreateObject("WScript.Shell")

' Get folder where the VBS is located
Set FSO = CreateObject("Scripting.FileSystemObject")
currentFolder = FSO.GetParentFolderName(WScript.ScriptFullName)

python = currentFolder & "\.venv\Scripts\pythonw.exe"
script = currentFolder & "\gui\main.py"

WshShell.Run """" & python & """ """ & script & """", 0

Set WshShell = Nothing