from db import run_query

result = run_query("RETURN 'Neo4j connected!' AS message")
print(result)