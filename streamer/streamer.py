import cv2
from flask import Flask, render_template, Response, request, jsonify
import json

class Streamer:
    def __init__(self, frame_queue, configurator):
        self.frame_queue = frame_queue
        self.configurator = configurator

    def get_frame(self):
        """ Получает кадр из очереди и изменяет его размер в соответствии с текущими настройками """
        frame = self.frame_queue.get()
        if frame is None:
            return None
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()

def start_streamer(frame_queue, configurator):
    streamer = Streamer(frame_queue, configurator)

    app = Flask(__name__)

    @app.route('/')
    def index():
        fps = configurator.get_fps()
        scale = configurator.get_scale()
        return render_template('index.html', fps=fps, scale=scale)

    @app.route('/video_feed')
    def video_feed():
        def generate():
            while True:
                frame = streamer.get_frame()
                if frame is None:
                    break
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/set_fps', methods=['POST'])
    def set_fps():
        fps = int(request.form['fps'])
        configurator.set_fps(fps)
        return ('', 204)

    @app.route('/set_scale', methods=['POST'])
    def set_scale():
        scale = float(request.form['scale'])
        configurator.set_scale(scale)
        return ('', 204)

    app.run(host='0.0.0.0', port=5000)
