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
        self.dev_ws_path = f"/home/{self.username}/dev_ws"
        self.path = f"{self.dev_ws_path}/{self.workspace_name}/src/{self.application_name}"
        self.devcontainer_folder = ".devcontainer"
        self.devcontainer_env_file = "devcontainer.env"
        self.dest_file = f"{self.dev_ws_path}/{self.workspace_name}/src/devcontainer.env"

    def replace_content(self, file_path):
        with open(file_path, 'r') as file:
            filedata = file.read()

        # Replace the target strings
        filedata = filedata.replace('workspace_name', self.workspace_name)
        filedata = filedata.replace('application_name', self.application_name)

        # Write the file out again
        with open(file_path, 'w') as file:
            file.write(filedata)

    def update_devcontainer_json(self, file_path):
        self.replace_content(file_path)
        with open(file_path, 'r+') as file:
            content = file.read()

            # Use regex to replace the values
            content = re.sub(
                r'(?<=\bname": ")[^"]*', self.workspace_name, content)
            content = re.sub(
                r'(?<=\bCONTAINER_NAME": ")[^"]*', self.application_name, content)

            # Update the distro type
            content = re.sub(
                r'(?<=\bDISTRO": ")[^"]*', self.distro_type, content)

            if self.distro_type == 'WSL':
                content = self.modify_runArgs(content)
            else:
                content = self.modify_runArgs(content)

            # Move the cursor to the beginning of the file
            file.seek(0)

            # Save the changes
            file.write(content)

            # Truncate anything remaining as the new data might be smaller than the previous
            file.truncate()

    def modify_runArgs(self, content: str):
            
            wsl_run_args = [
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
                " --device=/dev/dxg",
                " --device=/dev/dri/card0",
                " --device=/dev/dri/renderD128",
                "--env-file",
                "../devcontainer.env"
            ]
            linux_run_args = [
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
            formatted_args = json.dumps(wsl_run_args if self.distro_type == 'WSL' else linux_run_args, indent=2)

            # Regex pattern to find and replace runArgs
            pattern = r'("runArgs": )(\[.*?\])'
            replacement = r'\1' + formatted_args

            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            return new_content

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def create_workspace(self):
        self.create_directory(self.dev_ws_path)
        self.create_directory(self.path)

        temp_folder = "temp_dir"
        temp_devcontainer = os.path.join(temp_folder, '.devcontainer')
        if os.path.exists(temp_devcontainer) and os.path.isdir(temp_devcontainer):
            shutil.rmtree(temp_devcontainer)

        shutil.copytree(self.devcontainer_folder, temp_devcontainer)

        for subdir, dirs, files in os.walk(temp_devcontainer):
            for file in files:
                if file == 'devcontainer.json':
                    self.update_devcontainer_json(os.path.join(subdir, file))
                else:
                    self.replace_content(os.path.join(subdir, file))

        dest_folder = os.path.join(self.path, ".devcontainer")
        shutil.copytree(temp_devcontainer, dest_folder)
        shutil.rmtree(temp_folder)
        shutil.copy2(self.devcontainer_env_file, self.dest_file)

        print(
            f'Successfully copied .devcontainer and devcontainer.env to to {self.path}')


if __name__ == '__main__':
    print('Username', getpass.getuser())
    print("Please choose the type of distro:")
    print("1. WSL")
    print("2. Linux")
    distro_choice = input("Enter your choice (1/2): ")
    if distro_choice not in ['1', '2']:
        print("Invalid choice. Please enter 1 for WSL or 2 for Linux.")
        exit(1)
    if distro_choice == '1':
        distro_type = 'WSL'
    else:
        distro_type = 'Linux'
    print(f"You have selected: {distro_type}")
    workspace_name = input('Enter workspace name: ')
    application_name = input('Enter application name: ')

    creator = WorkspaceCreator(workspace_name, application_name, distro_type)
    creator.create_workspace()
