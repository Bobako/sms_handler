def create_admin(session, user_class):
    """Creates user(login:dev, password:tushpy) if not already exists"""
    if not session.query(user_class).first():
        session.add(user_class("dev", "tushpy"))
        session.commit()
