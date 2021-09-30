# Greatkart
> An eCommerce website created with Python Django framework.
> Live demo [_here_](https://djangokart.com). 


## General Information
- This project focuses on using Python Django framework to develop a fully-featured eCommerce website.
- The website is deployed on Amazon Web Service (AWS).
- This project is based on [this tutorial](https://www.udemy.com/course/django-ecommerce-project-based-course-python-django-web-development/). 


## Technologies Used
- Python Django Framework
- AWS Elastic Beanstalk
- RDS Postgres database
- AWS S3 Bucket
- AWS Route 53


## Features
- ### User Login System
  * Registration with account activation email
  * Login, Logout & Forgot Password
  
- ### My Account Management 
  * User Dashboard & Review Order
  * Edit User Profile & Change Password
  
- ### Product Display
  * Product display in categories
  * Paginator & Search Bar
  
- ### Shopping Cart
  * Add product of choosen variation to cart
  * Increment & Decrement quantity, Remove cart item
  
- ### Order and Payment
  * Place order with billing information
  * Payment by Paypal gateway
  * Generate invoice & Send notification email
  
- ### Review and Rating
  * Interactive rating stars and comment


## Navigate through code
1. HTML templates can be found in directory `templates`.

2. Codes for each feature can be found in below list of directories correspondingly:
>
| Directory | Feature |
| :---: | :---: |
| `accounts` | User Login System, My Account Management |
| `store, category` | Product Display, Review and Rating |
| `carts` | Shopping Cart |
| `orders` | Order and Payment |

3. In each directory, you can mainly check out the following three files:
>
| File | Content |
| :---: | :---: |
| `urls.py`   |  url patterns that direct the user to the corresponding views |
| `views.py`  |  functions that process data based on related models |
| `models.py` |  essential fields and behaviors of data |
