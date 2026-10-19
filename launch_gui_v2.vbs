Option Explicit

Dim fso, shell, projectRoot, pythonw, guiEntry, command

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Resolve paths from this launcher so the checkout can live in any user folder.
projectRoot = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = fso.BuildPath(projectRoot, ".venv\Scripts\pythonw.exe")
guiEntry = fso.BuildPath(projectRoot, "gui_v2\main.py")

If Not fso.FileExists(pythonw) Then
    MsgBox "Python da virtualenv não encontrado:" & vbCrLf & pythonw, _
        vbCritical, "ASI Automação v2"
    WScript.Quit 1
End If

If Not fso.FileExists(guiEntry) Then
    MsgBox "Ponto de entrada da GUI v2 não encontrado:" & vbCrLf & guiEntry, _
        vbCritical, "ASI Automação v2"
    WScript.Quit 1
End If

command = """" & pythonw & """ -m gui_v2.main"
shell.CurrentDirectory = projectRoot
shell.Run command, 0, False
