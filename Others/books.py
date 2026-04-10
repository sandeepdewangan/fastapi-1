from typing import Optional

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field

# for explicit status code response
from starlette import status

app = FastAPI()

class Book:
    id: int
    title:str
    author:str
    description:str
    rating:int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

# Field for Request Data Validation
class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="Id is not needed on creating new book")
    title:str = Field(min_length=3, max_length=100)
    author:str = Field(min_length=3, max_length=50)
    description:str = Field(min_length=3, max_length=200)
    rating:int = Field(ge=1, le=5)

    model_config = {
        "json_schema_extra":{
            "example":{
                "title": "A New Book",
                "author": "Author Name",
                "description": "Book description",
                "rating": 5
            }
        }
    }

Books = [
    Book(id=1, title="Operating System", author="Galvin", description="Operating system guide", rating=5),
    Book(id=2, title="Theory of Computation", author="Max", description="TOC guide best book", rating=4),
    Book(id=3, title="Computer Network", author="Tananbaum", description="Networking pratices", rating=5),
    Book(id=4, title="DBMS", author="Navathe", description="DBMS to manage DB", rating=4),
]

# Return explicit status code
@app.get("/books", status_code=status.HTTP_200_OK)
def all_books():
    return Books

# Path Parameter Validations using Path()
@app.get("/books/{id}", status_code=status.HTTP_200_OK)
def get_book_by_id(id:int = Path(gt=0)):
    for book in Books:
        if book.id == id:
            return book
    # Exceptions, if book not found
    raise HTTPException(status_code=404, detail='Item not found')


# Query Parameter Validations using Query()
@app.get("/books/")
def get_book_by_rating(rating:int = Query(ge=1, le=5)):
    books = []
    for book in Books:
        if book.rating == rating:
            books.append(book)
    return books

@app.post("/books/create", status_code=status.HTTP_201_CREATED)
def create_book(book:BookRequest):
    # convert the request to Book object
    new_book = Book(**book.model_dump())
    Books.append(new_book)