import sqlite3
from fastapi import FastAPI, HTTPException

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


@app.get("/tracks/composers")
async def get_composers(composer_name: str):
    app.db_connection.row_factory = lambda cursor, row: row[0]
    cursor = app.db_connection.execute(
        """SELECT Name
        FROM tracks
        WHERE Composer = ?
        ORDER BY Name""",
        (composer_name,),
    )
    data = cursor.fetchall()
    if len(data) == 0:
        # return {"detail": {"error": "This composer does not have any songs."}}
        raise HTTPException(status_code=404, detail={"error":"This composer does not have any songs."})
    return data
