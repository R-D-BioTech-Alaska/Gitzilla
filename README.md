# Gitzilla

![License](https://img.shields.io/github/license/R-D-BioTech-Alaska/Gitzilla)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![GitHub stars](https://img.shields.io/github/stars/R-D-BioTech-Alaska/Gitzilla?style=social)

Gitzilla is a **minimalist and extensible GUI tool** built with Python's Tkinter library. It streamlines the process of managing SSH keys, connecting to GitHub repositories, and performing essential Git upload operations directly from a user-friendly interface. Whether you're a developer looking to simplify your workflow or someone new to Git and GitHub, Gitzilla offers an intuitive solution to handle your repository interactions seamlessly.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Generate SSH Key](#1-generate-ssh-key)
  - [2. Add SSH Key to GitHub](#2-add-ssh-key-to-github)
  - [3. Connect to GitHub Repository](#3-connect-to-github-repository)
  - [4. Upload Files](#4-upload-files)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **SSH Key Generation:** Easily generate a new SSH key pair directly from the GUI.
- **Public Key Management:** View a snippet of your public key and copy it to the clipboard for quick access.
- **GitHub Integration:** Connect to your GitHub repositories using your username and repository name.
- **Repository Cloning:** Clone repositories securely via SSH without manual command-line operations.
- **File Uploading:** Upload files to your repository with just a few clicks.
- **Drag & Drop Support:** (Optional) Drag and drop files into the application for easy selection.
- **Progress Tracking:** Visual progress bar to monitor ongoing operations.
- **Status Updates:** Real-time status messages to keep you informed of the application's actions and any issues.

## Prerequisites

Before installing and using Gitzilla, ensure you have the following installed on your system:

1. **Python 3.6 or Higher:** Gitzilla is built using Python. You can download Python from the [official website](https://www.python.org/downloads/).

2. **Git:** Necessary for cloning and interacting with GitHub repositories. Download Git from the [official website](https://git-scm.com/downloads).

3. **Tkinter:** Usually included with Python installations. If not, install it using your package manager.

4. **Optional - `tkdnd_wrapper`:** Enables drag and drop functionality within the application.

   - **Installation:**
     ```bash
     pip install tkdnd-wrapper
     ```

## Installation

1. **Clone the Gitzilla Repository:**
   

   ```bash
   git clone https://github.com/R-D-BioTech-Alaska/Gitzilla.git
   ```

2. **Navigate to the Project Directory:**
   
   ```bash
   cd Gitzilla
   ```

3. **Install Required Python Packages:**
   
   It's recommended to use a virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Note:** If you encounter issues with `tkdnd_wrapper`, ensure it's installed correctly or proceed without drag and drop functionality.

4. **Run the Application:**
   
   ```bash
   python gitzilla.py
   ```

## Usage

Gitzilla's intuitive GUI guides you through each step. Below is a step-by-step guide to using its core features.

### 1. Generate SSH Key

1. **Open Gitzilla:**
   
   Launch the application by running `python Gitzilla.py`, `py Gitzilla.py` or just double click `Gitzilla.py`

2. **Generate SSH Key:**
   
   - Click on the **"Generate SSH Key"** button.
   - A new SSH key pair (`id_rsa_gitzilla` and `id_rsa_gitzilla.pub`) will be created in the `~/.gitzilla_keys` directory.
   - A snippet of your public key will be displayed, and the full key will be copied to your clipboard automatically.
   - You can also click copy to clipboard just in case.

### 2. Add SSH Key to GitHub

1. **Navigate to GitHub SSH Settings:**
   
   Go to [GitHub SSH Keys](https://github.com/settings/keys).

2. **Add New SSH Key:**
   
   - Click **"New SSH key"**.
   - Provide a descriptive title, e.g., "Gitzilla Key".
   - Paste the copied SSH public key into the key field.
   - Click **"Add SSH key"**.

### 3. Connect to GitHub Repository

1. **Enter GitHub Username and Repository Name:**
   
   - In the **"GitHub Username"** field, enter your GitHub username.
   - In the **"Repository Name"** field, enter the exact name of the repository you wish to interact with.

2. **Connect:**
   
   - Click the **"Connect"** button.
   - Gitzilla will attempt to clone the specified repository using the provided SSH key.
   - Upon successful cloning, the top-level folders in the repository will populate the **"Folders in Repo"** dropdown.


### 4. Upload Files

1. **Select File to Upload:**
   
   - Click on the **"Locate File"** button to browse and select a file from your system.
   - **OR** drag and drop a file into the designated area if drag and drop is enabled.

2. **Specify Destination Path:**
   
   - In the **"New file/folder path"** field, enter the path within the repository where you want the file to be placed. For example, entering `newFolder` will place the file inside a folder named `newFolder`.

3. **Upload:**
   
   - Click the **"Upload"** button.
   - Monitor the progress via the progress bar and status messages.
   - Upon successful upload and push, a confirmation message will appear.


## Troubleshooting

Encountering issues? Below are common problems and their solutions.

### 1. SSH Test Timed Out

**Issue:**  
The application displays a timeout error during the SSH test phase.

**Solutions:**

- **Check Network Connection:**
  - Ensure you have a stable internet connection.
  - Verify that `github.com` is reachable by running:
    ```bash
    ping github.com
    ```

- **Firewall and Antivirus:**
  - Temporarily disable firewall or antivirus software to see if they're blocking SSH connections.
  - If disabled, configure them to allow SSH traffic.

- **SSH Agent Service (Windows):**
  - Ensure the `ssh-agent` service is running.
  - **Steps:**
    1. Press **Win + R**, type `services.msc`, and press **Enter**.
    2. Scroll to **"OpenSSH Authentication Agent"**.
    3. Right-click, select **"Properties"**, set **Startup type** to **"Automatic"**, and start the service.

### 2. Permission Denied (Publickey)

**Issue:**  
GitHub denies permission, indicating an issue with the SSH key.

**Solutions:**

- **Verify SSH Key on GitHub:**
  - Ensure the public key (`id_rsa_gitzilla.pub`) is correctly added to your GitHub account.
  - Re-add the key if necessary.

- **Check Key Permissions:**
  - Ensure the SSH key files have the correct permissions.
  - **On Unix-based systems:**
    ```bash
    chmod 600 ~/.gitzilla_keys/id_rsa_gitzilla
    ```
  - **On Windows:**  
    Permissions are generally managed automatically, but ensure no restrictions prevent access.

- **Correct SSH Key Path:**
  - Ensure Gitzilla points to the correct SSH key location.

### 3. Repository Not Found

**Issue:**  
Gitzilla cannot find the specified repository.

**Solutions:**

- **Verify Repository Name:**
  - Ensure the repository name is correct, including case sensitivity.
  - Confirm that the repository exists under your GitHub account.

- **Access Permissions:**
  - If the repository is private, ensure your GitHub account has access permissions.

### 4. Drag and Drop Not Working

**Issue:**  
Drag and drop functionality is not available.

**Solutions:**

- **Install `tkdnd_wrapper`:**
  - Ensure `tkdnd_wrapper` is installed.
  - **Installation:**
    ```bash
    pip install tkdnd-wrapper
    ```

- **Restart Gitzilla:**
  - After installation, restart the application to enable drag and drop.

## Contributing

Contributions are welcome! Whether it's reporting a bug, suggesting a feature, or submitting a pull request, your input helps improve Gitzilla.

1. **Fork the Repository:**
   
   Click the **"Fork"** button at the top right of the repository page.

2. **Clone Your Fork:**
   
   ```bash
   git clone https://github.com/R-D-BioTech-Alaska/Gitzilla.git
   cd Gitzilla
   ```

3. **Create a New Branch:**
   
   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**

5. **Commit Your Changes:**
   
   ```bash
   git commit -m "Add your message here"
   ```

6. **Push to Your Fork:**
   
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Submit a Pull Request:**
   
   Navigate to your fork on GitHub and click **"New pull request"**.

## License

Distributed under the [MIT License](LICENSE). See `LICENSE` for more information.

## Contact

If you have any questions, suggestions, or need support, feel free to reach out:

- **Email:** contact@rdbiotechalaska.com
- **GitHub Issues:** [GitHub Issues](https://github.com/R-D-BioTech-Alaska/Gitzilla/issues)
- **Twitter:** [@RDBioTechAlaska](https://twitter.com/rdbiotechalaska)

---

*This project is inspired by the need for a simple and efficient GUI tool to manage GitHub repositories via SSH. Contributions and feedback are highly appreciated!*
