import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, RadioField, validators,  IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, EqualTo, Email, DataRequired,  Regexp
from wtforms.validators import Length, EqualTo, Email, DataRequired,  Regexp, NumberRange

# this contains all the forms used in the application

# user registration form


class RegisterForm(FlaskForm):
    # all the fields in the form
    # regex for password validation
    exp = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&+])[A-Za-z\d@$!%*#?&+]{4,}$"
    username = StringField(label='User Name:', validators=[
                           Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[
                                Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[
                              Regexp(re.compile(exp),
                                     message='Password must contain at least one letter, one number and one special character'),
                              Length(min=4,  message='Password must have a minimum length of 4'), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[
                              EqualTo('password1', message="please enter the same password as above"), DataRequired()])
    address = TextAreaField(
        'Address', [validators.optional(), validators.length(max=200)], render_kw={
            "placeholder": "Enter your address min length 5 max length 200"})

    postal_code = IntegerField("Postal Code",  render_kw={
        "placeholder": "Enter your 6 digit postal code"})
    submit = SubmitField(label='Create Account')


# user login form
class LoginForm(FlaskForm):
    username = StringField(label='Enter your username here',
                           validators=[DataRequired()])
    password = PasswordField(
        label='Enter Your Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class UpdateProfilePicForm(FlaskForm):
    image_file = FileField(label='Update Profile Picture', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], message="Only Jpeg and png allowed "), DataRequired(message='Image is required')])
    submit = SubmitField(label='Update Account')


# user modify profile form


class ProfileForm(FlaskForm):
    exp = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&+])[A-Za-z\d@$!%*#?&+]{4,}$"
    username = StringField(label='Username', validators=[
                           Length(min=2, max=30, message='username must have length between 2-30'), DataRequired(message='username is required')])
    email_address = StringField(label='Email', validators=[
                                Email(), DataRequired()])

    # password2 = PasswordField(label='New Password', validators=[
    #     Regexp(re.compile(exp),
    #            message='Password must contain at least one letter, one number and one special character'),
    #     Length(min=4,  message='Password must have a minimum length of 4'), DataRequired()]
    # )
    password = StringField(label='Old Password', validators=[
        Regexp(re.compile(exp),
               message='Password must contain at least one letter, one number and one special character'),
        Length(min=4,  message='Password must have a minimum length of 4'), DataRequired()])
    address = TextAreaField(
        'Address', [validators.optional(), validators.length(max=200)], render_kw={
            "placeholder": "Enter your address min length 5 max length 200"})

    postal_code = IntegerField("Postal Code",  render_kw={
        "placeholder": "Enter your 6 digit postal code"})
    submit = SubmitField(label='Update Account')


# admin registration form
class CreateAdminForm(FlaskForm):
    exp = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&+])[A-Za-z\d@$!%*#?&+]{4,}$"
    first_name = StringField('First Name', [Length(
        min=2, max=50, message=" for first Name Minimum length should be 2 and max length should be 50"), DataRequired()], render_kw={"placeholder": "Enter First Name"})
    last_name = StringField('Last Name', [Length(
        min=2, max=50, message=" For Last Name Minimum length should be 2 and max length should be 50"), DataRequired()], render_kw={"placeholder": "Enter Last Name"})
    phone_no = StringField('Phone Number', validators=[validators.Regexp(
        r"^\d{8}$", message="Invalid phone number format. Please use the format XXXXXXXX")], render_kw={"placeholder": "XXXXXXXX"})
    gender = RadioField('Gender', choices=[("M", "Male"), ("F", "Female")], render_kw={
                        "placeholder": "Enter Your Gender"}, validators=[DataRequired(message="Please select an option for gender:")])
    email_address = EmailField("Email Address", [validators.InputRequired(message="please enter  an email address")], render_kw={
                               "placeholder": "e.g. example@gmail.com"})
    password = PasswordField(label='Password:', validators=[
        Regexp(re.compile(exp),
               message='Password must contain at least one letter, one number and one special character'),
        Length(min=4,  message='Password must have a minimum length of 4'), DataRequired()])
    postal_code = IntegerField("Postal Code",  render_kw={
                               "placeholder": "Enter your 6 digit postal code"})
    # create submit field
    submit = SubmitField('Submit')


# admin login form
class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Enter an email"), Length(min=2, max=64, message="Minimum length should be 4 and max length should be 64")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Add product form


class addproduct(FlaskForm):
    name = StringField(label='Product Name:', validators=[
                       Length(min=2, max=30, message='Product name must have length between 2-30'), DataRequired(message='Product name is required')])
    price = StringField(label='Price:', validators=[
                        Length(min=2, max=30, message='Price must have length between 2-30'), DataRequired(message='Price is required')])
    description = StringField(label='Description:', validators=[
                              Length(min=2, max=30, message='Description must have length between 2-30'), DataRequired(message='Description is required')])
    # create integer field for quantity of products with range in 2-30
    quantity = IntegerField(label='Quantity:', validators=[validators.NumberRange(
        min=2, max=30, message='Quantity must have length between 2-30'), DataRequired(message='Quantity is required')])
    sales_rate = IntegerField(label='Sales Rate:', validators=[validators.NumberRange(
        min=1, max=100, message='Sales Rate must be  between 1-100'), DataRequired(message='Sales Rate is required')])

    image_file = FileField(label='Update Product Picture', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], message="Only Jpeg and png allowed "), DataRequired(message='Image is required')])

    submit = SubmitField(label='Add Product')


# Add product form
class addtocart(FlaskForm):
    quantity = IntegerField(label='Quantity:', validators=[validators.NumberRange(
        min=1, max=30, message='Quantity must have length between 2-30'), DataRequired(message='Quantity is required')])
    submit = SubmitField(label='Add to cart')

# Update from


class update(FlaskForm):
    submit = SubmitField(label='Update Product')

# Update Cart form


class updatecart(FlaskForm):
    quantity = IntegerField(label='Update Quantity:', validators=[validators.NumberRange(
        min=0, max=30, message='Quantity must have length between 2-30'), DataRequired(message='Quantity is required')])
    submit = SubmitField(label='Update cart')

# cnfrm order form


class cnfrmorder(FlaskForm):
    submit = SubmitField(label='Confirm Order')

# Update Product form


class updateProduct(FlaskForm):
    price = StringField(label='Price:', validators=[
                        Length(min=2, max=30, message='Price must have length between 2-30'), DataRequired(message='Price is required')])
    quantity = StringField(label='Update Quantity:', validators=[
                           DataRequired(message='Quantity is required')])
    sales_rate = IntegerField(label='Sales Rate:', validators=[validators.NumberRange(
        min=1, max=100, message='Sales Rate must be  between 1-100'), DataRequired(message='Sales Rate is required')])
    # image_file = FileField(label='Update Product Picture', validators=[FileAllowed(
    #     ['jpg', 'png', 'jpeg'], message="Only Jpeg and png allowed "), DataRequired(message='Image is required')])
    description = StringField(label='Description:', validators=[
                              Length(min=2, max=30, message='Description must have length between 2-30'), DataRequired(message='Description is required')])
    submit = SubmitField(label='Modify Product')

# feedback form


class feedbackform(FlaskForm):
    feedback = TextAreaField(
        'Feedback', [validators.optional(), validators.length(max=200)], render_kw={
            "placeholder": "Enter your feedback min length 5 max length 200"})
    experience = RadioField('Experience', choices=[("Highly Satisfied", "Highly Satisfied"), ("Satisfied", "Satisfied"), ("Satisfactory", "Satisfactory"), ("Dissatisfied", "Dissatisfied"), ("Highly Dissatisfied", "Highly Dissatisfied")], render_kw={
        "placeholder": "select your experience"})
    submit = SubmitField('Submit')

# faq form


class FaqForm(FlaskForm):
    question = TextAreaField(
        'Question', [validators.optional(), validators.length(max=200)], render_kw={
            "placeholder": "Enter your question min length 5 max length 200"})
    submit = SubmitField(label='Submit')


class remove_user(FlaskForm):
    submit = SubmitField(label='Remove User')
