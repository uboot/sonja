import os
import string


def build_credential_helper(credentials):
    credential_template_path = os.path.join(os.path.dirname(__file__), "credential_helper.sh.in")
    with open(credential_template_path) as credential_template_file:
        template = string.Template(credential_template_file.read())
    git_usernames = ['["{0}"]="{1}"'.format(c["url"], c["username"]) for c in credentials]
    git_passwords = ['["{0}"]="{1}"'.format(c["url"], c["password"]) for c in credentials]
    credential_helper = template.substitute({
        "git_usernames": " ".join(git_usernames),
        "git_passwords": " ".join(git_passwords)
    })
    return credential_helper
