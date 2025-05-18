import os
import shutil
import re
import getpass
import json

class WorkspaceCreator:
    def __init__(self, workspace_name, application_name, distro_type):
        self.workspace_name = workspace_name
        self.application_name = application_name
        self.distro_type = distro_type
        self.username = getpass.getuser()
        self.use_novnc = False
        if self.distro_type == "Mac":
            self.dev_ws_path = f"/Users/{self.username}/dev_ws"
        else:
            self.dev_ws_path = f"/home/{self.username}/dev_ws"
        self.path = f"{self.dev_ws_path}/{self.workspace_name}/src/{self.application_name}"
        self.devcontainer_folder = ".devcontainer"
        self.devcontainer_env_file = "devcontainer.env"
        self.dest_file = f"{self.dev_ws_path}/{self.workspace_name}/src/devcontainer.env"

    def replace_content(self, file_path):
        try:
            with open(file_path, 'r') as file:
                filedata = file.read()

            filedata = filedata.replace('workspace_name', self.workspace_name)
            filedata = filedata.replace('application_name', self.application_name)

            with open(file_path, 'w') as file:
                file.write(filedata)
        except Exception as e:
            print(f"Error replacing content in {file_path}: {e}")
    
    def add_novnc_to_post_create(self, post_create_path):
        """Add noVNC setup commands to post_create.bash"""
        if not self.use_novnc:
            return
        
        novnc_setup = """
    # noVNC setup
    # Create directory for VNC (if it doesn't exist already)
    mkdir -p /root/.vnc

    # Setup VNC password
    if [ ! -f /root/.vnc/passwd ]; then
    x11vnc -storepasswd "${VNC_PASSWORD:-password}" /root/.vnc/passwd
    fi

    # Make sure novnc startup script is executable
    if [ -f /usr/local/bin/novnc_startup.sh ]; then
    chmod +x /usr/local/bin/novnc_startup.sh
    else
    echo "Warning: novnc_startup.sh not found in /usr/local/bin"
    
    # Copy it if it exists in the .devcontainer folder
    if [ -f /workspaces/*/src/*/.devcontainer/novnc_startup.sh ]; then
        cp /workspaces/*/src/*/.devcontainer/novnc_startup.sh /usr/local/bin/
        chmod +x /usr/local/bin/novnc_startup.sh
        echo "Copied novnc_startup.sh to /usr/local/bin"
    fi
    fi

    # Start noVNC in the background if not already running
    if ! pgrep -f "novnc" > /dev/null; then
    echo "Starting noVNC server..."
    nohup /usr/local/bin/novnc_startup.sh > /tmp/novnc.log 2>&1 &
    echo "noVNC started. Access at http://localhost:6080/vnc.html"
    else
    echo "noVNC is already running. Access at http://localhost:6080/vnc.html"
    fi
    """
        
        try:
            if os.path.exists(post_create_path):
                with open(post_create_path, 'r') as f:
                    content = f.read()
                    
                if "# noVNC setup" not in content:
                    with open(post_create_path, 'a') as f:
                        f.write(novnc_setup)
                        
                    print(f"Added noVNC setup to {post_create_path}")
        except Exception as e:
            print(f"Error adding noVNC setup to post_create.bash: {e}")

    def update_devcontainer_json(self, file_path):
        try:
            # First just replace basic content
            self.replace_content(file_path)
            
            # Then do the more complex regex replacements
            with open(file_path, 'r') as file:
                content = file.read()

            # Update basic fields with regex
            content = re.sub(r'(?<=\bname": ")[^"]*', self.workspace_name, content)
            content = re.sub(r'(?<=\bCONTAINER_NAME": ")[^"]*', self.application_name, content)
            content = re.sub(r'(?<=\bDISTRO": ")[^"]*', self.distro_type, content)
            
            # Update runArgs
            if self.distro_type == 'WSL':
                runargs = self.get_wsl_run_args()
            elif self.distro_type == 'Linux':
                runargs = self.get_linux_run_args()
            elif self.distro_type == 'Mac':
                runargs = self.get_mac_run_args()
            else:
                runargs = []
                
            runargs_str = json.dumps(runargs, indent=2)
            pattern = r'("runArgs": )(\[.*?\])'
            content = re.sub(pattern, r'\1' + runargs_str, content, flags=re.DOTALL)
            
            # Add noVNC settings if enabled
            if self.use_novnc:
                # Add VNC password to containerEnv
                if '"containerEnv": {' in content:
                    # If containerEnv already exists, add to it
                    content = content.replace('"containerEnv": {', '"containerEnv": {\n    "VNC_PASSWORD": "password",')
                else:
                    # Find the first { and add containerEnv right after it
                    first_brace = content.find('{')
                    if first_brace != -1:
                        content = content[:first_brace+1] + '\n  "containerEnv": {\n    "VNC_PASSWORD": "password"\n  },' + content[first_brace+1:]
                
                # Add postStartCommand
                if '"postStartCommand": "' in content:
                    # If postStartCommand already exists, prepend to it
                    content = content.replace('"postStartCommand": "', '"postStartCommand": "/usr/local/bin/novnc_startup.sh & ')
                else:
                    # Find the first { and add postStartCommand right after it
                    first_brace = content.find('{')
                    if first_brace != -1:
                        content = content[:first_brace+1] + '\n  "postStartCommand": "/usr/local/bin/novnc_startup.sh &",' + content[first_brace+1:]
                
                # Add forwardPorts
                if '"forwardPorts": [' in content:
                    # If forwardPorts already exists, add to it
                    content = content.replace('"forwardPorts": [', '"forwardPorts": [\n    6080,')
                else:
                    # Find the first { and add forwardPorts right after it
                    first_brace = content.find('{')
                    if first_brace != -1:
                        content = content[:first_brace+1] + '\n  "forwardPorts": [6080],' + content[first_brace+1:]
            
            with open(file_path, 'w') as file:
                file.write(content)
            
        except Exception as e:
            print(f"Error updating devcontainer.json: {e}")

    def get_wsl_run_args(self):
        args = [
            "--cap-add=SYS_PTRACE",
            "--security-opt=seccomp=unconfined",
            "--privileged",
            "--network=host",
            "--env=NVIDIA_VISIBLE_DEVICES=all",
            "--env=NVIDIA_DRIVER_CAPABILITIES=all",
            "--env=DISPLAY",
            "--env=WAYLAND_DISPLAY",
            "--env=PULSE_SERVER",
            "--gpus",
            "all",
            "--env=QT_X11_NO_MITSHM=1",
            "--volume=tmp/.X11-unix:/tmp/.X11-unix",
            "--volume=/mnt/wslg:/mnt/wslg",
            "--volume=/usr/lib/wsl:/usr/lib/wsl",
            "--device-cgroup-rule=c 189:* rmw",
            "--device=/dev/dxg",
            "--device=/dev/dri/card0",
            "--device=/dev/dri/renderD128",
            "--env-file",
            "../devcontainer.env"
        ]
        
        if self.use_novnc:
            args.append("--publish=6080:6080")
            
        return args

    def get_linux_run_args(self):
        args = [
            "--cap-add=SYS_PTRACE",
            "--security-opt=seccomp=unconfined",
            "--privileged",
            "--network=host",
            "--env=NVIDIA_VISIBLE_DEVICES=all",
            "--env=NVIDIA_DRIVER_CAPABILITIES=all",
            "--env=DISPLAY",
            "--gpus",
            "all",
            "--env=QT_X11_NO_MITSHM=1",
            "-v",
            "/tmp/.X11-unix:/tmp/.X11-unix:rw",
            "--volume=/etc/X11:/etc/X11:rw",
            "--volume=/dev:/dev:rw",
            "--device-cgroup-rule=c 189:* rmw",
            "--volume=/dev/bus/usb:/dev/bus/usb:rw",
            "--volume=/dev/input:/dev/input:rw",
            "--env-file",
            "../devcontainer.env"
        ]
        
        if self.use_novnc:
            args.append("--publish=6080:6080")
            
        return args

    def get_mac_run_args(self):
        args = [
            "--cap-add=SYS_PTRACE",
            "--security-opt=seccomp=unconfined",
            "--env=DISPLAY=host.docker.internal:0",
            "--env=QT_X11_NO_MITSHM=1",
            "-v",
            "/tmp/.X11-unix:/tmp/.X11-unix:rw",
            "--platform=linux/arm64",
            "--env-file",
            "../devcontainer.env"
        ]
        
        if self.use_novnc:
            args.append("--publish=6080:6080")
            
        return args

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def create_novnc_startup_script(self, dest_path):
        """Creates the noVNC startup script in the destination path"""
        if not self.use_novnc:
            return
            
        script_content = """#!/bin/bash
set -e

# Start display
Xvfb :1 -screen 0 1920x1080x16 -ac -pn -noreset &

# Set display
export DISPLAY=:1

# Start window manager
fluxbox &

# Start VNC server
x11vnc -forever -usepw -shared -rfbport 5900 -display :1 &

# Start noVNC
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
"""
        script_path = os.path.join(dest_path, "novnc_startup.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Make executable
        print(f"Created noVNC startup script at {script_path}")

    def update_dockerfile(self, dest_path):
        """Adds noVNC installation to the Dockerfile"""
        if not self.use_novnc:
            return
            
        dockerfile_path = os.path.join(dest_path, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            print(f"Warning: Dockerfile not found at {dockerfile_path}")
            return
            
        novnc_install = """
# Install NoVNC
RUN apt-get update && apt-get install -y \\
    x11vnc \\
    xvfb \\
    fluxbox \\
    net-tools \\
    novnc \\
    && apt-get clean

# Create directory for VNC
RUN mkdir -p /root/.vnc

# Setup VNC password
RUN x11vnc -storepasswd ${VNC_PASSWORD:-password} /root/.vnc/passwd

# Copy the noVNC start script
COPY .devcontainer/novnc_startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/novnc_startup.sh
"""
        
        try:
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                
            if "# Install NoVNC" not in content:
                # Find a good place to insert the novnc installation
                if "# Install dependencies" in content:
                    content = content.replace("# Install dependencies", "# Install dependencies" + novnc_install)
                elif "RUN apt-get update" in content:
                    # Find the first apt-get update line
                    apt_index = content.find("RUN apt-get update")
                    if apt_index != -1:
                        # Find the end of that line
                        line_end = content.find("\n", apt_index)
                        if line_end != -1:
                            content = content[:line_end+1] + novnc_install + content[line_end+1:]
                else:
                    # Append to the end of the file
                    content += "\n" + novnc_install
                    
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
                    
                print(f"Updated Dockerfile at {dockerfile_path} with noVNC installation")
        except Exception as e:
            print(f"Error updating Dockerfile: {e}")

    def update_post_scripts(self):
        """Updates post_create.bash and post_attach.bash with noVNC information"""
        if not self.use_novnc:
            return
            
        novnc_message = """
echo "
-----------------------------------------
🖥️  GUI Applications with noVNC
-----------------------------------------
Access GUI applications through your browser:
  http://localhost:6080/vnc.html

Default VNC password: password
-----------------------------------------
"
"""
        
        for script_name in ["post_create.bash", "post_attach.bash"]:
            script_path = os.path.join(self.path, ".devcontainer", script_name)
            if os.path.exists(script_path):
                try:
                    with open(script_path, 'r') as f:
                        content = f.read()
                        
                    if "GUI Applications with noVNC" not in content:
                        with open(script_path, 'a') as f:
                            f.write(novnc_message)
                            
                        print(f"Updated {script_name} with noVNC information")
                except Exception as e:
                    print(f"Error updating {script_name}: {e}")

    def create_workspace(self):
        self.create_directory(self.dev_ws_path)
        self.create_directory(self.path)

        temp_folder = "temp_dir"
        temp_devcontainer = os.path.join(temp_folder, '.devcontainer')
        if os.path.exists(temp_devcontainer) and os.path.isdir(temp_devcontainer):
            shutil.rmtree(temp_devcontainer)

        shutil.copytree(self.devcontainer_folder, temp_devcontainer)

        # Create noVNC startup script if needed
        if self.use_novnc:
            self.create_novnc_startup_script(temp_devcontainer)
        
        if self.use_novnc:
            self.update_post_scripts()
            post_create_path = os.path.join(self.path, ".devcontainer", "post_create.bash")
            self.add_novnc_to_post_create(post_create_path)

        for subdir, dirs, files in os.walk(temp_devcontainer):
            for file in files:
                file_path = os.path.join(subdir, file)
                if file == 'devcontainer.json':
                    self.update_devcontainer_json(file_path)
                else:
                    self.replace_content(file_path)

        # Update Dockerfile for noVNC if needed
        if self.use_novnc:
            self.update_dockerfile(temp_devcontainer)

        dest_folder = os.path.join(self.path, ".devcontainer")
        shutil.copytree(temp_devcontainer, dest_folder)
        shutil.rmtree(temp_folder)
        shutil.copy2(self.devcontainer_env_file, self.dest_file)

        # Update post scripts with noVNC information
        if self.use_novnc:
            self.update_post_scripts()

        print(f'Successfully copied .devcontainer and devcontainer.env to {self.path}')
        
        if self.use_novnc:
            print("""
noVNC has been enabled for this workspace. After building the container:
1. Connect to http://localhost:6080/vnc.html in your browser
2. Use password: password
3. You can run GUI applications inside the container and access them through your browser
""")


if __name__ == '__main__':
    print('Username', getpass.getuser())
    print("Please choose the type of distro:")
    print("1. WSL")
    print("2. Linux")
    print("3. Mac (Apple Silicon)")
    distro_choice = input("Enter your choice (1/2/3): ")
    if distro_choice not in ['1', '2', '3']:
        print("Invalid choice. Please enter 1 for WSL, 2 for Linux, or 3 for Mac.")
        exit(1)
    if distro_choice == '1':
        distro_type = 'WSL'
    elif distro_choice == '2':
        distro_type = 'Linux'
    else:
        distro_type = 'Mac'
    print(f"You have selected: {distro_type}")
    workspace_name = input('Enter workspace name: ')
    application_name = input('Enter application name: ')

    use_novnc = input("Do you want to enable noVNC for GUI applications? (y/n): ").lower() == 'y'
    if use_novnc:
        print("Enabling noVNC for GUI applications.")
    else:
        print("noVNC for GUI applications is disabled. Using X11 forwarding instead.")
    
    creator = WorkspaceCreator(workspace_name, application_name, distro_type)
    creator.use_novnc = use_novnc 
    creator.create_workspace()