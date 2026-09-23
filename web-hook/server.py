import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class SheetChangeEvent(BaseModel):
    sheet_name: str
    row: int
    column: int
    value: str | int | float | None
    timestamp: str


@app.post("/webhook")
async def receive_webhook(event: SheetChangeEvent):
    print(f"Получено изменение: Лист '{event.sheet_name}', Строка {event.row}, Колонка {event.column} -> {event.value}")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
