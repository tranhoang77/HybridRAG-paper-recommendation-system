from pymilvus import connections

# change the host and port as needed
connections.connect(alias="default", host="localhost", port="19530")

# Check if the connection is established
print("Checking connection to Milvus...")
if connections.has_connection("default"):
    print("✅ Connected to Milvus.")
else:
    print("❌ No connection.")