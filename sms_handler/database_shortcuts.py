from sms_handler.cfg import config


def create_admin(session, user_class):
    """Creates default user if not already exists"""
    if not session.query(user_class).first():
        session.add(user_class(
            config["DATABASE"]["default_admin_login"],
            config["DATABASE"]["default_admin_password"],
        ))
        session.commit()
