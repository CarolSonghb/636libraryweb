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
borrowerid = 0

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

#home page for public interface
@app.route("/")
def home():
    return render_template("base.html")

#home page for staff interface
@app.route("/staff")
def staff():
    return render_template("staff.html")

#page for "Search Book" from staff interface
@app.route("/staff/search")
def staffsearch():
    return render_template("staffsearch.html")

#page for "List Books" from public interface
@app.route("/listbooks")
def listbooks():
    connection = getCursor()
    connection.execute("SELECT * FROM books;")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist = bookList)   
 
#page for "Issue Book" from staff interface
@app.route("/staff/issuebook")
def issuebook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    #query to only show digital books and avalable physical books
    sql = """SELECT * FROM bookcopies c INNER JOIN books b 
    ON b.bookid = c.bookid
    WHERE c.format = "eBook" OR c.format ="Audio Book" OR bookcopyid 
    NOT IN (SELECT bookcopyid from loans where returned = 0);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("issuebook.html", loandate = todaydate,borrowers = borrowerList, books= bookList)

#page for updating a new loan
@app.route("/staff/newloan", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return render_template("newloan.html")

#page to show after a new borrower has been added or updating a borrower's detal or 
@app.route("/listborrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("borrowerlist.html", borrowerlist = borrowerList)


@app.route("/search", methods=["POST"])#search for the public page
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

#page to show after a search request has been sent
@app.route("/staff/searchbook", methods=["POST"])
def staffsearchbook():
    searchTitle = request.form.get('staffsearch1') 
    searchAuthor = request.form.get('staffsearch2') 
    searchTitle = "%" + searchTitle + "%" 
    searchAuthor = "%" + searchAuthor + "%"
    operator = request.form.get('staffop') 
    if len(searchTitle) > 2 and len(searchAuthor) > 2: 
        if operator == "or":
            sql = """SELECT * FROM books WHERE booktitle LIKE %s or author LIKE %s;"""
        else:
            sql = """SELECT * FROM books WHERE booktitle LIKE %s and author LIKE %s;"""
    else:
        sql = """SELECT * FROM books WHERE booktitle LIKE %s and author LIKE %s;"""
    connection = getCursor()
    print(sql)
    connection.execute(sql, (searchTitle, searchAuthor,))
    avaBookList = connection.fetchall()
    return render_template("staffsearchbook.html", booklist = avaBookList)

#page to show all copies after a searched book has been selected for public interface
@app.route("/searchresult", methods=["POST"])
def searchresult():
    searchBook = request.form.get('searchselect')
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

#page to show all copies after a searched book has been selected for staff interface
@app.route("/staff/searchresult", methods=["POST"])
def staffsearchresult():
    searchBook = request.form.get('staffselect')
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
    return render_template("staffsearchresult.html", searchedbooklist = searchedBookList)

#page for "Search Borrower" from staff interface
@app.route("/staff/searchborrower")
def searchborrower():
    return render_template("searchborrower.html")

#page to display when users enter borrowerid to search
@app.route("/staff/borrowerid", methods=["POST"])
def searchborrowerid():
    borrowerSearchid = request.form.get('borrowerid')
    global borrowerid
    borrowerid = borrowerSearchid
    print(borrowerSearchid)
    connection = getCursor()
    sql = """SELECT * FROM borrowers WHERE borrowerid = %s;"""
    print(sql)
    connection.execute(sql, (borrowerSearchid,))#one variable passed in
    searchedID = connection.fetchall()
    print(searchedID)
    return render_template("borrowerid.html", searchedborrowerlist = searchedID)

#page to display when users enter borrower name to search
@app.route("/staff/borrowername", methods=["POST"])
def searchborrowername():
    borrowerFirname = request.form.get('borrowerfirname')
    borrowerFamname = request.form.get('borrowerfamname')
    borrowerFirname = "%" + borrowerFirname + "%" 
    borrowerFamname = "%" + borrowerFamname + "%"
    print(borrowerFirname)
    print(borrowerFamname)
    if len(borrowerFirname) > 2 and len(borrowerFamname) == 2:
        sql = """SELECT * FROM borrowers WHERE firstname LIKE %s;"""
        connection = getCursor()
        connection.execute(sql, (borrowerFirname,))
    elif len (borrowerFamname) > 2 and len(borrowerFirname) == 2:
        sql = """SELECT * FROM borrowers WHERE familyname LIKE %s;"""
        connection = getCursor()
        connection.execute(sql, (borrowerFamname,))
    else:
        sql = """SELECT * FROM borrowers;"""
        connection = getCursor()
        connection.execute(sql)
    print(sql)
    searchedname = connection.fetchall()
    print(searchedname)
    return render_template("borrowername.html", searchedborrowerlist = searchedname)

#page for editing borrower details afrer a borrower has been selected   
@app.route("/staff/editborrower", methods=["POST"])
def editborrower():
    borrowerinfo = request.form.get('borrowerselect')
    connection = getCursor()
    print(borrowerinfo)
    sql = """SELECT * FROM borrowers WHERE borrowerid = %s;"""
    print(sql)
    connection.execute(sql, (borrowerinfo,))
    searchedinfo = connection.fetchall()
    print(searchedinfo)
    return render_template("editborrower.html", searchedborrowerlist = searchedinfo)

#page to display updated details then confirm
@app.route("/staff/updateconfirm", methods=["POST"])
def borrowerupdate():
    firstname = request.form.get('firstname')
    familyname = request.form.get('familyname')
    dateofbirth = request.form.get('dobirth')
    housenumbername = request.form.get('housenum')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('pcode')
    print(firstname)
    sql = """UPDATE borrowers SET firstname=%s, familyname=%s, dateofbirth=%s,
     housenumbername=%s, street=%s, town=%s, city=%s, postalcode=%s WHERE borrowerid=%s"""
    connection = getCursor()
    connection.execute(sql, (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode, borrowerid,))
    newsql = """SELECT * FROM borrowers WHERE borrowerid=%s;"""
    connection.execute(newsql, (borrowerid,))
    updateInfo = connection.fetchall()
    print(borrowerid)
    print(newsql)
    print(updateInfo)
    return render_template("updateconfirm.html", updateinfo = updateInfo)

#page for "Add borrower" from staff interface
@app.route("/staff/addborrower")
def addborrower():
    return render_template("addborrower.html")

#page for getting data for a new borrower
@app.route("/staff/newborrower", methods=["POST"])
def newborrower():
    firstname = request.form.get('firstname')
    familyname = request.form.get('familyname')
    dateofbirth = request.form.get('dobirth')
    housenumbername = request.form.get('housenum')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('pcode')
    sql = "INSERT INTO borrowers(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) \
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"
    parameters=(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode)
    print(sql)
    connection = getCursor()
    connection.execute(sql, parameters)
    connection.execute("SELECT * FROM borrowers ORDER BY borrowerid DESC LIMIT 1;")
    updateInfo = connection.fetchall()
    return render_template("newborrower.html", updateinfo = updateInfo)

#page to display after a new loan has been added
@app.route("/staff/newloan")
def newloan():
    return render_template("newloan.html")

#function to display books on loan in a dropdown box
@app.route("/staff/returnbook")
def loanbooklist():
    connection = getCursor()
    sql = """SELECT c.bookcopyid, b.bookid, c.format, b.booktitle, b.author
    FROM bookcopies c LEFT JOIN books b ON b.bookid = c.bookid
    LEFT JOIN loans l ON c.bookcopyid = l.bookcopyid WHERE l.returned = 0
    AND c.format <> "eBook" AND c.format <> "Audio Book" 
    GROUP BY c.bookcopyid ORDER BY b.booktitle, c.format;"""
    connection.execute(sql)
    onLoanlist = connection.fetchall()
    return render_template("returnbook.html", onloanlist = onLoanlist)

#page to update data when users choose a book to return
@app.route("/staff/returnbook", methods=["POST"])
def returnbook():
    connection = getCursor()
    returnbook = request.form.get('returnbook')
    returnBook = returnbook
    print(returnBook)
    sql = """UPDATE loans SET returned = 1 WHERE bookcopyid = %s;"""
    print(sql)
    connection.execute(sql, (returnbook,))
    loansql="""SELECT br.borrowerid, br.firstname, br.familyname, l.borrowerid, 
    l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
    b.category, b.yearofpublication, bc.format FROM books b 
    INNER JOIN bookcopies bc ON b.bookid = bc.bookid
    INNER JOIN loans l ON bc.bookcopyid = l.bookcopyid
    INNER JOIN borrowers br ON l.borrowerid = br.borrowerid
    ORDER BY br.familyname, br.firstname, l.loandate;"""
    connection.execute(loansql)
    loanList = connection.fetchall()
    return render_template("loanreturn.html", loanlist = loanList)

#page for "Overdue Book" from staff interface
@app.route("/staff/overduelist")
def overduelist():
    connection = getCursor()
    sql = """SELECT CONCAT(br.borrowerid, ", ", br.firstname," ", br.familyname) AS fullname,
	   l.bookcopyid, b.booktitle, b.author,
       c.format, l.loandate, 
       (CASE WHEN l.returned = 0 THEN "Overdue" END) AS status, 
       (datediff(now(),l.loandate)) as daysonloan FROM books b
       INNER JOIN bookcopies c ON b.bookid = c.bookid
       INNER JOIN loans l ON c.bookcopyid = l.bookcopyid
       INNER JOIN borrowers br ON l.borrowerid = br.borrowerid
       WHERE l.loandate < (NOW() - INTERVAL 35 DAY) and l.returned <> 1
       ORDER BY br.familyname, br.firstname, l.loandate;"""
    connection.execute(sql)
    overdueList = connection.fetchall()
    print(overdueList)
    return render_template("overduelist.html", overduelist = overdueList)

#page for "Summary" from staff interface to display loan summary and borrower summary
@app.route("/staff/summary")
def summary():
    connection = getCursor()
    loansql = """SELECT b.bookid,c.bookcopyid, b.booktitle, b.author, b.yearofpublication, b.category, c.format,
    COUNT(loanid) AS loantimes FROM books b
    INNER JOIN bookcopies c ON b.bookid = c.bookid
    INNER JOIN loans l ON c.bookcopyid = l.bookcopyid
    GROUP BY c.bookcopyid ORDER BY b.booktitle, loantimes DESC;"""
    connection.execute(loansql)
    loanSummary = connection.fetchall()
    borrowersql = """SELECT br.borrowerid, CONCAT(br.firstname,' ', br.familyname) AS fullname, 
    count(l.borrowerid) AS loantims FROM borrowers br
    LEFT JOIN loans l ON br.borrowerid = l.borrowerid GROUP BY br.borrowerid;"""
    connection.execute(borrowersql)
    borrowerSummary = connection.fetchall()
    return render_template("summary.html", loansummary = loanSummary, borrowersummary = borrowerSummary)



