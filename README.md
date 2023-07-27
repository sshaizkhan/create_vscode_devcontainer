# Create VSCode Devcontainer
This is a python script based repo that can generate vscode devcontainer for ROS2 development.

This script will create a folder `dev_ws` in the home directory under which user will find their workspace and the development application directories

## How to run this script

To use it, run this python [script](./create_workspace.py) which will ask for following input from user:

- User desired workspace
- User desired application name

For e.g., if I want to work on [navigation2](https://navigation.ros.org/) and create my own development environment for my custom robot. I can use the above script to create a devcontaine environment such that I'll provide the following input for the above :

- Workspace name: navigation2_ws
- Application_name: navigation_app

Once the user has provided the input to the script, a folder will create in the home directory with following directory tree:

### Directory structure

    .
    ├── home/$USER
        ├── dev_ws
            ├──navigation2_ws                    
               ├── src          
                   ├── devcontainer.env 
                   ├── navigation_app         
                        └── .devcontainer


Once you have a similar directory structure, open Visual Studio Code inside the directory `application_name` (navigation2_app) and download the following extensions:

1. Dev Containers: [ms-vscode-remote.remote-containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Remote Development (https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

After downloading the above extensions, reload the VS Code window or reopen VS Code in the same folder and you a small pop-up should be appearing on the bottom right asking if you want to `Reopen in Container`. After clicking on it, sit back, relax and let the container development process complete to start your development.

**HAPPY CODING!!**