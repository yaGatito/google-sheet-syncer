import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pytds
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

class ProductEvent(BaseModel):
    id: int
    name: str
    desc: str
    type: str
    amount: int
    extra: str

@app.post("/webhook")
def receive_webhook(event: ProductEvent):
    print(f"Received event: {event}")

    product = Product(
        id=event.id,
        name=event.name,
        desc=event.desc,
        type=event.type,
        amount=event.amount,
        extra=event.extra
    )

    upsertProduct(product)

@dataclass
class Product:
    id: str
    name: str
    desc: str
    type: str
    amount: int
    extra: str

def upsertProduct(p: Product):
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

    query = """
    MERGE Products AS target
    USING (
        SELECT
            %s AS id,
            %s AS name,
            %s AS [desc],
            %s AS [type],
            %s AS amount,
            %s AS extra
    ) AS source
    ON target.id = source.id

    WHEN MATCHED THEN
        UPDATE SET
            target.name = source.name,
            target.[desc] = source.[desc],
            target.[type] = source.[type],
            target.amount = source.amount,
            target.extra = source.extra

    WHEN NOT MATCHED THEN
        INSERT (id, name, [desc], [type], amount, extra)
        VALUES (
            source.id,
            source.name,
            source.[desc],
            source.[type],
            source.amount,
            source.extra
        );
    """

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
                    query,
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

                print(f"Product {p.id} successfully upserted.")
    except Exception as e:
        print(f"Error during flush: {e}")
        raise
