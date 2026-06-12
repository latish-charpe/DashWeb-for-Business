# Deployment Guide: InsightHub

This application is ready to be deployed to production! I have configured the environment variables, created the `requirements.txt` file, and added a `wsgi.py` entry point. 

Follow these instructions to deploy to your preferred platform.

## 1. Environment Variables
In your production environment, you **must** configure the following environment variables:

- `DATABASE_URL`: Your production MySQL connection string. Format: `mysql+mysqlconnector://user:password@host:port/dbname`
- `SECRET_KEY`: A strong, random string (e.g., generate one with `python -c "import secrets; print(secrets.token_hex(24))"`).
- `FLASK_DEBUG`: Set this to `False`.

> [!WARNING]
> Never use `FLASK_DEBUG=True` or the default local `DATABASE_URL` in a public production environment.

## 2. Deploying to Render (Recommended & Easiest)

1. Create a new **Web Service** on [Render.com](https://render.com).
2. Connect your GitHub repository (or upload your code).
3. Set the environment to **Python**.
4. Set the **Build Command** to: `pip install -r requirements.txt`
5. Set the **Start Command** to: `gunicorn wsgi:app`
6. In the Render Dashboard, add the Environment Variables listed above.
7. Click **Deploy**.

*Note: Render offers a managed MySQL database which you can attach to your service and use for the `DATABASE_URL`.*

## 3. Deploying to an AWS EC2 / Ubuntu VPS

If you are using a raw Linux server:

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv mysql-server nginx
   ```
2. **Setup the App**:
   ```bash
   git clone <your-repo> /var/www/dashweb
   cd /var/www/dashweb
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Create a `.env` file** in `/var/www/dashweb/`:
   ```env
   DATABASE_URL=mysql+mysqlconnector://dbuser:dbpass@localhost/insighthub
   SECRET_KEY=your_secure_random_key
   FLASK_DEBUG=False
   ```
4. **Run with Gunicorn using Systemd**:
   Create `/etc/systemd/system/dashweb.service`:
   ```ini
   [Unit]
   Description=Gunicorn daemon for Dashweb
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/var/www/dashweb
   Environment="PATH=/var/www/dashweb/venv/bin"
   ExecStart=/var/www/dashweb/venv/bin/gunicorn --workers 3 --bind unix:dashweb.sock -m 007 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```
   Start the service: `sudo systemctl start dashweb` and `sudo systemctl enable dashweb`.
5. **Setup Nginx**:
   Proxy requests to the gunicorn socket by configuring Nginx.
