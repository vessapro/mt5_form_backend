from fastapi import FastAPI, Form
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
async def save_mt5_data(
    user_id: int = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    broker: str = Form(...),
    risk_type: str = Form(...),
    risk_value: str = Form(...)
):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET mt5_login = %s,
                mt5_password = %s,
                mt5_broker = %s,
                risk_type = %s,
                risk_value = %s
            WHERE user_id = %s;
        """, (login, password, broker, risk_type, risk_value, user_id))

        conn.commit()
        return JSONResponse(content={"message": "✅ MT5 details updated!"})
    except Exception as e:
        print("❌ Error saving MT5 data:", e)
        return JSONResponse(content={"error": "DB error"}, status_code=500)
    finally:
        release_conn(conn)
