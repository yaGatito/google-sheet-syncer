import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import pytds
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

ROWS_BUFFER = {}
REQUIRED_COLUMNS = {1, 2, 3, 4, 5} # id, name, desc, type, amount

class SheetEditEvent(BaseModel):
    sheet_name: str
    row: int
    column: int
    value: str | int | float | None
    change_type: str
    timestamp: str

@app.post("/webhook")
async def receive_webhook(event: SheetEditEvent):
    print(f" LOG RECEIVED {event}")

    if event.change_type != "EDIT" or event.row <= 1:
        return {"status": "ignored", "reason": "Not a data edit event"}

    row_num = event.row
    col_num = event.column
    new_value = event.value

    if row_num not in ROWS_BUFFER:
        ROWS_BUFFER[row_num] = {}

    ROWS_BUFFER[row_num][col_num] = new_value

    current_columns = set(ROWS_BUFFER[row_num].keys())

    print(f" LOG: ROWS_BUFFER {ROWS_BUFFER}")

    if REQUIRED_COLUMNS.issubset(current_columns):
        completed_entity = ROWS_BUFFER[row_num]
        print(f" LOG: Row {row_num} is fully populated! Data: {completed_entity}")

        new_product = Product(
            id=ROWS_BUFFER[row_num][1],
            name=ROWS_BUFFER[row_num][2],
            desc=ROWS_BUFFER[row_num][3],
            type=ROWS_BUFFER[row_num][4],
            amount=ROWS_BUFFER[row_num][5]
        )

        flush(new_product)

        del ROWS_BUFFER[row_num]
        return {"status": "flushed"}

    return {"status": "buffered"}

@dataclass
class Product:
    id: str
    name: str
    desc: str
    type: str
    amount: int

def flush(product: Product):
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
            %s AS amount
    ) AS source
    ON target.id = source.id

    WHEN MATCHED THEN
        UPDATE SET
            target.name = source.name,
            target.[desc] = source.[desc],
            target.[type] = source.[type],
            target.amount = source.amount

    WHEN NOT MATCHED THEN
        INSERT (id, name, [desc], [type], amount)
        VALUES (
            source.id,
            source.name,
            source.[desc],
            source.[type],
            source.amount
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
                        product.id,
                        product.name,
                        product.desc,
                        product.type,
                        product.amount,
                    )
                )

                conn.commit()

                print(f"Product {product.id} successfully flushed (UPSERTed).")
    except Exception as e:
        print(f"Error during flush: {e}")
        raise

if __name__ == "__main__":
    # uvicorn.run(app, host="localhost", port=8000)

    new_product = Product(
        id="123",
        name="afds",
        desc="aasd",
        type="aasd",
        amount=4
    )

    flush(new_product)
