import streamlit as st
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from models import Book, Session, Base, engine  # Updated models import

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Function to add a book
def add_book(title, author, isbn="", category="", publication_year=None):
    try:
        with Session() as session:
            new_book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publication_year=publication_year
            )
            session.add(new_book)
            session.commit()
            return True
    except SQLAlchemyError as e:
        st.error(f"Error adding book: {str(e)}")
        return False

# ✅ Cache with Streamlit cache_data
@st.cache_data(ttl=60)
def get_all_books():
    try:
        with Session() as session:
            books = session.query(Book).all()
            books_data = [{
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'category': book.category,
                'publication_year': book.publication_year,
                'status': book.status
            } for book in books]
            return pd.DataFrame(books_data) if books_data else pd.DataFrame()
    except SQLAlchemyError as e:
        st.error(f"Error retrieving books: {str(e)}")
        return pd.DataFrame()

# Function to delete a book
def delete_book(book_id):
    try:
        with Session() as session:
            book = session.query(Book).get(book_id)
            if book:
                session.delete(book)
                session.commit()
                return True
            return False
    except SQLAlchemyError as e:
        st.error(f"Error deleting book: {str(e)}")
        return False

# Main Streamlit app
def main():
    st.title("📚 Bayt al-Hikma: Database Connectivity Personal Library Manager")

    menu = st.sidebar.selectbox(
        "Menu",
        ["View Books", "Add Book", "Delete Book"],
        help="Select an operation to manage your library"
    )

    if menu == "View Books":
        st.header("Your Book Collection")
        books_df = get_all_books()
        if not books_df.empty:
            st.dataframe(
                books_df,
                use_container_width=True,
                column_config={
                    "publication_year": st.column_config.NumberColumn(format="%d")
                }
            )
        else:
            st.info("No books in your library yet. Add some books to get started!")

    elif menu == "Add Book":
        st.header("Add New Book")
        with st.form("add_book_form"):
            title = st.text_input("Title*", help="Required field")
            author = st.text_input("Author*", help="Required field")
            isbn = st.text_input("ISBN", help="10 or 13 digit ISBN number")
            category = st.selectbox(
                "Category",
                ["", "Fiction", "Non-Fiction", "Science", "History", "Technology"],
                index=0
            )
            publication_year = st.number_input(
                "Publication Year",
                min_value=1000,
                max_value=pd.Timestamp.now().year,
                value=pd.Timestamp.now().year
            )

            if st.form_submit_button("Add Book"):
                if title.strip() and author.strip():
                    if add_book(title, author, isbn, category, publication_year):
                        st.success(f"Book '{title}' by {author} added successfully!")
                        st.balloons()
                        get_all_books.clear()  # ✅ clear Streamlit's cached data
                else:
                    st.error("Title and Author are required fields")

    elif menu == "Delete Book":
        st.header("Delete Book")
        books_df = get_all_books()

        if not books_df.empty:
            st.dataframe(books_df, use_container_width=True)
            with st.form("delete_book_form"):
                book_id = st.number_input(
                    "Enter Book ID to delete:",
                    min_value=1,
                    step=1,
                    help="Enter the ID of the book you want to remove"
                )
                if st.form_submit_button("Delete Book"):
                    if delete_book(book_id):
                        st.success(f"Book ID {book_id} deleted successfully")
                        get_all_books.clear()  # ✅ clear Streamlit's cached data
                    else:
                        st.error("Book ID not found")
        else:
            st.info("No books in your library yet.")

if __name__ == "__main__":
    main()
