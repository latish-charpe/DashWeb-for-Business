from app import app
from dotenv import load_dotenv
import os

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()

if __name__ == "__main__":
    app.run()
