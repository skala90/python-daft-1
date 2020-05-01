import sqlite3
from fastapi import FastAPI, HTTPException, status

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
        raise HTTPException(
            status_code=404, detail={"error": "This composer does not have any songs."}
        )
    return data


@app.post("/albums", status_code=status.HTTP_201_CREATED)
async def add_new_album(album_details: dict):
    app.db_connection.row_factory = lambda cursor, row: row[0]
    cursor = app.db_connection.execute(
        """SELECT ArtistId
        FROM artists
        WHERE ArtistId = ?""",
        (album_details["artist_id"],),
    )
    artist = cursor.fetchall()
    if len(artist) == 0:
        raise HTTPException(
            status_code=404, detail={"error": "There is no artist with such ID."}
        )
    else:
        cursor = app.db_connection.execute(
            """INSERT INTO albums (artistid, title) VALUES (?,?)""",
            (album_details["artist_id"], album_details["title"]),
        )
        app.db_connection.commit()
        new_album_id = cursor.lastrowid
        
        app.db_connection.row_factory = sqlite3.Row
        cursor = app.db_connection.execute(
            """SELECT AlbumId, Title, ArtistId
        FROM albums 
        WHERE AlbumId = ?""",
            (new_album_id,),
        )
        new_album_data = cursor.fetchall()
        return new_album_data[0]

@app.get("/album/{album_id}")
async def get_album_data(album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.execute(
            """SELECT AlbumId, Title, ArtistId
            FROM albums 
            WHERE AlbumId = ?""",
            (album_id,),
        )
    album_data = cursor.fetchone()
    if len(album_data) == 0:
        # return {"detail": {"error": "This composer does not have any songs."}}
        raise HTTPException(
            status_code=404, detail={"error": "There is no album with such ID."}
        )
    
    return album_data