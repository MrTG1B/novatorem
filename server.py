import os
from flask import Flask, request, redirect, jsonify
import requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_in_prod')

# Load Spotify credentials from environment
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')  # e.g. https://your-tunnel.io/callback

print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret: {CLIENT_SECRET}")
print(f"Redirect URI: {REDIRECT_URI}")


SCOPE = 'user-read-currently-playing user-read-playback-state'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return f"Error during authorization: {error}", 400

    code = request.args.get('code')
    if not code:
        return 'No code provided', 400

    # Exchange code for tokens
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(TOKEN_URL, data=payload, headers=headers)
    if resp.status_code != 200:
        return f"Failed to get token: {resp.text}", resp.status_code

    data = resp.json()
    # You can store refresh_token securely here or return it
    refresh_token = data.get('refresh_token')
    access_token = data.get('access_token')

    # For demonstration, return tokens as JSON
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': data.get('expires_in')
    })

if __name__ == '__main__':
    # Make sure FLASK_RUN_HOST and FLASK_RUN_PORT align with your tunnel
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8888)), debug=True)
     
