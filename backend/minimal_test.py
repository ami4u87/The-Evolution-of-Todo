from fastapi import FastAPI
from app.auth.password import hash_password

app = FastAPI()

@app.get("/test-hash")
def test_hash():
    try:
        hashed = hash_password("test_password")
        return {"status": "success", "hashed": hashed}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)