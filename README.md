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
- PUT "/user/{email}" -> Updates user registered with email

## To-do:
- [ ] Tokens
- [ ] Config File
- [ ] User Login/Registration
- [ ] Pagination
- [ ] Deploy on HEROKU
- [ ] Kafka
- [ ] Redis
- [x] API Testing
- [x] CRUD Operations for Users
- [x] MongoDB support
