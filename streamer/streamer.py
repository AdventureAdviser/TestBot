import cv2
import threading
import queue
from flask import Flask, render_template, Response, request

class Streamer:
    def __init__(self, frame_queue):
        self.frame_queue = frame_queue
        self.current_fps = 120
        self.current_scale = 1.0

    def set_fps(self, fps):
        self.current_fps = fps

    def set_scale(self, scale):
        self.current_scale = scale

    def get_frame(self):
        """ Получает кадр из очереди и изменяет его размер в соответствии с текущими настройками """
        frame = self.frame_queue.get()
        if frame is None:
            return None
        if self.current_scale != 1.0:
            width = int(frame.shape[1] * self.current_scale)
            height = int(frame.shape[0] * self.current_scale)
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()

def start_streamer(frame_queue):
    streamer = Streamer(frame_queue)

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

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
        streamer.set_fps(fps)
        return ('', 204)

    @app.route('/set_scale', methods=['POST'])
    def set_scale():
        scale = float(request.form['scale'])
        streamer.set_scale(scale)
        return ('', 204)

    app.run(host='0.0.0.0', port=5000)
