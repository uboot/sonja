from flask_login import current_user, login_required

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""

@login_required
def check_ApiKey(api_key, required_scopes):
    user = current_user
    if user and user.id:
        return {'sub': user.id}

    return None


