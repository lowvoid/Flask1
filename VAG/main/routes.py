from flask import Blueprint
import os, secrets
from werkzeug.utils import secure_filename
from flask import render_template, url_for, request, send_from_directory ,flash , redirect
from flask import current_app
from VAG import db , mail
from flask_mail import Message
from VAG.models import Feature, Service ,Contact
from flask_ckeditor import upload_success, upload_fail
from VAG.helpers import safe_extension
from VAG.main.forms import ContactForm

main = Blueprint('main',__name__)

@main.route('/files/<path:filename>')
def uploaded_files(filename):
    path = os.path.join(current_app.root_path, 'static/media')
    return send_from_directory(path, filename)

@main.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    if not f or not f.filename:
        return upload_fail(message='No file selected')

    filename = secure_filename(f.filename)
    ext = safe_extension(filename)
    if not ext:
        return upload_fail(message='File extension not allowed!')

    random_hex = secrets.token_hex(8)
    image_name = f"{random_hex}{ext}"
    save_path = os.path.join(current_app.root_path, 'static/media', image_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    f.save(save_path)

    url = url_for('main.uploaded_files', filename=image_name)
    return upload_success(url, filename=image_name)


@main.route("/")
@main.route("/home")
def home():
    services = Service.query.order_by(Service.name.asc()).paginate(page=1,per_page=6)
    features = Feature.query.order_by(Feature.date_posted.desc()).paginate(page=1,per_page=6)
    return render_template('home.html', services=services, features=features)

@main.route("/about")
def about():
    return render_template('about.html', title="About")

@main.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()

        msg = Message("New Contact Message", recipients=["realvirtualcode@gmail.com"])  
        msg.body = f"""
        New message from {form.name.data} <{form.email.data}>:
        {form.message.data}
        """
        msg.reply_to = form.email.data
        mail.send(msg)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)