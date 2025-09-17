from flask import Blueprint

from flask import render_template, redirect, url_for, flash, request ,abort ,jsonify
from VAG import db , bcrypt
from VAG.features.forms import FeaturesForm ,FeatureUpdateForm , DeleteForm
from VAG.services.forms import ServiceForm , JoinByCodeForm
from VAG.models import Feature, Service
from flask_login import current_user, login_required
from VAG.features.helpers import slugify , get_previous_next_lesson
from VAG.helpers import save_picture, delete_picture
import secrets




features_bp = Blueprint('features',__name__)

@features_bp.route("/generate_invite_code", methods=["GET"])
@login_required
def generate_invite_code():
    code = secrets.token_urlsafe(6)
    return jsonify({"invite_code": code})

@features_bp.route("/dashboard/feature", methods=['GET', 'POST'])
@login_required
def feature():
    feature_form = FeaturesForm()
    service_form = ServiceForm()
    code_form = JoinByCodeForm()

    if feature_form.submit.data and feature_form.validate_on_submit():
        clean_slug = slugify(feature_form.slug.data or feature_form.title.data)
        if Feature.query.filter_by(slug=clean_slug).first():
            flash("Slug already exists. Please choose a unique slug.", "danger")
            return redirect(url_for('features.feature'))

        thumbnail_file = "default_thumbnail.jpg"
        if feature_form.thumbnail.data:
            thumbnail_file = save_picture(feature_form.thumbnail.data, folder="static/feature_thumbnail")

        new_feature = Feature(
            title=feature_form.title.data,
            slug=clean_slug,
            content=feature_form.content.data,
            thumbnail=thumbnail_file,
            author=current_user,
            service=feature_form.service.data
        )
        db.session.add(new_feature)
        db.session.commit()
        flash("Your feature has been created!", "success")
        return redirect(url_for("main.home"))

    if service_form.submit.data and service_form.validate_on_submit():
        icon_file = "default_icon.jpg"
        if service_form.icon.data:
            icon_file = save_picture(service_form.icon.data, folder="static/service_icon")

        is_private = (service_form.is_private.data == "1")

        hashed_pw = None
        if is_private and service_form.join_password.data:
            hashed_pw = bcrypt.generate_password_hash(service_form.join_password.data).decode("utf-8")

        invite_code = service_form.invite_code.data.strip() if service_form.invite_code.data else None
        if is_private and not invite_code:
            invite_code = secrets.token_urlsafe(6)

        existing_service = Service.query.filter_by(name=service_form.name.data).first()
        if existing_service:
            flash("Service name already exists. Please choose another one.")
            return redirect(url_for("features.feature"))
        else:
            new_service = Service(
                name=service_form.name.data,
                description=service_form.description.data,
                icon=icon_file,
                user_id=current_user.id,
                is_private=is_private,
                join_password=hashed_pw,
                invite_code=invite_code,
        )
        db.session.add(new_service)
        db.session.commit()

        flash(f'Service "{new_service.name}" created successfully!', "success")
        if invite_code:
            flash(f"Invite Code: {invite_code}", "info")

        return redirect(url_for("users.dashboard"))

    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template(
        "feature.html",
        title="Feature",
        feature_form=feature_form,
        service_form=service_form,
        code_form=code_form,
        active_tab="feature",
        image_file=image_file
    )


@features_bp.route("/<string:service>/<string:lesson_slug>")
def lesson(service, lesson_slug):
    lesson_obj = Feature.query.filter_by(slug=lesson_slug).first_or_404()
    service = lesson_obj.service

    previous_lesson, next_lesson = get_previous_next_lesson(lesson_obj)

    if service.is_private:
        if not current_user.is_authenticated or (current_user != service.author and current_user not in service.members):
            flash("You are not authorized to view this feature.", "danger")
            return redirect(url_for("services.service", service_title=service.name))

    return render_template(
        "feature_view.html",
        title=lesson_obj.title,
        lesson=lesson_obj,
        previous_lesson=previous_lesson,
        next_lesson=next_lesson,
        service=service
    )

@features_bp.route("/dashboard/user_content", methods=['GET','POST'])
@login_required
def user_content():
    delete_form = DeleteForm()
    image_file = url_for('static', filename=f'user_pics/{current_user.image_file}')
    return render_template(
        "user_content.html",
        title='Your Content',
        image_file=image_file,
        active_tab='user_content',
        delete_form=delete_form
    )

@features_bp.route("/<string:service>/<string:lesson_slug>/update", methods=['GET','POST'])
@login_required
def update_feature(service, lesson_slug):
    lesson = Feature.query.filter_by(slug=lesson_slug).first_or_404()
    if lesson.author != current_user:
        abort(403)

    previous_lesson, next_lesson = get_previous_next_lesson(lesson)
    form = FeatureUpdateForm()

    if form.validate_on_submit():
        new_slug = slugify(form.slug.data or form.title.data)
        if new_slug != lesson.slug and Feature.query.filter_by(slug=new_slug).first():
            flash("Slug already exists. Please choose a unique slug.", "danger")
            return redirect(url_for('features.update_feature', service=service, lesson_slug=lesson.slug))

        if form.thumbnail.data:
            delete_picture(lesson.thumbnail, r'static/feature_thumbnail')
            lesson.thumbnail = save_picture(form.thumbnail.data, 'static/feature_thumbnail')

        lesson.service = form.service.data
        lesson.title = form.title.data
        lesson.slug = new_slug
        lesson.content = form.content.data

        db.session.commit()
        flash("Updated!", "success")
        return redirect(url_for('features.user_content'))

    elif request.method == 'GET':
        form.service.data = lesson.service
        form.title.data = lesson.title
        form.slug.data = lesson.slug
        form.content.data = lesson.content

    return render_template(
        "update_feature.html",
        title='update | ' + lesson.title,
        lesson=lesson,
        previous_lesson=previous_lesson,
        next_lesson=next_lesson,
        service=service,
        form=form
    )

@features_bp.route('/feature/<int:feature_id>/delete', methods=['POST'])
@login_required
def delete_feature(feature_id):
    feat = Feature.query.get_or_404(feature_id)
    if feat.author != current_user:
        abort(403)
    delete_picture(feat.thumbnail, 'static/feature_thumbnail')
    db.session.delete(feat)
    db.session.commit()
    flash('Deleted!', 'success')
    return redirect(url_for('features.user_content', feature_id=feature_id))

