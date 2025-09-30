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
 
@app.route('/put', methods=['GET', 'PUT'])
def put_file():
    if request.method == 'PUT':
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
            redirect_url = url_for('put_file', url=unique_filename, _external=True, _scheme='https')
            return redirect(redirect_url)

        except requests.exceptions.RequestException as e:
            return f"Error processing file: {e}", 500
    
    elif request.method == 'GET':
        filename = request.args.get('url') # Here 'url' is actually the filename
        if not filename:
            return "Please provide a filename parameter.", 400
        
        file_path = os.path.join('temp_files', filename)
        
        if not os.path.exists(file_path):
            return "File not found.", 404
        
        try:
            def generate_file():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            
            # Determine content type from filename extension
            mimetype = "application/octet-stream"
            if '.' in filename:
                extension = filename.rsplit('.', 1)[1].lower()
                if extension == 'jpg' or extension == 'jpeg':
                    mimetype = 'image/jpeg'
                elif extension == 'png':
                    mimetype = 'image/png'
                elif extension == 'gif':
                    mimetype = 'image/gif'
                elif extension == 'pdf':
                    mimetype = 'application/pdf'
                elif extension == 'mp4':
                    mimetype = 'video/mp4'
                elif extension == 'webm':
                    mimetype = 'video/webm'
                elif extension == 'ogg':
                    mimetype = 'video/ogg'
                elif extension == 'mp3':
                    mimetype = 'audio/mpeg'
                elif extension == 'wav':
                    mimetype = 'audio/wav'
                # Add more mimetypes as needed
            
            return Response(generate_file(), mimetype=mimetype)
            
        except Exception as e:
            return f"Error serving file: {e}", 500
    
if __name__ == '__main__':
    app.run(debug=True)
