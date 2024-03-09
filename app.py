from flask import Flask, render_template, request, jsonify, redirect
import logging
import jwt  # Regular jwt library
import requests
import os

from pprint import pprint

app = Flask(__name__)

# Constants
API_URL = os.environ.get('API_URL')  # Change this to your URL from cloud.hanko.io
AUDIENCE = os.environ.get('AUDIENCE')  # Change this to the domain you're hosting on, and make sure it matches the URL on cloud.hanko.io

# API_URL = "https://eb448bc5-6b9f-4bde-9494-9e755fcad1c5.hanko.io"
# AUDIENCE = "localhost"

# Retrieve the JWKS from the Hanko API
jwks_url = f"{API_URL}/.well-known/jwks.json"
jwks_response = requests.get(jwks_url)
jwks_data = jwks_response.json()
public_keys = {}
for jwk in jwks_data["keys"]:
    kid = jwk["kid"]
    public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)


def check_for_login(command="/profile"):
    # Retrieve the JWT from the cookie
    logging.info("Checking for jwt cookie...")
    jwt_cookie = request.cookies.get("hanko")
    # print(jwt_cookie)
    if not jwt_cookie:  # Check that the cookie exists
        logging.info("No jwt cookie found. Redirecting to /login...")
        # return redirect("/login")
        # return render_template('login.html', API_URL=API_URL, redirect=command)
        return False
    try:
        logging.info("jwt cookie found. Verifying...")
        kid = jwt.get_unverified_header(jwt_cookie)["kid"]
        payload = jwt.decode(
            str(jwt_cookie),
            public_keys[kid],
            algorithms=["RS256"],
            audience=AUDIENCE,
        )
        pprint(payload)
    except Exception as e:
        # The JWT is invalid
        logging.info("JWT is invalid. Redirecting to /login...")
        print(e)
        # return jsonify({"message": "unauthorised"})
        # return redirect("/login")
        return False
    # return jsonify({"message": "authorised"})
    logging.info("JWT is valid.")
    return True


@app.route("/login", methods=['GET'])
def login():
    redirect_url = request.args.get('redirect', default='/profile')
    # Render login page
    is_authenticated = check_for_login()
    if not is_authenticated:
        return render_template('login.html', API_URL=API_URL, redirect=redirect_url)
    else:
        print(redirect_url)
        return redirect(f"{redirect_url}")


@app.route("/profile", methods=['GET'])
def profile():
    # Render login page
    # return render_template('login.html', API_URL=API_URL)
    is_authenticated = check_for_login()
    if not is_authenticated:
        return render_template('login.html', API_URL=API_URL, redirect="/profile")
    else:
        return render_template('profile.html', API_URL=API_URL)


@app.route("/auth", methods=['POST'])
def auth():
    # Retrieve the JWT from the Authorization header
    logging.info("Checking for Authorization header...")
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logging.info("No Authorization header found. Redirecting to /login...")
        return jsonify({"message": "Not authorized"}), 401
    jwt_token = auth_header.split(' ', 1)[1].strip()
    try:
        logging.info("Authorization header found. Verifying...")
        kid = jwt.get_unverified_header(jwt_token)["kid"]
        payload = jwt.decode(
            str(jwt_token),
            public_keys[kid],
            algorithms=["RS256"],
            audience=AUDIENCE,
        )
        pprint(payload)
    except Exception as e:
        # The JWT is invalid
        logging.info("JWT is invalid. Redirecting to /login...")
        print(e)
        return jsonify({"message": "Not authorized"}), 401
    logging.info("JWT is valid.")
    return jsonify({"message": "Authorized"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    # 80 is the default port for http, so you won't need to specify the port in the browser
    # open http://localhost in a browser to see it in action
