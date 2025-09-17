from flask import Blueprint

from flask import render_template, redirect, url_for, flash, request
from VAG import bcrypt, db 
from VAG.users.forms import RegistrationForm, LoginForm, UpdateProfileForm , RequestResetForm ,ResetPasswordForm
from VAG.models import User, Feature
from flask_login import login_user, current_user, logout_user, login_required
from VAG.helpers import save_picture, delete_picture
from VAG.users.helpers import send_reset_email

users =  Blueprint('users',__name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            fname=form.fname.data,
            lname=form.lname.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for("users.login"))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        flash('Login unsuccessful. Check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/dashboard")
@login_required
def dashboard():
    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template('dashboard.html', title="Dashboard", image_file=image_file, active_tab="none")

@users.route("/dashboard/profile", methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UpdateProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.picture.data:
            picture_file = save_picture(profile_form.picture.data, 'static/user_pics', size=(150,150))
            delete_picture(current_user.image_file, 'static/user_pics')
            current_user.image_file = picture_file
        current_user.fname = profile_form.fname.data
        current_user.lname = profile_form.lname.data
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('users.profile'))
    elif request.method == "GET":
        profile_form.fname.data = current_user.fname
        profile_form.lname.data = current_user.lname
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        profile_form.bio.data = current_user.bio
    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template('profile.html', title="Profile", profile_form=profile_form, image_file=image_file, active_tab="profile")


@users.route('/author/<string:username>', methods=['GET'])
def author(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    features = (Feature.query.filter_by(author=user).order_by(Feature.date_posted.desc()).paginate(page=page, per_page=6))
    return render_template('author.html',features=features,user=user)


@users.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('If this account exists, you will receive an email with instructions', 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title="Reset Password", form=form) 


@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('The token is inavlid or expired', 'warning')
        return redirect(url_for('users.reset_requset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated. You can now log in", 'success')
        return redirect(url_for("users.login"))
    return render_template("reset_password.html", title="Reset Password", form=form) 

