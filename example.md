---
title: "How to Install OpenSSH on Arch Linux Using a Script"
date: 2025-05-04T00:43:21+05:30
tags: ["Arch Linux", "SSH", "Linux", "OpenSSH", "Automation"]
categories: ["Linux", "How-to"]
author: "Rohan Batra"
draft: false
description: "A step-by-step guide to install and configure OpenSSH on Arch Linux using an automated script."
---

## Introduction

In this post, we will walk through how to quickly install and configure **OpenSSH** on your **Arch Linux** system using a simple Bash script. Whether you're setting up SSH for the first time or automating your setup process, this script makes the process easy and efficient.

### Why Use OpenSSH?

**OpenSSH** is a widely used tool to enable secure remote connections to your Linux system. It allows you to remotely access and manage your machine through the terminal, which is essential for remote administration or server management.

### What This Script Does

The `install_ssh.sh` script automates the installation and configuration of the **OpenSSH server** (`sshd`) on Arch Linux. The script performs the following steps:

1. **System Update**: Ensures your system is up-to-date.
2. **Installs OpenSSH**: Installs the OpenSSH package, which includes both the SSH server and client.
3. **Enables SSH Service**: Configures the SSH service to start on boot and starts it immediately.
4. **Status Check**: Verifies that the SSH service is running correctly.

By using this script, you can avoid the need for repetitive manual setup tasks and streamline the process.

---

## The Script

Here’s the Bash script that automates the installation of **OpenSSH** on Arch Linux:

```bash
#!/bin/bash

# Update system and install OpenSSH
echo "Updating system..."
sudo pacman -Syu --noconfirm

echo "Installing OpenSSH..."
sudo pacman -S --noconfirm openssh

# Enable and start the SSH service
echo "Enabling and starting SSH service..."
sudo systemctl enable sshd
sudo systemctl start sshd

# Check if SSH service is running
echo "Checking SSH service status..."
sudo systemctl status sshd | grep "Active"

# Final status check
echo "SSH service status:"
sudo systemctl status sshd

echo "SSH installation and configuration completed!"
```

### How It Works

1. **System Update**: The script first updates your system using `pacman -Syu` to ensure you're working with the latest packages.
2. **OpenSSH Installation**: It installs the OpenSSH package (`openssh`) without requiring user interaction, making the process hands-off.
3. **Enabling and Starting SSH**: After installation, the script enables the SSH service (`sshd`) to start automatically on boot and starts it immediately, allowing you to use SSH right away.
4. **Service Status Check**: Finally, the script checks the SSH service status to ensure everything is running as expected.

---

## How to Use the Script

1. **Create the Script File**: Open a terminal and create the script file using your preferred text editor, e.g., `nano` or `vim`.

   ```bash
   nano install_ssh.sh
   ```

2. **Copy and Paste the Script**: Copy the provided script content and paste it into the `install_ssh.sh` file.

3. **Make the Script Executable**: You need to make the script executable to run it.

   ```bash
   chmod +x install_ssh.sh
   ```

4. **Run the Script**: Execute the script with the following command:

   ```bash
   ./install_ssh.sh
   ```

The script will take care of the rest, including installing OpenSSH and configuring it to run on boot.

---

## Conclusion

Using this script, you can easily automate the installation and configuration of **OpenSSH** on your **Arch Linux** machine. This is especially useful for new installations or if you need to quickly set up SSH without manually performing each step.

By streamlining this process, you can ensure that **SSH** is always ready to go, allowing you to remotely access and manage your system with ease.

If you have any questions or run into issues, feel free to leave a comment below!
