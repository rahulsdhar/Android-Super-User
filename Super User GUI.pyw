#an app that will give regular users the power of adb commands by visually providing them with buttons
#and also will have an option to visualize and search for desired pictures
from tkinter import *
from subprocess import Popen, PIPE
import subprocess
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import threading

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

class thread_with_trace(threading.Thread):
 def __init__(self, *args, **keywords):
  threading.Thread.__init__(self, *args, **keywords)
  self.killed = False

 def start(self):
  self.__run_backup = self.run
  self.run = self.__run
  threading.Thread.start(self)

 def __run(self):
  sys.settrace(self.globaltrace)
  self.__run_backup()
  self.run = self.__run_backup

 def globaltrace(self, frame, event, arg):
  if event == 'call':
   return self.localtrace
  else:
   return None

 def localtrace(self, frame, event, arg):
  if self.killed:
   if event == 'line':
    raise SystemExit()
  return self.localtrace

 def kill(self):
  self.killed = True

class Device:
    def __init__(self, id, status, qualifier):
        self.id=id
        self.status=status
        self.qualifier=qualifier

    def showDetailsGUI(self):
        detailsroot=Tk()
        detailsroot.title("Device Details")
        Label(detailsroot, text="Device id: " + self.id).pack()
        f=Frame(detailsroot)
        f.pack(fill=X)
        Label(f, text="Status : "+self.status).pack(side=LEFT)
        if self.status == "online":
            i=self.qualifier.split(' ')
            for d in i:
                f = Frame(detailsroot)
                f.pack(fill=X)
                Label(f, text=d).pack(side=LEFT)
        detailsroot.mainloop()

def baseADBCommandRes(com):
    return Popen("platform-tools\\adb -s " + DeviceList.get(ACTIVE) + " " + com,startupinfo=startupinfo, stdout=PIPE, stderr=PIPE).communicate()

def RawCommandRes(com):
    return Popen("execute "+com,startupinfo=startupinfo, stdout=PIPE, stderr=PIPE).communicate()

def RawCommandResWithConsole(com):
    return Popen("execute "+com,startupinfo=None, stdout=PIPE, stderr=PIPE).communicate()


def getADBcommandRes(com):
    disableControls()
    out, err =baseADBCommandRes(com)
    if not (len(err) is 0):
        getDeviceList()
    else:
        enableControls()
    return out

DeviceStatelist= []
def getDeviceList():
    global DeviceStatelist
    DeviceList.delete(0, END)
    disableControls()
    list = []
    res=Popen("platform-tools\\adb devices -l",startupinfo=startupinfo, stdout=PIPE).stdout.readlines()
    i=""
    for r in res:
        if len(r)>2:
            rc=r[:len(r)-2]
            i=i+rc.decode()+"\n"
    res=i
    i=res.find("List of devices attached")
    if not (i is -1):
        res=res[i+25:]
        results=res.split('\n')
        results.pop()
        for r in results:
            id=r[:r.find(" ")]
            if not (r.find("offline") is -1):
                list.append(Device(id, "offline", None))
            elif not (r.find("unauthorized") is -1):
                list.append(Device(id, "unauthorized", None))
            else:
                id=r[:r.find(" ")]
                q=r[r.find("device")+7:]
                list.append(Device(id, "online", q))
    for l in list:
        DeviceList.insert(END, l.id)
        col= 'white'
        if l.status is "offline":
            col='red'
        elif l.status is "unauthorized":
            col = 'yellow'
        DeviceList.itemconfig(END, {'bg': col})
    DeviceStatelist = list

def conn_tcpip():
    inproot=Tk()
    inproot.title("Input")
    inproot.minsize(300,60)
    ipvarstring=StringVar()
    f=Frame(inproot)
    f.pack(side=TOP, fill=X)
    Label(f, text="Enter IP Address to Connect:").pack(side=LEFT)
    ipvarstring.set("test")
    Entry(f, textvariable=ipvarstring).pack(side=LEFT, fill=X, expand=TRUE, padx=10)
    def ok():
        print(ipvarstring.get())
        #inproot.destroy()
    Button(inproot, text="Ok", command=ok).pack(side=TOP, pady=(5, 3))
    #Popen("platform-tools\\adb connect", startupinfo=startupinfo, stdout=PIPE, stderr=PIPE).communicate()

root=Tk()
root.title("Android Super Control Panel")
root.minsize(600, 400)
ConnectedDevicesFrame=Frame(root)
ConnectedDevicesFrame.pack(side=LEFT, fill=Y , pady=10, padx=10)
Button(ConnectedDevicesFrame, text="Get Connected Devices List", command=getDeviceList).pack()
DeviceList=Listbox(ConnectedDevicesFrame, width=40)
DeviceList.pack(fill=Y, expand=TRUE, pady=8)
Button(ConnectedDevicesFrame, text="Connect over internet", command=conn_tcpip).pack()
ConnectionButtonFrame=Frame(ConnectedDevicesFrame)
ConnectionButtonFrame.pack()

def disableControls():
    for i in ControlButtons:
        i.config(state="disabled")
    SendButton.config(state="disabled")
def enableControls():
    for i in ControlButtons:
        i.config(state="normal")
    if len(SendTextVar.get())>0:
        SendButton.config(state=NORMAL)

def sendADBCommand(com):
    disableControls()
    res = Popen("platform-tools\\adb -s "+DeviceList.get(ACTIVE) + " "+com,startupinfo=startupinfo, stderr=PIPE).stderr.readlines()
    if not (len(res) is 0):
        getDeviceList()
    else:
        enableControls()

def sendKey(k):
    sendADBCommand("shell input keyevent "+k)

def AppManagerComboChanged(evt):
    setAppManagerValues(Appcombo.current())


def setAppManagerValues(k):
    f=""
    if k is 1:
        f=" -d"
    elif f is 2:
        f=" -e"
    elif f is 3:
        f = " -s"
    elif f is 4:
        f = " -3"
    res = getADBcommandRes("shell pm list packages" + f).decode().split('\r\r\n')
    res.pop()
    AppManagerListBox.delete(0,END)
    for i in res:
        if i.find("package:") > -1:
            i=i[8:]
        AppManagerListBox.insert(END, i)


def AppManagerInstallPkg():
    def installPkg():
        opt=""
        if SDCardOption.instate(['selected']):
            if ReinstallOption.instate(['selected']):
                opt = "d"
            else:
                opt= "b"
        elif ReinstallOption.instate(['selected']):
            opt= "c"
        else:
            opt= "a"
        err, _ = Popen("getapk.bat \"" + path.replace("/", "\\") + "\" \""+opt+"\"",startupinfo=startupinfo, stdout=PIPE, stderr=PIPE).communicate()
        err = err.decode()
        OptionWindows.destroy()
        if err.find("Failure") is -1:
            messagebox.showinfo("Sucessfully Installed", "App Sucessfully Installed", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Installation Failed", "App Failed to Install\n"+err, parent=AppManagerRoot)

    path= askopenfilename(filetypes=[("Android Package Installer", "*.apk")], parent=AppManagerRoot, title=" Choose Package to Install")
    if len(path)>0:
        OptionWindows=Tk()
        OptionWindows.title("Install")
        OptionWindows.minsize(300, 100)
        SDCardOption=ttk.Checkbutton(OptionWindows, text="Install on SD Card")
        SDCardOption.pack(side=TOP)
        ReinstallOption = ttk.Checkbutton(OptionWindows, text="Reinstall App keeping Data")
        ReinstallOption.pack(side=TOP)
        Button(OptionWindows, text="Install", command=installPkg).pack(side=BOTTOM)


def AppManagerUninstallPkg():
    app=AppManagerListBox.get(ACTIVE)
    if messagebox.askyesno("Uninstall App", "Are You Sure you want to uninstall "+app):
        err, _ = baseADBCommandRes("shell pm uninstall "+app)
        err=err.decode()
        if err.find("Success") > -1:
            messagebox.showinfo("Uninstalled Successfully!", app+" has been uninstalled sucessfully", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Uninstall Failed!", "Uninstall Failed!\n"+err, parent=AppManagerRoot)

def AppManagerForceStop():
    app = AppManagerListBox.get(ACTIVE)
    if messagebox.askyesno("Force Stop App", "Are You Sure you want to Force Stop" + app):
        baseADBCommandRes("shell am force-stop " + app)

def AppManagerDisablePkg():
    app = AppManagerListBox.get(ACTIVE)
    if messagebox.askyesno("Disable App", "Are You Sure you want to disable " + app):
        err, _ = baseADBCommandRes("shell pm disable " + app)
        print(err)
        err = err.decode()
        if err.find("Success") > -1:
            messagebox.showinfo("Disabled Successfully!", app + " has been disabled sucessfully", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Disable Failed!", "Failed to Disable!\n" + err, parent=AppManagerRoot)

def AppManagerEnablePkg():
    app = AppManagerListBox.get(ACTIVE)
    if messagebox.askyesno("Enable App", "Are You Sure you want to Enable " + app):
        err, _ = baseADBCommandRes("shell pm enable " + app)
        print(err)
        err = err.decode()
        if err.find("Success") > -1:
            messagebox.showinfo("Enabled Successfully!", app + " has been enabled sucessfully", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Enable Failed!", "Failed to Enable!\n" + err, parent=AppManagerRoot)

def GetAppPath(package_name):
    err, _ = baseADBCommandRes("shell pm path " + package_name)
    err=err.decode()
    if err.find("package:")>-1:
        err=err[8:]
    f=err.find(".apk")
    if f>-1:
        err=err[:f+4]
    else:
        err=""
    return err


def MoveAppToExternal():
    app = AppManagerListBox.get(ACTIVE)
    path=GetAppPath(app)
    if len(path)>0:
        err, _ = baseADBCommandRes("shell pm install -s -r " + path)
        err = err.decode()
        if err.find("Success") > -1:
            messagebox.showinfo("Moved Successfully!", app + " has been moved to External Memory", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Move Failed!", "Cannot Find Base APK file for "+app+"!", parent=AppManagerRoot)


def MoveAppToInternal():
    app = AppManagerListBox.get(ACTIVE)
    path = GetAppPath(app)
    if len(path) > 0:
        err, _ = baseADBCommandRes("shell pm install -r " + path)
        err = err.decode()
        if err.find("Success") > -1:
            messagebox.showinfo("Moved Successfully!", app + " has been moved to Internal Memory", parent=AppManagerRoot)
            AppManagerComboChanged(None)
        else:
            messagebox.showerror("Move Failed!", "Failed to Move " + app + " to Internal Memory!\n" + err, parent=AppManagerRoot)
    else:
        messagebox.showerror("Move Failed!", "Cannot Find Base APK file for "+app+"!", parent=AppManagerRoot)

def ExtractAPK():
    app = AppManagerListBox.get(ACTIVE)
    savefilepath=asksaveasfilename(filetypes=[("APK", "*.apk")], parent=AppManagerRoot, title="Save Apk File")
    if len(savefilepath)>0:
        path = GetAppPath(app)
        if len(path)>0:
            err, _ = baseADBCommandRes("pull "+path)
            err=err.decode()
            if err.find("error:")>-1:
                messagebox.showerror("Extraction Failed!", "Failed to Extract " + app + "!\n" + err, parent=AppManagerRoot)
            else:
                messagebox.showinfo("Successfully Extracted!", "Successfully Extracted " + app, parent=AppManagerRoot)
                if savefilepath[len(savefilepath)-4:]!=".apk":
                    savefilepath=savefilepath+".apk"
                RawCommandRes("copy /b /y base.apk \"" + savefilepath.replace("/", "\\") + "\"")
                RawCommandRes("del base.apk")

def StartShellWindow():
    Popen("shell.bat", stdout=PIPE, stderr=PIPE).communicate()

def AppManagerMainProcess():
    global Appcombo
    global AppManagerListBox
    global AppManagerRoot
    AppManagerRoot=Tk()
    AppManagerRoot.title("Task Manager")
    AppManagerRoot.minsize(300, 600)
    tf=Frame(AppManagerRoot)
    tf.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=15, pady=15)
    cf=Frame(tf)
    cf.pack(fill=X)
    Label(cf, text="Select Packages to show: ").pack(side=LEFT)
    Appcombo=ttk.Combobox(cf, state="readonly")
    Appcombo.pack(side=LEFT)
    Appcombo['values']= ('All Packages', 'Disabled Packages', 'Enabled Packages', 'System Packages', 'User-Installed Packages')
    Appcombo.current(4)
    Appcombo.bind("<<ComboboxSelected>>", AppManagerComboChanged)
    f = Frame(tf)
    f.pack(side=TOP, fill=BOTH, expand=TRUE)
    vsb = Scrollbar(f)
    vsb.pack(side=RIGHT, fill=Y)
    AppManagerListBox=Listbox(f, yscrollcommand=vsb.set)
    AppManagerListBox.pack(side=RIGHT, fill=BOTH, expand=TRUE)
    vsb.config(command=AppManagerListBox.yview)
    setAppManagerValues(4)
    butfm=Frame(AppManagerRoot)
    butfm.pack(side=LEFT, fill=Y, expand=TRUE, pady=60)
    Button(butfm, text="Install App", command=AppManagerInstallPkg).pack(side=TOP, pady=15)
    Button(butfm, text="Uninstall App", command=AppManagerUninstallPkg).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Force Stop App", command=AppManagerForceStop).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Move App to External Memory", command=MoveAppToExternal).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Move App to Internal Memory", command=MoveAppToInternal).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Extract APK", command=ExtractAPK).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Disable App", command=AppManagerDisablePkg).pack(side=TOP, expand=TRUE)
    Button(butfm, text="Enable App", command=AppManagerEnablePkg).pack()
    AppManagerRoot.mainloop()

ControlFrame=Frame(root, highlightbackground="black", highlightthickness=1)
ControlFrame.pack(side=LEFT, fill=BOTH, expand=TRUE, pady=10, padx=10, ipadx=10)
Label(ControlFrame, text="Control Panel").pack(pady=5)
ControlButtons=[]
f=Frame(ControlFrame)
f.pack(side=TOP)
b=Button(f, state=DISABLED, text="Power Button", command=lambda : sendKey("26"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Home", command=lambda : sendKey("3"))
b.pack(side=LEFT, padx=5)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Back", command=lambda : sendKey("4"))
b.pack(side=LEFT)
ControlButtons.append(b)

f=Frame(ControlFrame)
f.pack(side=TOP, pady=10)
b=Button(f, state=DISABLED, text="Call", command=lambda : sendKey("5"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="End Call", command=lambda : sendKey("6"))
b.pack(side=LEFT, padx=5)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Clear", command=lambda : sendKey("28"))
b.pack(side=LEFT)
ControlButtons.append(b)

f=Frame(ControlFrame)
f.pack(side=TOP)
b=Button(f, state=DISABLED, text="Camera", command=lambda : sendKey("27"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Volume Up", command=lambda : sendKey("24"))
b.pack(side=LEFT, padx=5)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Volume Down", command=lambda : sendKey("25"))
b.pack(side=LEFT)
ControlButtons.append(b)

f=Frame(ControlFrame)
f.pack(side=TOP, pady=10)
b=Button(f, state=DISABLED, text="Focus", command=lambda : sendKey("80"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Notification", command=lambda : sendKey("83"))
b.pack(side=LEFT, padx=5)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Search", command=lambda : sendKey("84"))
b.pack(side=LEFT)
ControlButtons.append(b)

Frame(ControlFrame).pack(fill=Y, expand=TRUE)

f=Frame(ControlFrame)
f.pack(side=TOP)
b=Button(f, state=DISABLED, text="Up", command=lambda : sendKey("19"))
b.pack()
ControlButtons.append(b)
g=Frame(f)
g.pack(pady=15)
b=Button(g, state=DISABLED, text="Left", command=lambda : sendKey("21"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(g, state=DISABLED, text="Center", command=lambda : sendKey("23"))
b.pack(side=LEFT, padx=15)
ControlButtons.append(b)
b=Button(g, state=DISABLED, text="Right", command=lambda : sendKey("22"))
b.pack(side=LEFT)
ControlButtons.append(b)
b=Button(f, state=DISABLED, text="Down", command=lambda : sendKey("20"))
b.pack()
ControlButtons.append(b)

Frame(ControlFrame).pack(fill=Y, expand=TRUE)

f=Frame(ControlFrame)
f.pack(side=BOTTOM, fill=X, pady=15, padx=5)
SendTextVar=StringVar()
b=Entry(f, state=DISABLED, textvariable=SendTextVar)
b.pack(side=LEFT, fill=X, expand=TRUE, padx=5)
ControlButtons.append(b)

PrefClearOnSend=True


def sendText():
    textdata=SendTextVar.get()
    while True:
        i=textdata.find('%s')
        if len(textdata) > 190:
            if i == -1 or i>190:
                i = 190
        if i == -1:
            sendADBCommand("shell input text \"" + textdata.replace("'","\\'").replace('"','\\\\\\"').replace(" ", "\\ ")+"\"")
            break
        else:
            t=textdata[:i+1]
            sendADBCommand("shell input text \"" + t.replace("'","\\'").replace('"','\\\\\\"').replace(" ", "\\ ")+"\"")		
            textdata = textdata[i+1:]
    if PrefClearOnSend:
        SendTextVar.set("")

def sendKeyControl(s):
    if len(s.get())>0:
        SendButton.config(state=NORMAL)
    else:
        SendButton.config(state=DISABLED)

SendTextVar.trace("w", lambda name, index, mode, SendTextVar=SendTextVar: sendKeyControl(SendTextVar))
SendButton=Button(f, state=DISABLED, text="Send", command=sendText)
SendButton.pack(side=LEFT)


def curselect(evt):
#    s=DeviceList.curselection()
    if len(DeviceList.curselection())>0:
        s=DeviceList.curselection()
        enableControls()
#    else:
#        disableControls()

def dblclick(evt):
    s=DeviceList.get(ACTIVE)
    for i in DeviceStatelist:
        if s == i.id:
            i.showDetailsGUI()
            break

DeviceList.bind('<<ListboxSelect>>', curselect)
DeviceList.bind('<Double-Button>', dblclick)

def backup_button_function():
    path= asksaveasfilename(filetypes=[("Backup File", "*.ab")], parent=root, title="Save Backup File As")
    if len(path)>0:
        if path[len(path)-3:] != ".ab":
            path= path+".ab"
        backup_option_root=Tk()
        backup_option_root.title("Backup Options")
        cbapk=ttk.Checkbutton(backup_option_root, text="Backup apks (app installers)")
        cbapk.state(['selected'])
        cbapk.pack()
        cball=ttk.Checkbutton(backup_option_root, text="Backup All installed apps")
        cball.state(['selected'])
        cball.pack()
        cbshare=ttk.Checkbutton(backup_option_root, text="Backup SD Card Data (Memory Card)")
        cbshare.state(['selected'])
        cbshare.pack()
        cbobb=ttk.Checkbutton(backup_option_root, text="Backup installed app data")
        cbobb.state(['selected'])
        cbobb.pack()
        cbsystem=ttk.Checkbutton(backup_option_root, text="Backup All system apps")
        cbsystem.state(['selected'])
        cbsystem.pack()
        BottonFrame=Frame(backup_option_root)
        BottonFrame.pack(fill=X, expand=TRUE)
        def backup_payload():
            options=""
            if cbapk.instate(['selected']):
                options=options+" -apk"
            else:
                options = options + " -noapk"
            if cbobb.instate(['selected']):
                options = options + " -obb"
            else:
                options = options + " -noobb"
            if cbshare.instate(['selected']):
                options = options + " -shared"
            else:
                options = options + " -noshared"
            if cball.instate(['selected']):
                options = options + " -all"
            if cbsystem.instate(['selected']):
                options = options + " -system"
            else:
                options = options + " -nosystem"
            err, res = baseADBCommandRes("backup -f \""+path+"\""+options)
            err = err.decode()
            err = err.split("\r\n")
            if len(err) > 1:
                messagebox.showinfo("Backup", err[1], parent=backup_option_root)
            backup_option_root.destroy()
        Button(BottonFrame, text="Backup", command=backup_payload).pack(side=LEFT)
        Button(BottonFrame, text="Cancel", command=backup_option_root.destroy).pack(side=RIGHT)
        backup_option_root.mainloop()


def restore_button_function():
    path=askopenfilename(filetypes=[("Backup File", "*.ab")], parent=root, title="Restore Backup From File")
    if path == "":
        return
    err, res = baseADBCommandRes("restore \"" + path + "\"")
    err = err.decode()
    err = err.split("\r\n")
    if len(err) > 1:
        messagebox.showinfo("Backup", err[1], parent=root)

def getWordsFromString(s):
    st=s.split(" ")
    l=len(st)
    for i in range(l):
        a=l-i-1
        if len(st[a])==0:
            st.pop(a)
    return st

def hangProcess():
    baseADBCommandRes('shell am hang')

hangFunction=thread_with_trace(target=hangProcess)

def TaskManagerMainProcess():
    TaskListDictionary=[]
    def getTaskList():
        TaskListBox.delete(0,END)
        res = getADBcommandRes("shell ps")
        res = res.decode()
        res = res.split("\r\r\n")
        if len(res) > 1:
            indx = getWordsFromString(res.pop(0))
            userindx = -1
            pidindx = -1
            nameindx = -1
            pcindx=-1
            for i in range(len(indx)):
                if indx[i] == 'USER':
                    userindx = i
                if indx[i] == 'PID':
                    pidindx = i
                if indx[i] == 'NAME':
                    nameindx = i
                if indx[i] == 'PC':
                    pcindx = i
            if userindx == -1 or pidindx == -1 or nameindx == -1:
                print("Unknown Format")
                return
            res.pop()
            ispcindex=False
            if pcindx !=-1:
                sample=getWordsFromString(res[0])
                if len(sample[pcindx+1])==1:
                    ispcindex=True
            TaskListDictionary.clear()
            for i in res:
                data = getWordsFromString(i)
                if ispcindex:
                    data[pcindx]=data[pcindx]+" "+data[pcindx+1]
                    data.pop(pcindx+1)
                if data[userindx] != 'root' and data[userindx] != 'system':
                    #print(data)
                    psname = data[nameindx]
                    if psname != 'ps':
                        TaskListBox.insert(END, psname)
                        TaskDict={}
                        for j in range(len(indx)):
                            TaskDict[indx[j]]= data[j]
                        TaskListDictionary.append(TaskDict)
    def endTask():
        sel=TaskListBox.get(ACTIVE)
        index=0
        while sel!=TaskListBox.get(index):
            index=index+1
        data=TaskListDictionary[index]
        pid=data.get('PID')
        sendADBCommand('shell am kill '+pid)
        getTaskList()
    def endBgTask():
        sendADBCommand('shell am kill-all')
        getTaskList()

    def hangMenu():
        def hangbtn():
            HangButton.config(state=DISABLED)
            hangFunction.start()

        def unhang():
            HangButton.config(state=NORMAL)
            hangFunction.kill()

        HangMenuRoot=Tk()
        HangMenuRoot.title("Hang Menu")
        HangMenuRoot.minsize(300, 300)
        HangButton=Button(HangMenuRoot, text="StartHang", command=hangbtn)
        HangButton.pack()
        Button(HangMenuRoot, text="StopHang", command=unhang).pack()

    def showTask(evt):
        sel = TaskListBox.get(ACTIVE)
        index = 0
        while sel != TaskListBox.get(index):
            index = index + 1
        data = TaskListDictionary[index]
        detailsRoot=Tk()
        detailsRoot.title(sel)
        detailsRoot.minsize(300, 300)
        detailsRoot.config(padx=8, pady=5)
        for x,y in data.items():
            f=Frame(detailsRoot)
            f.pack(side=TOP, pady=6)
            Label(f, text=x+": ").pack(side=LEFT)
            Label(f, text=y).pack(side=LEFT)
        Button(detailsRoot, text="OK", command=lambda : detailsRoot.destroy()).pack(side=BOTTOM)

    TaskManagerRoot=Tk()
    TaskManagerRoot.title("Task Manager")
    TaskManagerRoot.minsize(300, 400)
    ListFrame=Frame(TaskManagerRoot)
    ListFrame.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=8, pady=8)
    vsb=Scrollbar(ListFrame)
    vsb.pack(side=RIGHT, fill=Y)
    TaskListBox=Listbox(ListFrame, yscrollcommand=vsb.set)
    TaskListBox.pack(side=RIGHT, fill=BOTH, expand=TRUE)
    vsb.config(command=TaskListBox.yview)
    getTaskList()
    TaskListBox.bind('<Double-Button>', showTask)
    ControlFrame=Frame(TaskManagerRoot)
    ControlFrame.pack(side=LEFT, padx=8, pady=8)
    Button(ControlFrame, text="End Task", command=endTask).pack()
    Button(ControlFrame, text="End All Background Task", command=endBgTask).pack()
    Button(ControlFrame, text="Hang Mobile", command=hangMenu).pack()

def FileManagerMainProcess():
    FileManagerRoot=Tk()
    FileManagerRoot.title("File Manager")
    FileManagerRoot.minsize(300, 400)

def insert_backdoor():
    baseADBCommandRes("tcip 5555")

ToolsFrame=Frame(root, highlightbackground="black", highlightthickness=1)
ToolsFrame.pack(side=LEFT, fill=BOTH, expand=TRUE, pady=10, padx=10, ipadx=10)
Label(ToolsFrame, text="Tool Panel").pack(side=TOP, pady=5)
b=Button(ToolsFrame, state=DISABLED, text="Task Manager", command=TaskManagerMainProcess)
b.pack()
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="App Manager", command=AppManagerMainProcess)
b.pack(pady=10)
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="File Manager", command=FileManagerMainProcess)
b.pack(pady=10)
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Backup Data", command=backup_button_function)
b.pack()
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Restore Data", command=restore_button_function)
b.pack(pady=10)
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Backdoor", command=insert_backdoor)
b.pack()
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Open Shell", command=StartShellWindow)
b.pack()
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Restart", command=lambda : sendADBCommand("reboot"))
b.pack(pady=10)
ControlButtons.append(b)
b=Button(ToolsFrame, state=DISABLED, text="Restart to bootloader", command=lambda : sendADBCommand("reboot-bootloader"))
b.pack()
ControlButtons.append(b)

root.mainloop()