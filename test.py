import sys
print("Python OK")
print("sys.path:", sys.path)
try:
    import requests
    print("requests OK")
except Exception as e:
    print("requests error:", e)