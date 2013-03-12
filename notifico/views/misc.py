from notifico import app, user_required


@app.route('/')
@user_required
def misc_landing():
    return ''
