import re

AI_OUTPUT = """
Hello, Ashwin.
I have written the letter you request for the receiver
ashwin01@gmail.com
"""

DEVOPS_AI_OUTPUT = """
192.168.159.99 [01/01/2026 15:00:00] /data.html 404
"""

normalized_output = AI_OUTPUT.lower()

#matched = re.search(r"[A-Za-z0-9_]+@[A-Za-z0-9_]+\.[A-Za-z0-9]+",normalized_output)
#matched = re.search(r"\w+@\w+\.\w+", normalized_output)
#result = re.sub(r"\w+@\w+\.\w+", 'REDACTED_EMAIL_ADDRESS',normalized_output)

result = re.sub(r"\d+\.\d+\.\d+\.\d+",'SERVER_IPV4',DEVOPS_AI_OUTPUT)

print(result)