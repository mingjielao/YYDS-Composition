import json

secure_paths = [
    "/login/google",
    "/login/google/authorized",
    "/",
]


def check_security(request, google, blueprint):
    path = request.path
    result_ok = False

    if path not in secure_paths:
        google_data = None

        user_info_endpoint = "/oauth2/v2/userinfo"

        if google.authorized:
            google_data = google.get(user_info_endpoint).json()

            # print(json.dumps(google_data, indent=2))

            s = blueprint.session
            t = s.token

            # # If email in database
            # if google_data['email'] in database:
            #
            # else:
            #     result_ok = False
            # print("Token = \n", json.dumps(t, indent=2))
            result_ok = True
    else:
        result_ok = True

    return result_ok
