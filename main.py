from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_conn, release_conn

app = FastAPI()

# ✅ CORS supaya Telegram WebApp (GitHub Pages) boleh akses
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vessapro.github.io",  # ✅ Guna ni kalau deploy dekat GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "✅ MT5 Form Backend is running."}

@app.post("/save_mt5_data")
async def save_mt5_data(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    login = data.get("login")
    password = data.get("password")
    broker = data.get("broker")
    risk_type = data.get("risk_type")
    risk_value = data.get("risk_value")

    if not all([user_id, login, password, broker, risk_type, risk_value]):
        return JSONResponse(content={"error": "❌ Missing required fields"}, status_code=400)

    try:
        conn = get_conn()
        cur = conn.cursor()

        # ✅ Update existing user row (replace values if already exists)
        cur.execute("""
            UPDATE users SET
                mt5_login = %s,
                mt5_password = %s,
                mt5_broker = %s,
                risk_type = %s,
                risk_value = %s
            WHERE user_id = %s
        """, (login, password, broker, risk_type, risk_value, user_id))
        conn.commit()

        return JSONResponse(content={"message": "✅ MT5 account saved successfully."})
    except Exception as e:
        print("❌ Error saving MT5 data:", e)
        return JSONResponse(content={"error": "DB error"}, status_code=500)
    finally:
        release_conn(conn)
