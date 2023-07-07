from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import csv
import os
from Intermediate import *
from PIL import Image
import secrets
import pandas as pd
import shelve
from forms import RegisterForm, LoginForm, ProfileForm, AdminLoginForm, CreateAdminForm, UpdateProfilePicForm, remove_user
from forms import addproduct, addtocart, updatecart, cnfrmorder, updateProduct, update, feedbackform, FaqForm
from datetime import datetime

# create app
app = Flask(__name__)

# configure app
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

# configuring folders in the app which will be used to store images for users and products
app.config['profile_pics'] = 'static/profile_pics'
app.config['product_pics'] = 'static/product_pics'

# function which displays the home page


@app.route('/', methods=['GET', 'POST'])
def home():

    return render_template('home.html')

############# user routes #############

# function which displays the user registration page


@app.route('/register', methods=['GET', 'POST'])
def register():
    # creating an instance of the RegisterForm class
    form = RegisterForm()
    # necessary variables to store the user input
    username = None
    email = None
    password1 = None
    password2 = None
    address = None
    postal_code = None
    # if the request method is POST, the form is validated
    if request.method == "POST":
        if form.validate():
            # the user input is stored in the variables
            username = request.form['username']
            email = request.form['email_address']
            password1 = request.form['password1']
            password2 = request.form['password2']
            address = request.form['address']
            postal_code = request.form['postal_code']
            # if the user input is valid, the user is added to the database
            # validation is done in the validate_registration function
            if validate_registration(email, username):
                # the user is added to the database using the add_user function
                add_user(username, email, password1, address, postal_code)
                flash('Account created successfully!', category='success')
                # the user is redirected to the marketplace page
                return redirect(url_for('product', username=username, profile=find_profile_pic(username)))
            # if the user input is invalid, the user is redirected to the registration page again
            else:
                flash('Username or Email already exists', category='danger')
        # the errors are displayed to the user using flash messages
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with creating a user: {err_msg}', category='danger')
    # the registration page is rendered
    return render_template('register.html', form=form)

# function which diisplays the user modification page


@ app.route('/modify', methods=['GET', 'POST'])
def ModifyUser():
    # getting the username from the url
    username = request.args.get('username')
    # getting the profile picture from the url
    image_fn = request.args.get('profile')
    # creating an instance of the ProfileForm class
    form = ProfileForm()
    # if the request method is GET, the user details are retrieved from the database
    if request.method == 'GET':
        # the user details are retrieved from the database by creating an instance of the shelve class
        user_file = shelve.open("users")
        # the user details are stored in a list
        users = user_file['users']
        # the user details are retrieved from the list
        for user in users:
            if user[0] == username:
                # the user details are displayed pn the form
                form.username.data = user[0]
                form.email_address.data = user[1]
                form.password.data = user[2]
                form.address.data = user[4]
                form.postal_code.data = user[5]
    # if the request method is POST, the form is validated
    if request.method == "POST":
        if form.validate():
            # the user input is stored in the variables
            previous_username = request.args.get('username')
            username = request.form['username']
            email = request.form['email_address']
            password = request.form['password']
            address = request.form['address']
            postal_code = request.form['postal_code']
            previous_mail = get_prev_mail(previous_username)
            # if the user input is valid, the user is modified in the database
            # email and username validation is done in the check_email and check_username functions
            # password validation is done in the CheckExistingPassword function
            if (((check_email(email) == False) or (email == previous_mail)) and ((check_username(username) == False) or username == previous_username)):
                # the user is modified in the database using the modify_user function
                modify_user(previous_username, username,
                            email, password, address, postal_code)
                flash('Account updated successfully!', category='success')
                return redirect(url_for('product', username=username, profile=image_fn))
            # if there was error in the user input, the user is redirected to the modification page again
            # the errors are displayed to the user using flash messages

            else:
                if check_email(email):
                    flash('Email already exists', category='danger')
                elif username == previous_username and check_username(username):
                    flash('New Username already exists', category='danger')
                elif form.image_file.data:
                    flash('Please Select an Image', category='danger')
                else:
                    flash('Username or Email already exists',
                          category='danger')
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with updating information: {err_msg}', category='danger')
    return render_template('update.html', form=form, username=username, profile=image_fn)


@ app.route('/userpic', methods=['GET', 'POST'])
def userpic():
    # getting the username from the url
    username = request.args.get('username')
    # getting the profile picture from the url
    image_fn = request.args.get('profile')
    # creating an instance of the ProfileForm class
    form = UpdateProfilePicForm()
    if request.method == "POST":
        if form.validate():
            image_fn_1 = save_picture(form.image_file.data)
            image_fn = url_for(
                'static', filename='profile_pics/' + image_fn_1)
            modify_user_pic(username, image_fn_1)
            flash("Picture Updated Successfully!")
            return redirect(url_for('product', username=username, profile=image_fn))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                f'There was an error with updating information: {err_msg}', category='danger')
    return render_template('modifypic.html', form=form, username=username, profile=image_fn)

    # function which checks if the password entered by the user is indeed the existing password


def CheckExistingPassword(username, password):
    user_file = shelve.open("users")
    users = user_file['users']
    user_file.close()
    for user in users:
        if user[0] == username:
            if user[2] == password:
                return True
            else:
                return False

# function which saves the profile picture in the folder


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if not os.path.exists(os.path.join(app.root_path, 'static/profile_pics')):
        os.makedirs(os.path.join(app.root_path, 'static/profile_pics'))
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

# function which checks if the user is using his existing email address


def get_prev_mail(username):
    user_file = shelve.open("users")
    users = user_file['users']
    for user in users:
        if user[0] == username:
            return user[1]


# function to find the profile picture of the user
def find_profile_pic(username):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        for user in users:
            if user[0] == username:
                return os.path.join(app.config['profile_pics'], user[3])
    except:
        return "default.jpeg"


# function which displays the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # creating an instance of the LoginForm class
    form = LoginForm()
    # if the request method is GET, the username is retrieved from the url
    if request.method == "GET":
        username = request.args.get('username')
    # if the request method is POST, the form is validated
    if request.method == "POST":
        cart_file = shelve.open("cart")
        cart_file['cart'] = []
        cart_file.close()
        if form.validate():
            # the user input is stored in the variables
            username = request.form['username']
            password = request.form['password']
            # check if the user exists in the database
            if validate_login(username, password):
                flash('Logged in successfully!', category='success')
                # redirecting him to the product page
                return redirect(url_for('product', username=username, profile=find_profile_pic(username)))
            else:
                flash('Username or Password is incorrect', category='danger')
        # if there were errors in the user input, the user is redirected to the login page again
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with logging in: {err_msg}', category='danger')
    return render_template('login.html', form=form, username=username, profile=find_profile_pic(username))


# function which displays the the market (product) page
@app.route('/product', methods=['GET', 'POST'])
def product():
    # these variables are used to store the total and gst of a shopping cart
    total = 0

    gst = 0
    # calclate total
    # open cart file and store data in an array named cart
    cart_file = shelve.open("cart")
    cart = cart_file['cart']
    cart_file.close()
    # calculate total and gst
    for prod in cart:
        total += int(prod[1])*int(prod[3])
        gst += int(prod[5])
    # open products file and store data in an array named products
    product_file = shelve.open("products")
    #  the username is retrieved from the url
    username = request.args.get('username')
    # the products are stored in an array named products
    products = product_file['prods']
    product_file.close()
    image_link = url_for('static', filename='product_pics')
    # creating an instance of the AddToCartForm class
    cartform = addtocart()
    if request.method == "GET":
        username = request.args.get('username')
        # the user is redirected to the product page
        return render_template("products.html", products=products, image=image_link, form=cartform, username=username, profile=find_profile_pic(username), total=total, gst=gst)
    if request.method == "POST":
        # the user input is stored in the variables
        username = request.args.get('username')
        prod_name = request.args.get('product_name', None)
        # check if the product is already in the cart
        if not checkcart(prod_name):
            for pro in products:
                if pro[0] == prod_name:
                    # add_to_cart
                    # check if the prod_name already exist in cart or not
                    # if not, add the product to the cart
                    add_to_cart(pro)
                    cart_file = shelve.open("cart")
                    cart = cart_file['cart']
                    cart_file.close()
                    for prod in cart:
                        total += int(prod[1])*int(prod[3])
                        gst += int(prod[5])

                    flash('Product added to cart successfully!',
                          category='success')
                    return render_template("products.html", form=cartform, products=products, image=image_link, username=username, profile=find_profile_pic(username), total=total, gst=gst)
        else:
            flash('Product already in cart!', category='danger')
            return render_template("products.html", form=cartform, products=products, image=image_link, username=username, profile=find_profile_pic(username), total=total, gst=gst)

    return render_template("products.html", form=cartform, products=products, image=image_link, username=username, profile=find_profile_pic(username))


# function which adds a product to the cart
def add_to_cart(prod):
    # create a list of the product attributes
    prod = [prod[0],
            prod[1],
            prod[2],
            1,
            prod[4],
            prod[5]]

    # try
    try:
        # open cart file and store data in an array named cart
        cart_file = shelve.open("cart")
        # add the information of the product to the cart
        cart = list(cart_file['cart'])
        cart.append(prod)
        # close the cart file
        cart_file['cart'] = cart
        cart_file.close()
    # except
    except:
        # create a new cart file
        # add the information of the product to the cart
        cart = []
        cart.append(prod)
        cart_file = shelve.open("cart")
        cart_file['cart'] = cart
        cart_file.close()


# functions which displays the cart page
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    try:
        # create an instance of the and cnfrmorder UpdateCartForm class
        cform = cnfrmorder()
        form = updatecart()
        # these variables are used to store the total and gst of a shopping cart
        total = 0

        gst = 0
        # opeing cart file and storing data in an array named cart
        cart_file = shelve.open("cart")
        cart = cart_file['cart']
        cart_file.close()
        # calculate total and gst
        for prod in cart:
            total += int(prod[1])*int(prod[3])

            gst += int(prod[5])

        username = request.args.get('username')
        image_link = url_for('static', filename='product_pics')
        # open cart file and store data in an array named cart
        cart_file = shelve.open("cart")
        cart = cart_file['cart']
        cart_file.close()
        # open products
        product_file = shelve.open("products")
        products = product_file['prods']
        product_file.close()
        if request.method == "GET":
            return render_template("cart.html", cart=cart, image=image_link, form=form, username=username, cform=cform, profile=find_profile_pic(username), total=total, gst=gst)
        if request.method == "POST":
            # get product name
            prod_name = request.args.get('product_name', None)
            # get quantity
            quantity = request.form['quantity']
            # check if quantity is integer
            if quantity.isdigit() and int(quantity) >= 0:
                # check if products quantity is greater than quantity selected
                for item in products:
                    if item[0] == prod_name:
                        if int(quantity) <= 0:
                            # remove item from cart
                            for pro in cart:
                                if pro[0] == prod_name:
                                    cart.remove(pro)
                            # update cart file
                            cart_file = shelve.open("cart")
                            cart_file['cart'] = cart
                            cart = cart_file['cart']
                            cart_file.close()

                        if int(item[3]) >= int(quantity):
                            # update cart quantity
                            for pro in cart:
                                if pro[0] == prod_name:
                                    pro[3] = quantity

                            # update cart file
                            cart_file = shelve.open("cart")
                            cart_file['cart'] = cart
                            cart = cart_file['cart']
                            cart_file.close()
                            # create updated bill
                            total = 0
                            gst = 0
                            for pro in cart:
                                total = total+int(pro[1])*int(pro[3])
                                # calculate gst

                                gst += int(pro[5])

                            flash('Cart updated successfully!',
                                  category='success')
                            return render_template("cart.html", cart=cart, image=image_link, form=form, total=total, username=username, cform=cform, profile=find_profile_pic(username), gst=gst)

                        else:
                            flash(
                                'Quantity selected is greater than quantity available!', category='danger')
                            return render_template("cart.html", cart=cart, image=image_link, form=form, total=total, username=username, cform=cform, profile=find_profile_pic(username), gst=gst)

            else:
                flash('Quantity selected is invalid!', category='danger')
                return render_template("cart.html", cart=cart, image=image_link, form=form, total=total, username=username, cform=cform, profile=find_profile_pic(username), gst=gst)

    except:
        pass
    # if the user presses the place order button
    if request.form['Place Order'] == 'Place Order':
        # get product name
        prod = request.args.get('cart', None)
        username = request.args.get('username')
        # open cart file and store data in an array named cartitems
        cart_file = shelve.open("cart")
        cartitems = cart_file['cart']
        cart_file.close()

        # check if cart is empty
        if len(cartitems) == 0:
            flash('Cart is empty!', category='danger')
            return render_template("response.html", cart=cart, image=image_link, form=form, total=total, username=username, cform=cform, profile=find_profile_pic(username), gst=gst)

        # update products file based in the prod array
        for pro in products:
            for item in cart:
                if pro[0] == item[0]:
                    pro[3] = int(pro[3])-int(item[3])
        # update products file
        product_file = shelve.open("products")
        product_file['prods'] = products
        product_file.close()
        # store data of user and prod in file name record
        try:
            record_file = shelve.open("record")
            record = list(record_file['record'])
            record.append([username, cart, datetime.now()])
            record_file['record'] = record
            record_file.close()
        # except
        except:
            record = []
            record.append([username, cart, datetime.now()])
            record_file = shelve.open("record")
            record_file['record'] = record
            record_file.close()
        # empty cart
        cart_file = shelve.open("cart")
        cart_file['cart'] = []
        cart_file.close()
        flash('Order placed successfully we will contact u in a while',
              category='success')
        return render_template("response.html", products=products, image=image_link, form=form, total=total, cform=cform, username=username, profile=find_profile_pic(username), gst=gst)

    return render_template("cart.html", cart=cart, image=image_link, form=form, total=total, cform=cform, username=username, profile=find_profile_pic(username), gst=gst)


# function to check if product is in cart
def checkcart(prod):
    cart_file = shelve.open("cart")
    cart = cart_file['cart']
    cart_file.close()
    for item in cart:
        if item[0] == prod:
            return True
    return False

# function which shows the feedback page


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    # create form object
    form = feedbackform()
    # get username
    username = request.args.get('username')

    if request.method == "GET":
        return render_template("feedback.html", form=form, username=username, profile=find_profile_pic(username))
    # if the user presses the submit button
    if request.method == "POST":
        # get data from form
        feedbackmes = request.form['feedback']
        experience = request.form['experience']
        # store data of user and prod in file name feedback record
        # save data in file
        try:
            feedback_file = shelve.open("feedback")
            feedback = list(feedback_file['feedback'])
            feedback.append(
                [username, feedbackmes, experience, datetime.now()])
            feedback_file['feedback'] = feedback
            feedback_file.close()
        # except
        except:
            feedback = []
            feedback.append(
                [username, feedbackmes, experience, datetime.now()])
            feedback_file = shelve.open("feedback")
            feedback_file['feedback'] = feedback
            feedback_file.close()
        flash('Feedback submitted successfully!', category='success')
        return render_template("response.html", username=username, profile=find_profile_pic(username))
    return render_template("feedback.html", form=form, username=username, profile=find_profile_pic(username))


# function which shows the view history page
@app.route('/viewhistory', methods=['GET', 'POST'])
def viewhistory():
    username = request.args.get('username')
# open record file and store data in an array named record
    record_file = shelve.open("record")
    record = list(record_file['record'])
    record_file.close()
# get all the history of products bought by the user
    for i in range(len(record)):
        for j in range(len(record[i])):
            # check if record[i][j] is not of type datetime
            if not isinstance(record[i][j], datetime):

                for k in record[i][j]:
                    # check if k is list
                    if isinstance(k, list):
                        for l in range(len(k)):
                            # check if k[l] is a string and is digit is not a date
                            if isinstance(k[l], str) and k[l].isdigit() and k[l] != "2020":
                                k[l] = int(k[l])

    # udate in record file
    record_file = shelve.open("record")
    record_file['record'] = record
    record_file.close()

    return render_template("viewhistory.html", record=record, username=username, profile=find_profile_pic(username))

# function which shows the faq page


@app.route('/faq', methods=['GET', 'POST'])
def faq():
    # get username
    username = request.args.get('username')
    form = FaqForm()
    if request.method == "GET":
        return render_template("faq.html", form=form, username=username, profile=find_profile_pic(username))
    # if the user presses the submit button
    if request.method == "POST":
        question = request.form['question']
        # store data of user and prod in file name feedback record
        try:
            faq_file = shelve.open("faq")
            faq = list(faq_file['faq'])
            faq.append([username, question, datetime.now()])
            faq_file['faq'] = faq
            faq_file.close()
        # except
        except:
            faq = []
            faq.append([username, question, datetime.now()])
            faq_file = shelve.open("faq")
            faq_file['faq'] = faq
            faq_file.close()
        flash('Question submitted successfully!', category='success')
        return render_template("response.html", username=username, profile=find_profile_pic(username))

    return render_template("faq.html", username=username, profile=find_profile_pic(username))


################## Admin Routes ###################

# function to display admin login page
@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    # create form object
    form = AdminLoginForm()
    # variable to store email and password
    email = None
    password = None
    # if the user presses the submit button
    if request.method == "POST":
        if form.validate():
            # get data from form
            email = request.form['email']
            password = request.form['password']
            # check if email and password is correct
            if validate_admin(email, password):
                flash('Logged in successfully!', category='success')
                return redirect(url_for('admin_home'))
            else:
                flash('Email or Password is incorrect', category='danger')
        # if there are errors display them
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with logging in: {err_msg}', category='danger')
    return render_template("admin_login.html", form=form)


# function to validate admin login
def validate_admin(email, password):
    try:
        admin_file = shelve.open("admin")
        admins = admin_file['admin']
        is_email = False
        is_password = False
        for admin in admins:
            if email == admin[4]:
                is_email = True
                if password == admin[5]:
                    is_password = True
                    break
        if is_email and is_password:
            admin_file.close()
            return True
        else:
            admin_file.close()
            return False
    except:
        admins = []
        admins.append(['Admin', 'Account',  '+62311 8559959',
                      'M', 'admin@gmail.com', 'admin@', '47010'])
        admin_file['admin'] = admins
        return False


# function to display admin registration page
@app.route('/admin_registration', methods=['GET', 'POST'])
def create_admin():
    # new variables to store data
    first_name = None
    last_name = None
    phone_no = None
    gender = None
    email_address = None
    password = None
    postal_code = None

    form = CreateAdminForm()
# if the user presses the submit button
    if request.method == "POST":
        # validate form
        if form.validate():
            # get data from form
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            phone_no = request.form['phone_no']
            gender = request.form['gender']
            email_address = request.form['email_address']
            password = request.form['password']
            postal_code = request.form['postal_code']
            # check if email already exists
            if validate_admin_email(email_address) == False:
                # check if postal code is valid
                if validate_postalcode(postal_code):
                    # create admin
                    add_admin(first_name, last_name, phone_no, gender,
                              email_address, password, postal_code)
                    flash('Admin created successfully!', category='success')

                    return redirect(url_for('admin_home'))
            # display all errors
                else:
                    flash('Invalid postal code ', category='danger')

            else:
                flash('Email already exists', category='danger')

        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with Registration: {err_msg}', category='danger')
    return render_template("admin_registration.html", form=form, )


# function to validate postal code
def validate_postalcode(postalcode):
    postalcode = str(postalcode)
    if len(postalcode) > 6 or len(postalcode) < 4:
        return False
    if not postalcode.isdigit():
        return False
    return True

# function to validate email for admin


def validate_admin_email(email):
    try:
        admin_file = shelve.open("admin")
        admins = admin_file['admin']
        for admin in admins:
            if email == admin[4]:
                return True
        admin_file.close()
        return False
    except:
        admin_file.close()
        return False

# function to add admin


def add_admin(first_name, last_name, phone_no, gender, email_address, password, postal_code):
    try:
        admin_file = shelve.open("admin")
        admins = admin_file['admin']
        admins.append([first_name, last_name, phone_no, gender,
                      email_address, password, postal_code])
        admin_file['admin'] = admins
        admin_file.close()
    except:
        admins = []
        admins.append([first_name, last_name, phone_no, gender,
                      email_address, password, postal_code])
        admin_file['admin'] = admins
        admin_file.close()

# function to display admin home page


@app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():

    return render_template("admin_home.html")

# function to display admin products page


@app.route('/admin_see_products', methods=['GET', 'POST'])
def admin_products():
    product_file = shelve.open("products")
    products = product_file['prods']
    product_file.close()
    image_link = url_for('static', filename='product_pics')
    form = update()
    if request.method == "GET":
        # getting all products
        prod_name = request.args.get('prod_name', None)
        product_pic = request.args.get('product_pic', None)
    if request.method == "POST":
        # displaying all the products
        prod_name = request.args.get('prod_name', None)
        product_pic = request.args.get('product_pic', None)
        product_pic_1 = url_for(
            'static', filename='product_pics/' + product_pic)
        flash("Product is {}".format(prod_name))
        return redirect(url_for('ModifyProducts', product_name=prod_name, product_pic=product_pic_1, pic=product_pic))
    return render_template("admin_products.html", form=form, products=products, image=image_link, pic=product_pic)


@app.route('/admin_see_users', methods=['GET', 'POST'])
def admin_users():
    users_file = shelve.open("users")
    users = users_file['users']
    users_file.close()
    image_link = url_for('static', filename='profile_pics')
    form = remove_user()
    if request.method == "GET":
        # getting all products
        user_name = request.args.get('user_name', None)
        user_pic = request.args.get('user_pic', None)
    if request.method == "POST":
        # displaying all the products
        user_name = request.args.get('user_name', None)
        user_pic = request.args.get('product_pic', None)
        delete_user(user_name)
        flash("the user removed is {}".format(user_name))
        return redirect(url_for('admin_users', user_name=user_name))
    return render_template("admin_users.html", form=form, users=users, image=image_link, pic=user_pic)


# write a function to delete user from file user
def delete_user(name):
    try:
        user_file = shelve.open("users")
        users = user_file['users']
        for user in users:
            if name == user[0]:
                users.remove(user)
        user_file['users'] = users
        user_file.close()
    except:
        user_file.close()

# function which displays the modify products page


@app.route('/modify_products', methods=['GET', 'POST'])
def ModifyProducts():
    product_file = shelve.open("products")
    products = product_file['prods']
    product_file.close()
    prod_name = request.args.get('product_name', None)
    picture_file_1 = request.args.get('pic', None)
    form = updateProduct()
    if request.method == "GET":
        # get information of the product and display them in form
        for product in products:
            if prod_name == product[0]:
                form.description.data = product[2]
                form.price.data = product[1]
                form.quantity.data = int(product[3])
                form.sales_rate.data = product[5]
                pict = product[4]

    if request.method == "POST":
        if form.validate():
            # get new data from form
            new_price = request.form['price']
            sales_rate = request.form['sales_rate']
            new_quantity = request.form['quantity']
            # check new_quantity using validatequantiy method
            if not validate_quantity(new_quantity):
                flash('Invalid quantity ', category='danger')
                return redirect(url_for('ModifyProducts', product_name=prod_name, product_pic=picture_file_1, pic=picture_file_1))
            # enter new data into database
            description = request.form['description']
            picture_file = url_for(
                'static', filename='product_pics/' + picture_file_1)
            modify_product(picture_file_1, prod_name,
                           new_price, description, new_quantity, sales_rate)
            flash('Product modified successfully!', category='success')
            return redirect(url_for('admin_home'))

        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with Updating Product: {err_msg}', category='danger')
    return render_template("admin_modify_products.html", form=form, profile=picture_file_1, product_name=prod_name)

# function which modifies the product in database


def modify_product(product_pic, product_name, price, description, quantity, sales_rate):
    try:
        product_file = shelve.open("products")
        products = product_file['prods']
        i = 0
        for product in products:
            if product_name == product[0]:

                break
            i += 1
        products[i] = [product_name, price, description,
                       int(quantity), product_pic, sales_rate]
        product_file['prods'] = products
        product_file.close()
    except:
        products = []
        products.append([product_name, price, description,
                        quantity, product_pic, sales_rate])
        product_file['prods'] = products
        product_file.close()

# validator for quantity


def validate_quantity(quantity):
    if quantity.isdigit() and int(quantity) >= 0 and int(quantity) <= 30:
        return True
    return False

# function to save product picture


def save_product_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if not os.path.exists(os.path.join(app.root_path, 'static/product_pics')):
        os.makedirs(os.path.join(app.root_path, 'static/product_pics'))
    picture_path = os.path.join(
        app.root_path, 'static/product_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

# function to display add product page


@app.route('/addprod', methods=['GET', 'POST'])
def addprod():
    prod_pic = 'static\product_pics\defaultprod.jpg'
    form = addproduct()
    if request.method == "GET":
        return render_template("addprod.html", form=form)
    # if the form is submitted
    if request.method == "POST":
        if form.validate():
            # get data from form
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            quantity = request.form['quantity']
            sales = request.form['sales_rate']
            # check if product already exists
            if check_product(name):
                image_fn_1 = save_product_picture(form.image_file.data)
            # add product to database
                add_prod(name, price, description, int(
                    quantity), image_fn_1, sales)
                flash('Product added successfully!', category='success')
                return redirect(url_for('admin_home'))
            else:
                flash('Product already exists!', category='danger')
                return redirect(url_for('addprod'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with adding product: {err_msg}', category='danger')
        return render_template("addprod.html", form=form)

# function to check if product already exists


def check_product(product_name):
    product_file = shelve.open("products")
    products = product_file['prods']
    product_file.close()
    for product in products:
        if str(product_name).lower() == str(product[0]).lower():
            return False
    return True

# function which displays the admin order history page


@app.route('/adminorderhistory', methods=['GET', 'POST'])
def adminorderhistory():
    # open record file
    record_file = shelve.open("record")
    # get record from record file
    record = list(record_file['record'])
    record_file.close()

    for i in range(len(record)):
        for j in range(len(record[i])):
            # check if record[i][j] is not of type datetime
            if not isinstance(record[i][j], datetime):

                for k in record[i][j]:
                    # check if k is list
                    if isinstance(k, list):
                        for l in range(len(k)):
                            # check if k[l] is a string and is digit is not a date
                            if isinstance(k[l], str) and k[l].isdigit() and k[l] != "2020":
                                k[l] = int(k[l])

    # udate in record file
    record_file = shelve.open("record")
    record_file['record'] = record
    record_file.close()

    return render_template("adminorderhistory.html", record=record)

# function which displays the admin feedback page


@app.route('/viewfeedback', methods=['GET', 'POST'])
def viewfeedback():
    feedback_file = shelve.open("feedback")
    feedback = list(feedback_file['feedback'])
    feedback_file.close()
    return render_template("viewfeed.html", feedback=feedback)

# function which displays the admin faq page


@app.route('/viewfaq', methods=['GET', 'POST'])
def viewfaq():
    faq_file = shelve.open("faq")
    faq = list(faq_file['faq'])
    faq_file.close()
    return render_template("viewfaq.html", faq=faq)


# to run the app
if __name__ == '__main__':
    # empty cart
    cart_file = shelve.open("cart")
    cart_file['cart'] = []
    cart_file.close()

    app.run(debug=True)
