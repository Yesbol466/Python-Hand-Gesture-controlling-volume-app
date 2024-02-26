from flask import Flask
from flask import Response
from flask import render_template
from controle_volume import generate_frames


app: Flask = Flask(__name__)


@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/video_feed')
def video_feed() -> Response:
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
