#!/usr/bin/env python3

import os
import re
import tkinter as tk
import tkinter.ttk as ttk
import subprocess
import tempfile
import shutil
from tkinter import filedialog, messagebox
from pathlib import Path

# For drag and drop (optional):
try:
    from tkdnd_wrapper import TkDND
    HAS_DND = True
except ImportError:
    HAS_DND = False

#  Theme
BG_COLOR    = "#0D1117"  # background
FG_COLOR    = "#C9D1D9"  # foreground (text)
ENTRY_COLOR = "#21262D"  # entry / button background
BTN_COLOR   = "#21262D"
BTN_FG      = "#C9D1D9"

class GitzillaApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gitzilla - Minimal Dark UI, Automated SSH URL")
        self.master.configure(bg=BG_COLOR)
        self.master.geometry("800x600")

        # Attempt DnD
        self.dnd = None
        if HAS_DND:
            self.dnd = TkDND(master)

        #  Track program state
        self.clone_dir = None
        self.generated_priv_key = None
        self.generated_pub_key = None

        # Store the entire public key
        self.current_pub_key_full = ""

        # Store the detected GitHub username
        self.github_username = None

        # --------------- 1) Generate Key, snippet, copy btn --------------- #
        self.top_frame = tk.Frame(master, bg=BG_COLOR)
        self.top_frame.pack(pady=10, fill="x", padx=10)

        # Generate SSH Key
        self.gen_key_btn = tk.Button(
            self.top_frame,
            text="Generate SSH Key",
            command=self.generate_ssh_key,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=20
        )
        self.gen_key_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Snippet label
        self.pubkey_snippet_var = tk.StringVar(value="No key generated")
        self.pubkey_snippet_label = tk.Label(
            self.top_frame,
            textvariable=self.pubkey_snippet_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            width=40,
            anchor="w"
        )
        self.pubkey_snippet_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Copy Key button
        self.copy_key_btn = tk.Button(
            self.top_frame,
            text="Copy Key",
            command=self.copy_pub_key,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=10
        )
        self.copy_key_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # --------------- 2) GitHub Username & Repo Name + Connect Button --------------- #
        self.second_frame = tk.Frame(master, bg=BG_COLOR)
        self.second_frame.pack(pady=10, fill="x", padx=10)

        # GitHub Username label
        self.username_label = tk.Label(
            self.second_frame,
            text="GitHub Username:",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        # GitHub Username entry
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            self.second_frame,
            textvariable=self.username_var,
            width=30,
            bg=ENTRY_COLOR,
            fg=FG_COLOR
        )
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.username_entry.insert(0, "yourUsername")  # example default

        # Repo name label
        self.repo_name_label = tk.Label(
            self.second_frame,
            text="Repository Name:",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.repo_name_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Repository name entry
        self.repo_name_var = tk.StringVar()
        self.repo_name_entry = tk.Entry(
            self.second_frame,
            textvariable=self.repo_name_var,
            width=30,
            bg=ENTRY_COLOR,
            fg=FG_COLOR
        )
        self.repo_name_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.repo_name_entry.insert(0, "myRepo")  # example default

        # Connect button
        self.connect_btn = tk.Button(
            self.second_frame,
            text="Connect",
            command=self.connect_to_github,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=15
        )
        self.connect_btn.grid(row=0, column=4, padx=15, pady=5, sticky="w")

        # --------------- 3) Folder Dropdown --------------- #
        self.third_frame = tk.Frame(master, bg=BG_COLOR)
        self.third_frame.pack(pady=10, fill="x", padx=10)

        self.folders_label = tk.Label(
            self.third_frame,
            text="Folders in Repo:",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.folders_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.folders_var = tk.StringVar()
        self.folders_dropdown = ttk.Combobox(
            self.third_frame,
            textvariable=self.folders_var,
            state="readonly",
            width=30
        )
        self.folders_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.folders_dropdown['values'] = ["(No folders yet)"]
        self.folders_dropdown.current(0)

        # --------------- 4) New file/folder path --------------- #
        self.fourth_frame = tk.Frame(master, bg=BG_COLOR)
        self.fourth_frame.pack(pady=10, fill="x", padx=10)

        self.new_path_label = tk.Label(
            self.fourth_frame,
            text="New file/folder path:",
            bg=BG_COLOR,
            fg=FG_COLOR
        )
        self.new_path_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.new_path_var = tk.StringVar()
        self.new_path_entry = tk.Entry(
            self.fourth_frame,
            textvariable=self.new_path_var,
            width=50,
            bg=ENTRY_COLOR,
            fg=FG_COLOR
        )
        self.new_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.new_path_entry.insert(0, "newFolder")  # example default

        # --------------- 5) Locate file / drag-drop --------------- #
        self.fifth_frame = tk.Frame(master, bg=BG_COLOR)
        self.fifth_frame.pack(pady=10, fill="x", padx=10)

        self.locate_btn = tk.Button(
            self.fifth_frame,
            text="Locate File",
            command=self.locate_file_dialog,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=15
        )
        self.locate_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.selected_file_var = tk.StringVar(value="(no file chosen)")
        self.file_label = tk.Label(
            self.fifth_frame,
            textvariable=self.selected_file_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            width=50,
            anchor="w"
        )
        self.file_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.drag_label = tk.Label(
            self.fifth_frame,
            text="(Drag & Drop file here)",
            bg=ENTRY_COLOR,
            fg=FG_COLOR,
            width=25,
            height=2,
            relief="groove"
        )
        self.drag_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        if self.dnd:
            self.dnd.bindtarget(self.drag_label, "text/uri-list", "<Drop>", self.handle_drop)

        # --------------- 6) Upload & progress bar --------------- #
        self.sixth_frame = tk.Frame(master, bg=BG_COLOR)
        self.sixth_frame.pack(pady=10, fill="x", padx=10)

        self.upload_btn = tk.Button(
            self.sixth_frame,
            text="Upload",
            command=self.upload_file,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=15
        )
        self.upload_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.progress_bar = ttk.Progressbar(
            self.sixth_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress_bar.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --------------- Status and Exit --------------- #
        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = tk.Label(
            master,
            textvariable=self.status_var,
            bg=BG_COLOR,
            fg=FG_COLOR,
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=10, pady=10)

        self.exit_btn = tk.Button(
            master,
            text="Exit",
            command=self.quit_app,
            bg=BTN_COLOR,
            fg=BTN_FG,
            width=15
        )
        self.exit_btn.pack(pady=5)

    #   1) Generate SSH Key
    def generate_ssh_key(self):
        """Generate new SSH key pair, copy pubkey to clipboard, show snippet."""
        # Define a persistent directory for SSH keys for easier debugging
        keys_dir = Path.home() / ".gitzilla_keys"
        keys_dir.mkdir(exist_ok=True)
        self.generated_priv_key = keys_dir / "id_rsa_gitzilla"
        self.generated_pub_key = self.generated_priv_key.with_suffix(".pub")

        # Cleanup old keys if they exist
        if self.generated_priv_key.exists():
            self.generated_priv_key.unlink()
        if self.generated_pub_key.exists():
            self.generated_pub_key.unlink()

        self.update_status("Generating SSH key pair...")
        try:
            subprocess.run([
                "ssh-keygen",
                "-t", "rsa",
                "-b", "4096",
                "-C", "gitzilla_key",
                "-f", str(self.generated_priv_key),
                "-N", ""
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip() if e.stderr else "Unknown error."
            self.update_status(f"Error generating key: {error_msg}")
            messagebox.showerror("SSH Key Generation Error", f"Error generating key:\n{error_msg}")
            return

        # Read the public key
        try:
            with open(self.generated_pub_key, "r") as f:
                pub_key = f.read().strip()
                self.current_pub_key_full = pub_key
        except Exception as e:
            self.update_status(f"Error reading public key: {str(e)}")
            messagebox.showerror("Public Key Error", f"Error reading public key:\n{str(e)}")
            return

        # Show snippet
        snippet = self.current_pub_key_full[:30] + "..."
        self.pubkey_snippet_var.set(snippet)

        # Copy to clipboard
        self.master.clipboard_clear()
        self.master.clipboard_append(self.current_pub_key_full)
        self.update_status("SSH key generated & public key copied to clipboard.\nPlease add it to your GitHub account.")

    def copy_pub_key(self):
        """Copies the full public key to the clipboard again."""
        if self.current_pub_key_full:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.current_pub_key_full)
            self.update_status("Public key copied to clipboard.")
        else:
            self.update_status("No public key to copy.")
            messagebox.showwarning("No Public Key", "No public key to copy. Generate a key first.")


    #   2) Connect to GitHub
    #      (using provided username and repo name)
    def connect_to_github(self):
        """
        1) Uses provided GitHub username and repository name to build SSH URL.
        2) Clones the repository using the specified SSH key.
        """
        if not self.generated_priv_key or not self.generated_priv_key.exists():
            self.update_status("Error: No generated SSH key found. Generate SSH key first.")
            messagebox.showerror("No SSH Key", "No generated SSH key found. Please generate an SSH key first.")
            return

        github_username = self.username_var.get().strip()
        repo_name = self.repo_name_var.get().strip()

        if not github_username:
            self.update_status("Error: Please enter your GitHub username.")
            messagebox.showerror("Username Missing", "Please enter your GitHub username.")
            return

        if not repo_name:
            self.update_status("Error: Please enter a repository name.")
            messagebox.showerror("Repository Name Missing", "Please enter a repository name.")
            return

        self.github_username = github_username

        # Step 1: Build final SSH URL
        final_url = f"git@github.com:{self.github_username}/{repo_name}.git"
        self.update_status(f"Cloning repository '{final_url}'...")

        # Step 2: Clone the repository using GIT_SSH_COMMAND
        try:
            # Set GIT_SSH_COMMAND to use the specific SSH key
            git_env = os.environ.copy()
            git_env["GIT_SSH_COMMAND"] = f'ssh -i "{self.generated_priv_key}" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'

            # Create a temporary directory for cloning
            if self.clone_dir and Path(self.clone_dir).exists():
                shutil.rmtree(self.clone_dir)
            self.clone_dir = tempfile.mkdtemp(prefix="gitzilla_clone_")

            # Clone the repository
            clone_cmd = ["git", "clone", final_url, self.clone_dir]
            clone_proc = subprocess.run(
                clone_cmd,
                shell=False,
                check=True,
                capture_output=True,
                text=True,
                env=git_env
            )

            self.update_status("Repository cloned successfully.")

        except subprocess.CalledProcessError as e:
            # Capture and display stderr
            error_output = e.stderr.strip() if e.stderr else "No error output."
            self.update_status(f"Error cloning repository:\n{error_output}")
            messagebox.showerror("Clone Error", f"Error cloning repository:\n{error_output}")
            return
        except Exception as e:
            self.update_status(f"Unexpected error during cloning: {str(e)}")
            messagebox.showerror("Clone Error", f"Unexpected error during cloning:\n{str(e)}")
            return

        # Step 3: Populate the folders dropdown
        try:
            folder_list = []
            for item in os.listdir(self.clone_dir):
                full_path = Path(self.clone_dir) / item
                if full_path.is_dir() and item != ".git":
                    folder_list.append(item)
            folder_list.sort()
            if not folder_list:
                folder_list = ["(No folders yet)"]
            self.folders_dropdown['values'] = folder_list
            self.folders_dropdown.current(0)
            self.update_status("Folders dropdown updated.")
        except Exception as e:
            self.update_status(f"Error reading repository folders: {str(e)}")
            messagebox.showerror("Folder Read Error", f"Error reading repository folders:\n{str(e)}")
            return

    #   3) File location & DnD
    def locate_file_dialog(self):
        """Open a file dialog and store the selected file path."""
        fp = filedialog.askopenfilename(title="Select file to upload")
        if fp and os.path.isfile(fp):
            self.selected_file_var.set(fp)
            self.update_status(f"Selected file: {os.path.basename(fp)}")

    def handle_drop(self, event):
        """Handle file(s) dropped into the drag label."""
        dropped = event.data.strip()
        if dropped.startswith("{") and dropped.endswith("}"):
            dropped = dropped[1:-1]
        if dropped.startswith("file:///"):
            dropped = dropped[8:]
        dropped = dropped.replace("\\", "/")
        pieces = dropped.split()
        fp = pieces[0]
        if os.path.isfile(fp):
            self.selected_file_var.set(fp)
            self.update_status(f"File dropped: {os.path.basename(fp)}")
        else:
            self.update_status("Dropped data is not a file.")
            messagebox.showwarning("Invalid Drop", "Dropped data is not a valid file.")

    #   4) Upload File
    def upload_file(self):
        """Creates a new file/folder path (if needed), copies the file in, commits, and pushes."""
        if not self.clone_dir or not Path(self.clone_dir).exists():
            self.update_status("Error: Repository not cloned. Connect first.")
            messagebox.showerror("Clone Required", "Repository not cloned. Please connect to GitHub first.")
            return

        local_file = self.selected_file_var.get().strip()
        if not local_file or not os.path.isfile(local_file):
            self.update_status("Error: No valid file to upload.")
            messagebox.showerror("No File Selected", "No valid file selected for upload.")
            return

        new_path = self.new_path_var.get().strip()

        # Determine selected folder from dropdown
        folder_choice = self.folders_var.get().strip()
        if folder_choice in ("(No folders yet)", "(No folders yet)"):
            folder_choice = ""  # top-level

        repo_target_dir = Path(self.clone_dir) / folder_choice if folder_choice else Path(self.clone_dir)
        full_target_path = repo_target_dir / new_path if new_path else repo_target_dir

        # Create the target directory if it doesn't exist
        try:
            full_target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.update_status(f"Error creating new folder(s): {str(e)}")
            messagebox.showerror("Folder Creation Error", f"Error creating new folder(s):\n{str(e)}")
            return

        # Copy the local file to the target directory
        dest_file = full_target_path / Path(local_file).name
        try:
            shutil.copyfile(local_file, dest_file)
            self.update_status(f"File copied to {dest_file}.")
        except Exception as e:
            self.update_status(f"Error copying file: {str(e)}")
            messagebox.showerror("File Copy Error", f"Error copying file:\n{str(e)}")
            return

        # Update progress bar
        self.progress_bar["value"] = 0
        self.progress_bar.update_idletasks()

        # Set GIT_SSH_COMMAND to use the specific SSH key
        git_env = os.environ.copy()
        git_env["GIT_SSH_COMMAND"] = f'ssh -i "{self.generated_priv_key}" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'

        # Commit and push changes
        try:
            original_cwd = os.getcwd()
            os.chdir(self.clone_dir)

            # Git add
            add_cmd = ["git", "add", "."]
            subprocess.run(add_cmd, shell=False, check=True, capture_output=True, text=True, env=git_env)
            self.progress_bar["value"] = 33
            self.progress_bar.update_idletasks()

            # Git commit
            commit_cmd = ["git", "commit", "-m", "Add file via Gitzilla"]
            commit_proc = subprocess.run(commit_cmd, shell=False, check=True, capture_output=True, text=True, env=git_env)
            if "nothing to commit" in commit_proc.stdout.lower():
                self.update_status("Nothing to commit.")
                messagebox.showinfo("No Changes", "No changes to commit.")
                os.chdir(original_cwd)
                self.progress_bar["value"] = 0
                return
            self.progress_bar["value"] = 66
            self.progress_bar.update_idletasks()

            # Git push
            push_cmd = ["git", "push"]
            subprocess.run(push_cmd, shell=False, check=True, capture_output=True, text=True, env=git_env)
            self.progress_bar["value"] = 100
            self.progress_bar.update_idletasks()

            os.chdir(original_cwd)
            self.update_status("File uploaded and changes pushed successfully.")
            messagebox.showinfo("Success", "File uploaded and changes pushed successfully.")
        except subprocess.CalledProcessError as e:
            os.chdir(original_cwd)
            error_output = e.stderr.strip() if e.stderr else "No error output."
            self.update_status(f"Error during Git operations:\n{error_output}")
            messagebox.showerror("Git Error", f"Error during Git operations:\n{error_output}")
            self.progress_bar["value"] = 0
            return
        except Exception as e:
            os.chdir(original_cwd)
            self.update_status(f"Unexpected error during Git operations: {str(e)}")
            messagebox.showerror("Git Error", f"Unexpected error during Git operations:\n{str(e)}")
            self.progress_bar["value"] = 0
            return

    #   Helpers
    def update_status(self, msg):
        self.status_var.set(msg)
        self.master.update_idletasks()

    def quit_app(self):
        """Cleanup clone directory and SSH keys before exiting."""
        # Cleanup clone directory if needed
        if self.clone_dir and Path(self.clone_dir).exists():
            try:
                shutil.rmtree(self.clone_dir)
            except Exception as e:
                print(f"Error removing clone directory: {str(e)}")

        # Cleanup generated SSH keys
        if self.generated_priv_key and self.generated_priv_key.exists():
            try:
                self.generated_priv_key.unlink()
            except Exception as e:
                print(f"Error removing private key: {str(e)}")
        if self.generated_pub_key and self.generated_pub_key.exists():
            try:
                self.generated_pub_key.unlink()
            except Exception as e:
                print(f"Error removing public key: {str(e)}")

        self.master.destroy()

def main():
    root = tk.Tk()
    app = GitzillaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
