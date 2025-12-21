# 🚀 Full Noob Guide: Deploying FastAPI + Postgres to AWS EC2

This guide will take you from **zero** to a **live running API** on the internet. We will use **Docker** because it is the easiest and most robust way to deploy.

---

## ✅ Prerequisites

1.  **AWS Account**: You need an active AWS account.
2.  **Credit Card**: You need one for AWS (but we will use the **Free Tier** capable `t2.micro` or `t3.micro` instance).

---

## 🛠 Step 1: Launch an EC2 Instance (Virtual Server)

1.  Log in to your [AWS Console](https://console.aws.amazon.com/).
2.  Search for **EC2** in the top search bar and click it.
3.  Click the orange **Launch Instance** button.
4.  **Name**: Give it a cool name like `GST-Backend-Server`.
5.  **OS Images**: Select **Ubuntu** (Ubuntu Server 24.04 LTS or 22.04 LTS).
6.  **Instance Type**: Select `t2.micro` (Free Tier eligible).
7.  **Key Pair (Login)**:
    *   Click "Create new key pair".
    *   Name: `gst-key`.
    *   Type: `.pem` (for Mac/Linux) or `.ppk` (for Windows PuTTY, though `.pem` works with Windows PowerShell now too).
    *   Download the file and **keep it safe!**
8.  **Network Settings**:
    *   Click "Edit" (top right of this box).
    *   Ensure "Auto-assign public IP" is **Enable**.
    *   **Security Group** (Firewall):
        *   Choose "Create security group".
        *   Allow **SSH** (Port 22) from "Anywhere" (0.0.0.0/0).
        *   Allow **HTTP** (Port 80) from "Anywhere" (0.0.0.0/0).
        *   Allow **HTTPS** (Port 443) from "Anywhere" (0.0.0.0/0).
9.  Click **Launch Instance**.

---

## 🔌 Step 2: Connect to Your Server

1.  Click **Instances** on the left menu to see your list.
2.  Wait until "Instance State" is **Running**.
3.  Click the **Instance ID** to see details. Copy the **Public IPv4 address** (e.g., `54.123.45.67`).

### 💻 For Windows (PowerShell) or Mac/Linux (Terminal):

Open your terminal on your computer and run:

```bash
# Go to where you downloaded the key
cd Downloads

# (Mac/Linux only) Set permissions
chmod 400 gst-key.pem

# Connect (replace 1.2.3.4 with your ACTUAL AWS IP)
ssh -i "gst-key.pem" ubuntu@1.2.3.4
```

*Type `yes` if asked about fingerprints.*

You are now inside the remote server! 🎉

---

## 🐳 Step 3: Install Docker

Run these commands inside your server one by one:

```bash
# Update the package list
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io

# Install Docker Compose (V2)
sudo apt-get install -y docker-compose-v2

# Start Docker and enable it to run on boot
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (avoids typing sudo every time)
sudo usermod -aG docker $USER
```

**IMPORTANT**: Now type `exit` to disconnect, and reconnect again (SSH back in) for the changes to take effect.

---

## 📂 Step 4: Get Your Code

There are two ways. The **easiest** is to clone from GitHub.

### Option A: Clone from GitHub (Recommended)
1.  Push your code to GitHub if you haven't already.
2.  On the server:
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
    ```

### Option B: Copy Files Manually (If no GitHub)
(Skip if you used Option A). Only do this if you are desperate.
On your **local computer**:
```bash
scp -i "gst-key.pem" -r ./ ubuntu@1.2.3.4:~/app
```

---

## 🚀 Step 5: Start the App

Go into your project folder on the server:

```bash
cd YOUR_REPO_NAME (or whatever your folder is)
```

Create a `.env` file if you have secrets (Docker Compose will read it):

```bash
nano .env
```
*(Paste your secrets here. `Ctrl+O` to save, `Enter` to confirm, `Ctrl+X` to exit).*

**Run the Deployment:**

```bash
docker compose up -d --build
```

*   `up`: Starts the containers.
*   `-d`: Detached mode (runs in background so it doesn't stop when you disconnect).
*   `--build`: Forces a rebuild of the image.

---

## 🌐 Step 6: Test It!

Open your browser and go to your AWS IP Address:

`http://YOUR_AWS_PUBLIC_IP/docs`

You should see your Swagger UI!

---

## 🔄 Useful Commands

*   **View Logs**: `docker compose logs -f`
*   **Stop Everything**: `docker compose down`
*   **Update Code**:
    1.  `git pull`
    2.  `docker compose up -d --build` (Rebuilds automatically)

---

## 🛡 (Optional) Domain & SSL (HTTPS)

If you want a real domain like `api.myapp.com`:
1.  Buy a domain (Namecheap/GoDaddy).
2.  Create an **A Record** pointing to your AWS IP.
3.  Use **Nginx Proxy Manager** (easiest for noobs) or **Caddy** to auto-handle SSL.
