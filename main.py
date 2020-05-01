import sqlite3
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("chinook.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks")
async def get_tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.execute(
        """SELECT TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice 
        FROM tracks 
        ORDER BY TrackID 
        LIMIT ? OFFSET ?""",
        (per_page, page * per_page),
    )
    data = cursor.fetchall()
    return data
