import os
import shutil
import re
import getpass


class WorkspaceCreator:
    def __init__(self, workspace_name, application_name):
        self.workspace_name = workspace_name
        self.application_name = application_name
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

            # Move the cursor to the beginning of the file
            file.seek(0)

            # Save the changes
            file.write(content)

            # Truncate anything remaining as the new data might be smaller than the previous
            file.truncate()

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
    workspace_name = input('Enter workspace name: ')
    application_name = input('Enter application name: ')

    creator = WorkspaceCreator(workspace_name, application_name)
    creator.create_workspace()
