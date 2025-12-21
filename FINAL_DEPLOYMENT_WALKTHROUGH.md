# 🏁 The Final, Absolute Deployment Guide
**Method: AWS EC2 (Ubuntu) + Docker Compose**

You asked for the **best, easiest, and most professional** way. This is it. Stop looking at other guides. This method creates your Database and your App automatically using Docker.

**Why this method?**
1.  **It's an "All-in-One":** Docker creates a fake computer *inside* your server for your App, and another one for your Database. They connect automatically.
2.  **Zero Manual Installs:** You do NOT need to install Python, Postgres, or messy dependencies manually.
3.  **Free:** Fits on the AWS Free Tier.

---

## 🛑 Step 1: Launch the Server (AWS)

1.  Log in to [AWS Console](https://console.aws.amazon.com/).
2.  Search **EC2** -> **Launch Instance**.
3.  **Name**: `GST-Production`.
4.  **OS**: Choose **Ubuntu** (NOT Windows).
5.  **Instance Type**: `t2.micro` (Free tier).
6.  **Key Pair**: Create new -> Name: `gst-key` -> Download `.pem`.
7.  **Network Settings**: Check the boxes for:
    *   [x] Allow SSH traffic from Anywhere
    *   [x] Allow HTTP traffic from the internet
    *   [x] Allow HTTPS traffic from the internet
8.  **Launch Instance**.

---

## 🔌 Step 2: Connect to the Server

1.  Go to your AWS **Instances** list.
2.  Copy the **Public IPv4 address** (e.g., `54.123.45.67`).
3.  Open **Command Prompt** (cmd) or PowerShell on your computer.
4.  Navigate to your downloads folder (where the key is):
    ```powershell
    cd Downloads
    ```
5.  Run this command (replace with your specific IP):
    ```powershell
    ssh -i "gst-key.pem" ubuntu@54.123.45.67
    ```
    *   Type `yes` if asked.
    *   *If you get a "Permission Denied" error on the key, Google "windows ssh permissions pem", but usually PowerShell handles it fine.*

**You are now in the terminal of your server.**

---

## 🐳 Step 3: Install Docker (The Engine)

Copy and paste this ENTIRE block into your terminal and hit Enter. It installs everything.

```bash
sudo apt-get update && \
sudo apt-get install -y docker.io docker-compose-v2 git && \
sudo systemctl enable --now docker && \
sudo usermod -aG docker $USER
```

**CRITICAL STEP:** Now type `exit` to disconnect. Then press `Up Arrow` on your keyboard and hit `Enter` to connect again. This refreshes your permissions.

---

## 📂 Step 4: Get Your Code

1.  Clone your repository (Replace with your actual GitHub URL):
    ```bash
    git clone https://github.com/YOUR_GITHUB_USER/YOUR_REPO_NAME.git
    ```
2.  Enter the folder:
    ```bash
    cd YOUR_REPO_NAME
    ```

---

## 🔐 Step 5: The "Environment" (Where secrets live)

This is the step you asked about. We need to create the `.env` file on this new computer because we didn't upload it to GitHub (for security).

1.  Type this to open a text editor inside the terminal:
    ```bash
    nano .env
    ```
2.  **Paste** your production config. Use `POSTGRES_SERVER=db` (This is magic. Docker names the database `db`).

    **COPY THIS EXACT TEXT:**
    ```ini
    # Database (Docker handles the 'db' hostname)
    POSTGRES_SERVER=db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=securepassword123
    POSTGRES_DB=gst_compliance
    
    # Secrets
    SECRET_KEY=change_this_to_something_random
    ALGORITHM=HS256
    
    # Other
    PROJECT_NAME=GST Compliance Prod
    ```

3.  **Save & Exit**:
    *   Press `Ctrl + O` (Letter O) -> Hit `Enter`.
    *   Press `Ctrl + X`.

---

## 🚀 Step 6: Launch Everything

Run this single command. It downloads Postgres, installs Python, and starts your app.

```bash
docker compose up -d --build
```

*   `up`: Start.
*   `-d`: Detached (run in background).
*   `--build`: Build the app from scratch.

---

## ✅ Step 7: Done.

Go to your browser:
`http://54.123.45.67/docs`

(Replace with your AWS IP).

---

## ❓ FAQ

**Q: Where is the database?**
A: It is running in a Docker Container named `db`. It is saving data to a folder on the server hidden by Docker.

**Q: How do see the logs?**
A: `docker compose logs -f`

**Q: How do I update the code?**
A:
```bash
git pull
docker compose up -d --build
```
