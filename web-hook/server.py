import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

ROWS_BUFFER = {}
REQUIRED_COLUMNS = {1, 2, 3, 4, 5}

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

        del ROWS_BUFFER[row_num]
        return {"status": "flushed"}

    return {"status": "buffered"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
