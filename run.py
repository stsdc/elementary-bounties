from app.log import timestamp_log_config
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", log_config=timestamp_log_config(), reload=True)
