CRUD BOILERPLATE
---
**Starting point for CRUD server with authentication with tokens and db connection.**

Server runs on localhost port 5000, base route returns json with a list of routes.

Other database support is planned.

Available routes:

- GET "/" -> Shows all available routes
- GET "/user" -> Fetches all users from the database
- POST "/user/" -> Register an user with unique email required
- GET "/user/{email}" -> Get user by email
- DELETE "/user/{email}" -> Deletes user registered with email

## To-do:
- [ ] User Login/Registration
- [ ] Tokens
- [ ] CRUD Operations for Users  <br> 1. ~~Create User~~ <br> 2. ~~Get All Users~~ <br> 3. ~~Find User by e-mail~~ <br> 4. ~~Delete User~~ <br> 5. Update User
- [ ] API Testing
- [x] MongoDB support

 