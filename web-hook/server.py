import os
import logging
from fastapi import Header, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pytds
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
app = FastAPI()

logger = logging.getLogger("uvicorn")

UPSERT_PRODUCT_QUERY = (
    Path(__file__).parent / "sql" / "upsert_product.sql"
).read_text()

class ProductEvent(BaseModel):
    id: int
    name: str
    desc: str
    type: str
    amount: int
    extra: str

@app.post("/webhook")
def receive_webhook(
    event: ProductEvent,
    x_webhook_secret: str = Header(...)
):
    if x_webhook_secret != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(status_code=401, detail="Invalid secret")

    logger.info(f"Received product event: {event.id}")

    product = Product(
        id=event.id,
        name=event.name,
        desc=event.desc,
        type=event.type,
        amount=event.amount,
        extra=event.extra
    )

    upsert_product(product)

    return {"status": "ok"}

@dataclass
class Product:
    id: int
    name: str
    desc: str
    type: str
    amount: int
    extra: str

def upsert_product(p: Product):
    db_server = os.getenv("MSSQL_HOST")
    db_port = os.getenv("MSSQL_PORT")
    db_name = os.getenv("MSSQL_DB_NAME")
    db_user = os.getenv("MSSQL_USER")
    db_password = os.getenv("MSSQL_SA_PASSWORD")

    required_config = {
        "MSSQL_HOST": db_server,
        "MSSQL_PORT": db_port,
        "MSSQL_DB_NAME": db_name,
        "MSSQL_USER": db_user,
        "MSSQL_SA_PASSWORD": db_password,
    }

    missing = [key for key, value in required_config.items() if not value]

    if missing:
        raise RuntimeError(
            f"Missing database configuration: {', '.join(missing)}"
        )

    try:
        with pytds.connect(
            server=db_server,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_password,
            cafile=None,
            validate_host=False,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    UPSERT_PRODUCT_QUERY,
                    (
                        str(p.id),
                        str(p.name),
                        str(p.desc),
                        str(p.type),
                        int(p.amount),
                        str(p.extra),
                    )
                )

                conn.commit()

                logger.info(f"Product {p.id} successfully upserted.")
    except Exception as e:
        logger.error(f"Error during flush: {e}")
        raise
