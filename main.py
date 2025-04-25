from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_conn, release_conn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vessapro.github.io"],
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

    chat_id = user_id
    name = ''  # force kosong untuk bypass NOT NULL constraint

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (user_id, chat_id, name, mt5_login, mt5_password, mt5_broker, risk_type, risk_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET
                mt5_login = EXCLUDED.mt5_login,
                mt5_password = EXCLUDED.mt5_password,
                mt5_broker = EXCLUDED.mt5_broker,
                risk_type = EXCLUDED.risk_type,
                risk_value = EXCLUDED.risk_value;
        """, (user_id, chat_id, name, login, password, broker, risk_type, risk_value))

        conn.commit()
        return JSONResponse(content={"message": "✅ MT5 account saved successfully."})
    except Exception as e:
        print("❌ Error saving MT5 data:", e)
        return JSONResponse(content={"error": "DB error"}, status_code=500)
    finally:
        release_conn(conn)
