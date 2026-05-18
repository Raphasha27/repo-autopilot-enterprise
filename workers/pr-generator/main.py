import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pr-generator-worker")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def main():
    logger.info("PR Generator Worker active. Listening for job notifications...")
    while True:
        # Listening loop
        time.sleep(10)

if __name__ == "__main__":
    main()
