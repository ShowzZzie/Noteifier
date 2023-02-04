# Project Name: NOTEIFIER

### Overview
This is a web application built with Flask and SQLAlchemy for users to manage their notes and reminders. The project is a combination of a login/register system, a notes system, and a reminders system.

### Login and Register System
 - The system implements secure password hashing using bcrypt library
 - The password must be at least 8 characters long and must contain at least one digit and one uppercase letter
 - The users can either login to the application using an existing account or register a new account

### Notes System
 - The users can create, edit and delete their notes
 - Notes are sorted based on their priority

### Reminders System
 - The users can create, edit and delete their reminders
 - The reminders are sorted based on their reminder time

### Functionality
 - The user must be logged in to access the notes and reminders functionality
 - The system implements a login-required decorator to secure the functionality

### Technologies Used
 - Flask
 - SQLAlchemy
 - Bcrypt
 - HTML/CSS

### How to run
You can either use the code on your own or by accessing this website: 