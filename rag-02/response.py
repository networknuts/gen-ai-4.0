import redis
import time

redis_client = redis.Redis(host='localhost',
    port=6379,
    decode_responses=True)

job_id = input("JOB ID: ")

while True:
    result = redis_client.get(f"rag:response:{job_id}")
    if result:
        print(f"\n{result}")
        break
    else:
        print("waiting for result")
        time.sleep(2)