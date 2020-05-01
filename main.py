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
        new_album_data = cursor.fetchone()
        return new_album_data


@app.get("/albums/{album_id}")
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


@app.put("/customers/{customer_id}")
async def edit_customer_data(customer_id: int, customer_update_data: dict):
    cursor = app.db_connection.execute(
        "SELECT CustomerId FROM customers WHERE CustomerId = ?", (customer_id,)
    )
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(
            status_code=404, detail={"error": "Customer with given ID does not exist."}
        )
    list_of_possible_fields_to_update = (
        "company",
        "address",
        "city",
        "state",
        "country",
        "postalcode",
        "fax",
    )
    fields_to_update = []

    for key, val in customer_update_data.items():
        if key in list_of_possible_fields_to_update:
            fields_to_update.append(f"{key}='{val}'")

    update_values = ", ".join(fields_to_update)
    sql_stmt = f"UPDATE customers SET {update_values} WHERE customerid={customer_id}"
    cursor = app.db_connection.execute(sql_stmt)
    app.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.execute(
        "SELECT * FROM customers WHERE CustomerId = ?", (customer_id,)
    )
    customer = cursor.fetchone()
    return customer

@app.get("/sales")
async def get_sales(category:str):

    if category == "customers":
        sql_stmt = """
        SELECT a.CustomerId, a.Email, coalesce(a.Phone,'None') as Phone, round(Sum(b.Total),2) as Sum
        from customers a
        inner join invoices b on a.customerId=b.CustomerId
        group by a.CustomerId, a.Email, a.Phone
        order by sum(b.Total) desc, a.CustomerId desc 
        """
        app.db_connection.row_factory = sqlite3.Row
        cursor = app.db_connection.execute(sql_stmt)
        
        customer = cursor.fetchall()
        return customer
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Not implemented."}
        )