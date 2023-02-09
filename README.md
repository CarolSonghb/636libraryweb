# 636libraryweb Report
##### Student ID: 1154836
##### Student name: Haibei(Carol) Song

--------------------------------------------------------

### Table of Content
##### 1. Structure of the Website
##### 2. Assumptions and Design Decisions
##### 3. Discussion of Possible Changes to Support Multiple Library Branches

--------------------------------------------------------
*1. Structure of the Website*   
   
The website for Waikirikiri Library contains two interfaces. One is for
public and the other one is for staff. 
The public page has two main templates, which are linked to "Search Book" and View "List Books".
The staff page has seven main templates, which are for "Search Book", "Search Borrower", "Add Borrower", "Issue Book", "Returen Book", "Overdue Book" and "Summary".
How routes and functions are generated from the templates and how data is passed between them are displayed in the following image.
![This is an image](/structure.001.jpeg)

*2. Assumtions and Design Decisions*  
   
**Assumtion/Decision 1:** All staff know the url to the staff page is /staff, so there is no access to the staff page from the public one. 
    
**Assumtion/Decision 2:** Digital copy(eBook, Audio book) of books are always available, no matter how many people have borrowed them. 
    
Digital copy of books would have an available period of time (eg. 30 days). The file will expire after that period of time so that borrowers would not be able to view it again, which makes it no need to return them.  
   
**Assumtion/Decision 3:** There would be a sticker showing bookcopy ID on each physical copy of book. When a borrower comes to a staff to return this book, the staff can choose the book on loan according to the bookcopy ID shown on the sticker.  
   
**Assumtion/Decision 4:**  If a borrower or a staff does not know either book ID or name of a book, or they accidently click the search button without typing anything, a list of all books in the library will automatically show on the page.     
   
The same rule also applies to the "Search Borrower" page, if a user doesn't make any input at the name input fields and clicks "Check Name", a full list of borrowers will display on the screen. 
    
**Assumtion/Decision 5:**  When using the search functions(for books and borrowers) provided, there will be time that they make a typo or simply change their minds of what they want to search. Apart from a remind message shows up on the page when no matching results returned, a new search option is always displayed above the search results for quicker and easier access.
The same rule also applies to after a new loan is added. There is another pair of selection boxes displayed for quick access.  
  
**Assumtion/Decision 6:**  When a loan is returned, users might wonder if the action has really been made and if the status of the book is changed. That is why there will be a "Loan History Report" displayed for them to check.
   
   
*3. Discussion of Possible Changes to Support Multiple Library Branches*   
   
To support multiple library branches, the database would need a new table, maybe called "libraries" that has information from different branches, such as a libraryid, name, location, and contact number. It would become a parent table for the "books", and the libraryid the parent field for the bookid of "books".  
  
For the web app, the book list that shows availablity would also have the library branch displayed, indicating if a book is available at different braches. Users would also be able to first choose a branch to see book status at that library.
  
At the staff page, the staff will first choose a branch of the library that they would be working at. If the branch is not chosen at the start, when a staff is working on issuing books or returning, they will be reminded to choose a branch then.