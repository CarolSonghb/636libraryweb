from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/staff")
def staff():
    return render_template("base.html")

@app.route("/listbooks")
def listbooks():
    connection = getCursor()
    connection.execute("SELECT * FROM books;")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist = bookList)    

@app.route("/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
inner join books on books.bookid = bookcopies.bookid
 WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate = todaydate,borrowers = borrowerList, books= bookList)

@app.route("/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return redirect("/currentloans")

@app.route("/listborrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("borrowerlist.html", borrowerlist = borrowerList)

@app.route("/currentloans")
def currentloans():
    connection = getCursor()
    sql=""" select br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
            from books b
                inner join bookcopies bc on b.bookid = bc.bookid
                    inner join loans l on bc.bookcopyid = l.bookcopyid
                        inner join borrowers br on l.borrowerid = br.borrowerid
            order by br.familyname, br.firstname, l.loandate;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    print(loanList)
    return render_template("currentloans.html", loanlist = loanList)


@app.route("/search", methods=["POST"])
def search():
    searchTitle = request.form.get('search1') #for the search term Title
    searchAuthor = request.form.get('search2') #for the search term Author
    #give it a new variable so that it can be used in the queries for searching
    searchTitle = "%" + searchTitle + "%" 
    searchAuthor = "%" + searchAuthor + "%"
    #get the variable of whether a user has chosen "and" or "or"
    operator = request.form.get('searchop') 
    #if statements to check the length of the search terms entered so that different queries can be applied
    if len(searchTitle) > 2 and len(searchAuthor) > 2: #when users enter in both fields
        if operator == "or":
            sql = """SELECT * FROM books WHERE booktitle LIKE %s or author LIKE %s;"""
        else:
            sql = """SELECT * FROM books WHERE booktitle LIKE %s and author LIKE %s;"""
    else:
        sql = """SELECT * FROM books WHERE booktitle LIKE %s and author LIKE %s;"""
    connection = getCursor()
    print(sql)
    connection.execute(sql, (searchTitle, searchAuthor,))#two variables passed in
    avaBookList = connection.fetchall()
    return render_template("search.html", booklist = avaBookList)



@app.route("/searchresult", methods=["POST"])
def searchresult():
    searchBook = request.form.get('searchselect')#get the data of the book a user has chosen
    print(searchBook)
    connection = getCursor()
    sql = """SELECT c.bookcopyid, c.format, b.booktitle, b.author, b.category, 
    b.yearofpublication, (CASE WHEN l.returned = 0 THEN "On Loan" ELSE "Available" END) 
    AS status, l.loandate, (CASE WHEN l.returned = 0 THEN adddate(l.loandate, 
    interval 28 day) ELSE " " END ) AS duedate FROM books AS b
    INNER JOIN bookcopies AS c ON b.bookid = c.bookid LEFT JOIN loans AS l 
    ON c.bookcopyid = l.bookcopyid WHERE b.bookid = %s GROUP BY c.bookcopyid ORDER BY loandate DESC, c.format, c.bookcopyid;"""
    print(sql)
    connection.execute(sql, (searchBook,))#one variable passed in
    searchedBookList = connection.fetchall()
    print(searchedBookList)
    return render_template("searchresult.html", searchedbooklist = searchedBookList)


    




