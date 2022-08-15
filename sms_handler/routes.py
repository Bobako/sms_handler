import datetime

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user

from sms_handler import app, db, manager, sms_api
from sms_handler.models import User, Message, Sub
from sms_handler.forms_handler import parse_forms, update_objs


@manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login_page") + f"?next={request.url}")


@app.route("/login", methods=['post', 'get'])
def login_page():
    if current_user:
        logout_user()
    if request.method == "POST":    # validation disabled in demo
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index_page')
        return redirect(next_page)

    return render_template("login.html")


@app.route("/", methods=['post', 'get'])
def index_page():
    return render_template("sms_journal.html")


@app.route("/users", methods=["post", "get"])
def users_page():
    if request.method == "POST":
        form = parse_forms(request.form)
        update_objs(db.session, form, User, not_nullable="login", primary_key_name="login")
    users = db.session.query(User).all()
    return render_template("users.html", users=users, current_user=current_user)


@app.route("/subs", methods=["post", "get"])
def subs_page():
    if request.method == "POST":
        form = parse_forms(request.form)
        update_objs(db.session, form, Sub)
    return render_template("subs.html")


"""# --------------- api --------------------#"""


@app.route("/api/search/message", methods=["get"])
def api_message_live_search():
    date = request.args.get("date")
    phone = request.args.get("phone")
    text = request.args.get("text")
    prim_status = request.args.get("prim_status")
    sec_status = request.args.get("sec_status")
    text_not_null = request.args.get("text_not_null")

    query = db.session.query(Message)
    if text_not_null == "true":
        query = query.filter(Message.text != "")
    if text:
        query = query.filter(Message.text.ilike(f"%{text}%"))
    if phone:
        query = query.filter(Message.phone.ilike(f"%{phone}%"))
    if prim_status:
        prim_status = bool(int(prim_status))
        query = query.filter(Message.primary_service_status == prim_status)
    if sec_status:
        sec_status = bool(int(sec_status))
        query = query.filter(Message.secondary_service_status == sec_status)
    if date:
        start = datetime.datetime.strptime(date, "%Y-%m-%d")
        end = start + datetime.timedelta(days=1)
        query = query.filter(Message.datetime >= start).filter(Message.datetime <= end)
    query = query.order_by(Message.datetime.desc())
    query = query.limit(200)
    messages = query.all()
    return render_template("messages_table_body.html", messages=messages)


@app.route("/api/search/sub", methods=["get"])
def api_sub_live_search():
    date = request.args.get("date")
    phone = request.args.get("phone")
    name = request.args.get("name")
    name_not_null = request.args.get("name_not_null")
    query = db.session.query(Sub)
    if name_not_null == "true":
        query = query.filter(Sub.name != "")
    if phone:
        query = query.filter(Sub.phone.ilike(f"%{phone}%"))
    if name:
        query = query.filter(Sub.name.ilike(f"%{name}%"))
    if date:
        start = datetime.datetime.strptime(date, "%Y-%m-%d")
        end = start + datetime.timedelta(days=1)
        query = query.filter(Sub.last_message_datetime >= start).filter(Sub.last_message_datetime <= end)
    query = query.order_by(Sub.last_message_datetime.desc())
    query = query.limit(200)
    subs = query.all()
    return render_template("subs_table_body.html", subs=subs)


sms_api_worker = sms_api.SMSAPI.from_config(db.session)


@app.route("/api/resend", methods=["get"])
def api_resend_message():
    message_id = request.args.get("mid")
    message = db.session.query(Message).filter(Message.id == message_id).one()
    is_sent, status = sms_api_worker.send_sms(message.text, message.phone)
    if is_sent:
        sub = db.session.query(Sub).filter(Sub.phone == message.phone).one()
        sub.last_message_datetime = datetime.datetime.now()
        message.secondary_service_status = True
        message.secondary_service_status_text = status
        db.session.commit()
    return ['Не удалось отправить', 'Отправлено успешно'][is_sent] + (f": {status}" if not is_sent else '')
