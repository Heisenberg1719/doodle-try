from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Backend API URL
API_BASE_URL = 'https://bookish-pancake-v6grvx59jrrp3x649-8080.app.github.dev/'

# Utility function to extract a cookie value by its name
def get_cookie_value(cookies, cookie_name):
    for cookie in cookies:
        if cookie.name == cookie_name:
            return cookie.value
    return None

@app.route('/')
def home():
    # Show the login page
    return render_template('login.html', api_base_url=API_BASE_URL)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        phone_number = request.args.get('phone_number')

        # Perform a GET request to the API with the phone number as a query parameter
        response = requests.get(f"{API_BASE_URL}/user/login", params={'phone_number': phone_number})

        if response.status_code == 200:
            # Extract the username from the API response
            data = response.json()
            username = data.get('username')

            if username:
                # Render password input page with the username pre-filled
                return render_template('login_password.html', username=username)
            else:
                return "Username not found in the response.", 400
        else:
            return f"Login failed. Status code: {response.status_code}", 400

    elif request.method == 'POST':
        # Handle login using username and password
        username = request.form['username']
        password = request.form['password']

        # Create a session for requests
        session_requests = requests.Session()

        # Perform a POST request to the API to authenticate
        response = session_requests.post(f"{API_BASE_URL}/user/login", json={'username': username, 'password': password})

        if response.status_code == 200:
            # Get cookies and CSRF token from the response
            session['session_cookies'] = session_requests.cookies.get_dict()
            csrf_access_token = get_cookie_value(session_requests.cookies, 'csrf_access_token')

            if csrf_access_token:
                # Redirect to profile with CSRF token
                return redirect(url_for('profile', csrf_token=csrf_access_token))
            else:
                return "CSRF token not found in cookies.", 400
        else:
            return f"Login failed. Status code: {response.status_code}", 400

@app.route('/profile')
def profile():
    csrf_token = request.args.get('csrf_token')

    if 'session_cookies' in session:
        # Create a new session with cookies
        session_requests = requests.Session()
        session_requests.cookies.update(session['session_cookies'])

        # Set the CSRF token in the headers
        headers = {
            'X-CSRF-TOKEN': csrf_token
        }

        # Perform a GET request to the profile endpoint with the CSRF token in the headers
        profile_response = session_requests.get(f"{API_BASE_URL}/user/profile", headers=headers)

        if profile_response.status_code == 200:
            return profile_response.json()  # Return JSON response for the user profile
        else:
            return f"Failed to access the profile. Status code: {profile_response.status_code}", 400
    else:
        return "No session cookies found. Please login.", 400

if __name__ == '__main__':
    app.run(debug=True)
