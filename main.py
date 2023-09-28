import models, schemas
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """GET-метод для получения всех пользователей"""
    return db.query(models.User).all()


@app.post("/users")
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    """POST-метод создания пользователя"""
    if(db.query(models.User).filter_by(email=user.email).first() is not None):
        raise HTTPException(status_code=400, detail="user with this email already exists!")
    new_user = models.User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put("/users/{user_id}")
def edit_user(user_id: int, user: schemas.User, db: Session = Depends(get_db)):
    """PUT-метод изменения данных конкретного пользователя"""
    user_to_edit = db.query(models.User).filter_by(id=user_id).first()
    if(user_to_edit is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    user_to_edit.name = user.name
    user_to_edit.email = user.email
    db.commit()
    db.refresh(user_to_edit)
    return user_to_edit


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """DELETE-метод удаления конкретного пользователя"""
    if(db.query(models.User).filter_by(id=user_id).first() is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    db.query(models.User).filter_by(id=user_id).delete()
    db.commit()
    return {"info": "user succesfully deleted"}


@app.get("/users/books")
def get_all_books(db: Session = Depends(get_db)):
    """GET-метод для получения всех книг"""
    return db.query(models.Book).all()


@app.get("/users/{user_id}/books")
def get_user_books(user_id: int, db: Session = Depends(get_db)):
    """GET-метод для получения всех книг, связанных с конкретным пользователем"""
    user = db.query(models.User).filter_by(id=user_id).first()
    if(user is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    return user.books


@app.post("/users/{user_id}/books")
def create_book(user_id: int, book: schemas.Book, db: Session = Depends(get_db)):
    """POST-метод создания книги, привязываемой к конкретному пользователю"""
    if(db.query(models.User).filter_by(id=user_id).first() is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    if(db.query(models.Book).filter_by(name=book.name).first() is not None):
        raise HTTPException(status_code=400, detail="book with this name already exists!")
    new_book = models.Book(name=book.name, description=book.description, user_id=user_id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.put("/users/{user_id}/{book_id}")
def edit_book(user_id: int, book_id: int, book: schemas.Book, db: Session = Depends(get_db)):
    """PUT-метод изменения данных конкретной книги, привязанной к конкретному пользователю"""
    if(db.query(models.User).filter_by(id=user_id).first() is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    book_to_edit = db.query(models.Book).filter_by(id=book_id).first()
    if(book_to_edit is None):
        raise HTTPException(status_code=404, detail="book with this ID not found!")
    book_to_edit.name = book.name
    if(book.description is not None):
        book_to_edit.description = book.description
    db.commit()
    db.refresh(book_to_edit)
    return book_to_edit


@app.delete("/users/{user_id}/{book_id}")
def delete_book(user_id: int, book_id: int, db: Session = Depends(get_db)):
    """DELETE-метод удаления конкретной книги, привязанной к конкретному пользователю"""
    if(db.query(models.User).filter_by(id=user_id).first() is None):
        raise HTTPException(status_code=404, detail="user with this ID not found!")
    if(db.query(models.Book).filter_by(id=book_id).first() is None):
        raise HTTPException(status_code=404, detail="book with this ID not found!")
    db.query(models.Book).filter_by(id=book_id).delete()
    db.commit()
    return {"info": "book succesfully deleted"}


