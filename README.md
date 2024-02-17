# VSCode Devcontainer Creation for ROS2 Development
This repository hosts a Python script designed to automate the generation of a VSCode devcontainer specifically tailored for ROS2 development. The script streamlines the process of setting up a development workspace and application directories within a `dev_ws` folder located in the user's home directory.

# Getting Started
## Prerequisites
- Visual Studio Code
- Python installed on your system

## Installation and Usage
1. Clone the Repository: First, clone this repository to your local machine.

2. Run the Script: Execute the provided `create_workspace.py` script. During execution, you will be prompted to input:

    - Your desired workspace name
    - Your desired application name

    For example, if you aim to work on `navigation2` and establish a development environment, you would provide inputs like:
    ```
    - Workspace name: navigation2_ws
    - Application name: navigation_app
    ```
3. Verify the Directory Structure: Post-execution, a folder will be created in your home directory with the following structure:

```
    ├── home/$USER
        ├── dev_ws
            ├──navigation2_ws                    
               ├── src          
                   ├── devcontainer.env 
                   ├── navigation_app         
                        └── .devcontainer
```
4. Set Up in Visual Studio Code:

    - Open VS Code in the `application_name` directory (e.g., `navigation2_app`).
    - Install the necessary VS Code extensions:
        - [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
        - [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
    - After installing the extensions, reload or reopen VS Code in the same folder. A prompt will appear in the bottom right corner, asking if you want to Reopen in Container. Selecting this option will begin the container development process.

## Contributions and Feedback
Contributions, suggestions, and feedback are welcome to enhance the script and its documentation. Please feel free to raise issues or submit pull requests on the repository.

## Happy Coding!
Enjoy a seamless and efficient development experience with your new ROS2 devcontainer setup
