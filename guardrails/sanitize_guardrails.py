from guardrails.hub import DetectPII
from guardrails import Guard

guard = Guard().use(
    DetectPII(pii_entities=["EMAIL_ADDRESS","PHONE_NUMBER"], on_fail="fix")
)

AI_RESPONSE = """
Hello Aryan.
Successfully written data with your email aryan@networknuts.net.
Phone Number: 9326532664
"""

try:
    result = guard.validate(AI_RESPONSE)
    print(result)
except Exception as e:
    print(f"Error: {e}")