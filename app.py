'''
This Flask application provides an endpoint to stream files from a given URL.
'''
from flask import Flask, request, Response, redirect, url_for
import requests
import os
from urllib.parse import urlparse
import uuid

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
 
@app.route('/put', methods=['PUT'])
def put_file():
    url = request.args.get('url')
    if not url:
        return "Please provide a URL parameter.", 400

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an exception for HTTP errors

        # Extract extension from the URL
        parsed_url = urlparse(url)
        filename, extension = os.path.splitext(os.path.basename(parsed_url.path))
        if not extension:
            content_type = response.headers.get('Content-Type')
            if content_type and '/' in content_type:
                extension = '.' + content_type.split('/')[-1]
            else:
                extension = ""

        unique_filename = f"{uuid.uuid4()}{extension}"
        
        # Ensure the 'temp_files' directory exists
        os.makedirs('temp_files', exist_ok=True)
        file_path = os.path.join('temp_files', unique_filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Redirect to a URL with the new filename
        redirect_url = url_for('put_file', url=unique_filename, _external=True)
        return redirect(redirect_url)

    except requests.exceptions.RequestException as e:
        return f"Error processing file: {e}", 500
    
if __name__ == '__main__':
    app.run(debug=True)
