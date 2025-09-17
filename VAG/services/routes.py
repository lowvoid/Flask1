from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from VAG import db, bcrypt
from VAG.models import Service, Feature
from VAG.services.forms import ServiceUpdateForm, DeleteForm, JoinForm, JoinByCodeForm ,GenerateInviteForm ,InviteCodeForm ,LeaveForm,PublicJoinForm
from VAG.helpers import save_picture, delete_picture
import secrets

services_bp = Blueprint("services", __name__)

@services_bp.route("/<string:service_title>")
def service(service_title):
    service_obj = Service.query.filter_by(name=service_title).first_or_404()
    join_form = JoinForm()
    page = request.args.get('page', 1, type=int)
    invitecode = GenerateInviteForm()
    leave_form = LeaveForm()
    public_join_form = PublicJoinForm()

    features = None
    if not service_obj.is_private or (current_user.is_authenticated and (current_user == service_obj.author or current_user in service_obj.members)):
        features = Feature.query.filter_by(service_id=service_obj.id).paginate(page=page, per_page=6)

    code_form = JoinByCodeForm()
    return render_template(
        "service.html",
        title=service_obj.name,
        service=service_obj,
        features=features,
        form=join_form,
        code_form=code_form,
        invitecode=invitecode,
        leave_form=leave_form,
        public_join_form=public_join_form
    )

@services_bp.route("/services")
def services_page():
    page = request.args.get('page', 1, type=int)
    services = Service.query.paginate(page=page, per_page=6)
    join_forms = {s.id: JoinForm(prefix=str(s.id)) for s in services.items}
    code_form = JoinByCodeForm()
    public_join_form = PublicJoinForm()
    return render_template(
        "services.html",
        title="Services",
        services=services,
        join_forms=join_forms,
        code_form=code_form,
        public_join_form=public_join_form

    )

@services_bp.route("/dashboard/user_services")
@login_required
def user_services():
    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    services = Service.query.filter_by(user_id=current_user.id).all()
    delete_form = DeleteForm()
    return render_template(
        "user_services.html",
        title="Your Services",
        image_file=image_file,
        services=services,
        delete_form=delete_form
    )

@services_bp.route("/service/<int:service_id>/update", methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.author != current_user:
        abort(403)

    form = ServiceUpdateForm(obj=service)

    if request.method == "POST" and "generate_code" in request.form:
        import secrets
        new_code = secrets.token_urlsafe(6)
        form.invite_code.data = new_code
        flash("New invite code generated! Save changes to apply.", "info")
        return render_template("update_service.html",
                               title=f"Update | {service.name}",
                               service_form=form,
                               service=service)

    if form.validate_on_submit():
        if form.icon.data and hasattr(form.icon.data, "filename") and form.icon.data.filename != "":
            delete_picture(service.icon, "static/service_icon")
            service.icon = save_picture(form.icon.data, "static/service_icon")

        service.name = form.name.data
        service.description = form.description.data
        service.is_private = True if form.is_private.data in [True, "1", 1] else False
        service.join_password = form.join_password.data
        service.invite_code = form.invite_code.data
        db.session.commit()

        flash("Service updated successfully!", "success")
        return redirect(url_for("services.user_services"))

    return render_template("update_service.html",
                           title=f"Update | {service.name}",
                           service_form=form,
                           service=service)

@services_bp.route("/service/<int:service_id>/delete", methods=['POST'])
@login_required
def delete_service(service_id):
    form = DeleteForm()
    if form.validate_on_submit():
        service = Service.query.get_or_404(service_id)
        if service.author != current_user:
            abort(403)
        delete_picture(service.icon, "static/service_icon")
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
    return redirect(url_for("services.user_services"))

@services_bp.route("/join/<int:service_id>", methods=["POST"])
@login_required
def join_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = JoinForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(service.join_password, form.password.data):
            if current_user not in service.members:
                service.members.append(current_user)
                db.session.commit()
                flash("You have joined the service!", "success")
            else:
                flash("You are already a member of this service.", "info")
        else:
            flash("Wrong password. Try again.", "danger")
    else:
        flash("Invalid form submission.", "danger")
    return redirect(url_for("services.service", service_title=service.name))

@services_bp.route("/join_with_code/<int:service_id>", methods=["POST"])
@login_required
def join_with_code(service_id):
    service = Service.query.get_or_404(service_id)
    code = request.form.get("invite_code")
    if not code:
        flash("Please enter an invite code!", "danger")
        return redirect(url_for("services.service", service_title=service.name))

    if service.invite_code != code:
        flash("Invalid invite code!", "danger")
        return redirect(url_for("services.service", service_title=service.name))

    if current_user not in service.members:
        service.members.append(current_user)
        db.session.commit()
        flash(f"You joined {service.name} successfully!", "success")
    else:
        flash("You already joined this service.", "info")

    return redirect(url_for("services.service", service_title=service.name))

@services_bp.route("/<int:service_id>/set_invite", methods=["GET", "POST"])
@login_required
def set_invite_code(service_id):
    cd = InviteCodeForm()
    service = Service.query.get_or_404(service_id)
    if service.author != current_user:
        abort(403)
    if request.method == "POST":
        new_code = request.form.get("invite_code")
        if not new_code:
            flash("Invite code cannot be empty!", "danger")
        else:
            service.invite_code = new_code
            db.session.commit()
            flash("Invite code updated successfully!", "success")
            return redirect(url_for("services.service", service_title=service.name))
    return render_template("set_invite.html", service=service ,cd=cd)

@services_bp.route("/my_services")
@login_required
def my_services():
    services = Service.query.filter_by(author=current_user).all()
    return render_template("my_services.html", services=services)

@services_bp.route("/generate_invite/<int:service_id>", methods=['POST'])
@login_required
def generate_invite_code(service_id):
    service = Service.query.get_or_404(service_id)
    invitecode = GenerateInviteForm()
    if service.author != current_user:
        flash("You are not authorized to generate an invite code.", "danger")
        return redirect(url_for('services.service', service_title=service.name))


    if invitecode.validate_on_submit():
        service.invite_code = secrets.token_urlsafe(6)
        db.session.commit()
        flash("Invite code generated!", "success" )
    if invitecode:
            flash(f"Invite Code: {service.invite_code}", "info")


    return redirect(url_for('services.service', service_title=service.name))



@services_bp.route("/join_code", methods=["GET", "POST"])
@login_required
def join_code():
    form = JoinByCodeForm()

    if form.validate_on_submit():
        code = form.invite_code.data.strip()
        service = Service.query.filter_by(invite_code=code).first()

        if not service:
            flash("Invalid invite code!", "danger")
            return redirect(url_for("services.join_code"))

        if current_user not in service.members:
            service.members.append(current_user)
            db.session.commit()
            flash(f"You joined {service.name} successfully!", "success")
        else:
            flash("You already joined this service.", "info")

        return redirect(url_for("services.service", service_title=service.name))

    return render_template("join_with_code.html", form=form)


@services_bp.route("/<string:service_title>/quit", methods=["POST"])
@login_required
def quit_service(service_title):
    form = LeaveForm()
    service = Service.query.filter_by(name=service_title).first_or_404()

    if form.validate_on_submit():
        if service.user_id == current_user.id:
            flash(" You cannot quit your own service.", "warning")
            return redirect(url_for("services.service", service_title=service_title))

        if current_user in service.members:
            service.members.remove(current_user)
            db.session.commit()
            flash(f" You have left {service.name}.", "info")
        else:
            flash(" You are not a member of this service.", "danger")

    return redirect(url_for("services.service", service_title=service.name))


@services_bp.route("/join_public/<string:service_title>", methods=["POST"])
@login_required
def join_public_service(service_title):
    service = Service.query.filter_by(name=service_title).first_or_404()

    if service.is_private:
        flash(" This is a private service. Use password or invite code.", "danger")
        return redirect(url_for("services.service", service_title=service.name))

    if service.user_id == current_user.id:
        flash(" You cannot join your own service.", "warning")
        return redirect(url_for("services.service", service_title=service.name))

    if current_user in service.members:
        flash(" You are already a member of this service.", "info")
        return redirect(url_for("services.service", service_title=service.name))

    service.members.append(current_user)
    db.session.commit()
    flash(f" You joined {service.name} successfully!", "success")
    return redirect(url_for("services.service", service_title=service.name))
