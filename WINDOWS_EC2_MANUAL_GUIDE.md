# 🪟 Windows Server EC2 Deployment Guide (No Docker)

This guide is for deploying your FastAPI app to an **AWS EC2 Windows Server** without using Docker. This involves manually installing Python and Postgres, just like you would on your home computer.

---

## 🏗 Step 1: Launch Windows Server on EC2

1.  Log in to [AWS Console](https://console.aws.amazon.com/).
2.  Go to **EC2** -> **Launch Instance**.
3.  **Name**: `GST-Windows-Server`.
4.  **OS Images**: Search for "Windows" and select **Microsoft Windows Server 2022 Base** (Free Tier eligible).
5.  **Instance Type**: `t2.micro` or `t3.micro`.
6.  **Key Pair**: Create new or use existing.
    *   **Important**: For Windows, you need the PEM/PPK key to decrypt the Administrator password later.
7.  **Network Settings**:
    *   Allow **RDP** (Port 3389) - This is mostly open by default, but you might want to restrict to "My IP" for security.
    *   Allow **HTTP** (Port 80) from Anywhere.
    *   Allow **HTTPS** (Port 443) from Anywhere.
8.  Launch Instance.

---

## 🖥 Step 2: Connect via RDP (Remote Desktop)

1.  Go to **Instances**, select your new Windows Server.
2.  Click **Connect** (top right) -> **RDP client** tab.
3.  Click **Get password**.
    *   Upload your Key Pair file (`.pem`).
    *   Click **Decrypt Password**.
4.  Copy the **Public DNS**, **Username** (usually `Administrator`), and the **Password**.
5.  On your local computer:
    *   **Windows**: Open "Remote Desktop Connection", paste the Public DNS, connecting as Administrator with the password.
    *   **Mac**: Download "Microsoft Remote Desktop" from the App Store.

You represent now inside the remote Windows PC! 🤯

---

## 🛠 Step 3: Install Software on the Server

Inside the remote Windows Server, open the **Edge Browser** (yes, really) and download/install these:

### 1. Install Python
*   Download [Python 3.11.x for Windows](https://www.python.org/downloads/windows/).
*   **CRITICAL**: When running the installer, verify you check the box **"Add Python to PATH"** at the bottom of the first screen.
*   Click "Install Now".

### 2. Install Git
*   Download [Git for Windows](https://git-scm.com/download/win).
*   Just click "Next" through all the options.

### 3. Install PostgreSQL
*   Download [PostgreSQL Installer for Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
*   Run the installer.
*   **Remember the password** you set for the `postgres` superuser (default usually `postgres` or `password`).
*   Keep the default port `5432`.

### 4. (Optional) Install VS Code or Notepad++
*   Makes editing config files easier.

---

## 📂 Step 4: Setup the Code

Open **PowerShell** (Run as Administrator) on the Server.

```powershell
# Go to C drive
cd C:\

# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Create Virtual Environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

---

## ⚙ Step 5: Configure Environment & Database

1.  Create your `.env` file in the folder (Use Notepad).
2.  Paste your details. ensure `POSTGRES_SERVER` is set to `localhost` since Postgres is on the same machine.

```ini
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_installer_password
POSTGRES_DB=gst_compliance
SECRET_KEY=some_random_secret
```

3.  **Create the Database**:
    *   Open "pgAdmin 4" (installed with Postgres) or use command line.
    *   Create a new database named `gst_compliance`.

---

## 🚀 Step 6: Run the App

In your Administrator PowerShell window (with venv activated):

```powershell
# Run on Port 80 (Standard HTTP port)
python -m uvicorn app.main:app --host 0.0.0.0 --port 80
```

**Note**: If you get a "Permission denied" or "Access denied" on port 80, ensure you launched PowerShell as **Administrator**.

---

## 🚧 Step 7: Open Windows Firewall

Even though you opened the AWS Firewall (Security Group), **Windows itself** has a firewall.

1.  Press `Start`, type "Windows Defender Firewall with Advanced Security".
2.  Click **Inbound Rules** (left).
3.  Click **New Rule...** (right).
4.  **Rule Type**: Port.
5.  **Protocol**: TCP. **Specific local ports**: 80.
6.  **Action**: Allow the connection.
7.  **Profile**: Check Domain, Private, Public.
8.  **Name**: "Allow HTTP Port 80".

---

## ✅ Test It

Go to your browser on your LOCAL computer and visit:
`http://YOUR_EC2_PUBLIC_IP/docs`

---

## 🧹 Making it run permanently (Optional)

Closing Remote Desktop will NOT kill the server, but closing the black PowerShell window WILL.

To make it run in the background as a service:
1.  Download **NSSM** (Non-Sucking Service Manager).
2.  Run `nssm install GSTBackend`.
3.  Pointing `Path` to your `python.exe` inside the venv (e.g., `C:\YOUR_REPO\venv\Scripts\python.exe`).
4.  Set `Arguments` to: `-m uvicorn app.main:app --host 0.0.0.0 --port 80`.
5.  Set `Startup directory` to your project folder.
6.  Click "Install service".
7.  Run `nssm start GSTBackend`.


Now it runs automatically even if you reboot!

---

## 🧠 Understanding the Architecture: Where is Postgres?

You might be wondering: *"Do I need a separate server for the database?"*

### Option A: The "All-in-One" (What this guide does)
**Cost:** $0 (Free Tier) | **Difficulty:** Easy

In this guide, we installed Postgres **ON THE SAME EC2 INSTANCE** as your FastAPI app.
*   **Your Computer (EC2)**: It wears two hats. It is the Web Server AND the Database Server.
*   **Connection**: Because they are neighbors on the same hard drive, they talk via `localhost` (127.0.0.1).
*   **Pros**: Cheapest, fastest to set up.
*   **Cons**: If you delete the Server, you delete the Data (unless you backup).

### Option B: The "Professional" Way (AWS RDS)
**Cost:** $$$ (Free Tier available but tricky) | **Difficulty:** Medium

In big companies, we separate them. You would buy **two** services from AWS:
1.  **EC2**: Just runs the Python/FastAPI code.
2.  **AWS RDS**: A dedicated machine just for Postgres.
*   **Connection**: You would paste the RDS URL (e.g., `mydb.aws.com`) into your `.env` file instead of `localhost`.
*   **Pros**: AWS handles backups, scaling, and updates.
*   **Cons**: More expensive, more setup.


**For now, stick to Option A.** It is perfectly fine for prototypes and MVPs!

---

## 🎓 Deep Dive: How does the DB actually work?

You asked: *"Is Postgres already hosted like Supabase?"*

**The Answer is NO.** here is the difference:

### 1. The "Supabase" Way (Managed Service)
Think of this like **ordering Pizza**.
*   You call a phone number (API URL).
*   Someone else (Supabase) has a kitchen (Server).
*   They cook the pizza and deliver it to you.
*   You don't know what oven they used or if the chef is tired. You just get the result.
*   **Pros**: Easy, no cleanup.
*   **Cons**: You pay a premium for the service.

### 2. The "EC2 Manual" Way (Self-Hosted)
Think of this like **cooking in your own kitchen**.
*   **The Kitchen**: This is your EC2 Windows Server.
*   **The Utilities**: This is the Postgres Software you installed.
*   **The Chef**: That's YOU!

### So how is it "happening"?
When you ran that PostgreSQL Installer in Step 3, you didn't connect to a cloud. You literally installed a specialized computer program on your hard drive.

1.  **The Service**: Postgres installs a background worker (called a Windows Service). It runs silently 24/7, even if no one is logged in.
2.  **The Port**: It sits and listens on "Port 5432". It's like opening a specific window in your house and waiting for someone to shout a taco order through it.
3.  **The Files**: When you save a user, Postgres doesn't send it to the cloud. It literally writes the data to a file on your hard drive (usually `C:\Program Files\PostgreSQL\15\data`).

**Summary**: In this guide, your API and your Database are roommates living in the same apartment (Server). Your API just walks down the hall (localhost) to ask the Database for info.


