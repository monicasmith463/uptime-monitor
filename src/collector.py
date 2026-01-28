import requests
import time
import redis
import json
import schedule

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def fetch_site(site):
    try:
        start = time.time()
        response = requests.get(site, timeout=10)
        latency = time.time() - start

        payload = {
            "site": site,
            "response_time": latency,
            "status_code": response.status_code,
            "error": None
        }

    except Exception as e:
        payload = {
            "site": site,
            "response_time": None,
            "status_code": None,
            "error": str(e)
        }

    print("Publishing:", payload)
    r.publish("latency", json.dumps(payload))


if __name__ == "__main__":
    schedule.every(15).seconds.do(fetch_site, "https://example.com")

    while True:
        schedule.run_pending()
        time.sleep(1)