# Division

- main page
- books page
- login page
- sign up page (create user)
- admin page (show all users, admin the users, admin the book)
- find page (searching for a book by filter)

# Book

- author
- title
- id
- genre
- page count
- price

# User

- id
- name
- email
- password(hashed)

# TODO

- [ ] run in docker
- [ ] update documentation (install mongodb)
- [ ] create tests
- [ ] add static files (images)
- [ ] add styling (css)
- [ ] sepeare on multiple files (blueprints?)
- [ ] add sending email functionality
- [ ] fix user authorization

# Cart

Seperated component, which is located ONLY in session.
Not depended on logged in/out user.
Dict model represantion.
Before clicking `order` button app should check whether user is logged in.
After clicking `order` button cart is being cleared.


{
    {author: ..., title: ...}: amount
} 