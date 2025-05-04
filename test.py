from pymilvus import connections

connections.connect(uri="http://localhost:19530")
print("Kết nối thành công!")