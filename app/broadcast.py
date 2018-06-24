from api import broadcast
import sys
import time

time.sleep(1)

broadcast(
    user_id = sys.argv[1],
    block_name=sys.argv[3],
    attributes={'api_message_body':  sys.argv[2]}
)

