'''
This Flask application provides an endpoint to stream files from a given URL.
'''
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/get')
def get_file():
    url = request.args.get('url')
    if not url:
        return "Please provide a URL parameter.", 400

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk

        return Response(generate(), headers=response.headers)

    except requests.exceptions.RequestException as e:
        return f"Error fetching file: {e}", 500
 
if __name__ == '__main__':
    app.run(debug=True)
