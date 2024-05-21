import cv2
import threading
import queue
from flask import Flask, render_template, Response, request
from configurator.configurator import Configurator

class Streamer:
    def __init__(self, frame_queue, configurator, config_queue):
        self.frame_queue = frame_queue
        self.configurator = configurator
        self.config_queue = config_queue

    def get_frame(self):
        """ Получает кадр из очереди и изменяет его размер в соответствии с текущими настройками """
        while not self.config_queue.empty():
            config_item = self.config_queue.get()
            if config_item[0] == 'fps':
                self.configurator.set_fps(config_item[1])
            elif config_item[0] == 'scale':
                self.configurator.set_scale(config_item[1])
            elif config_item[0] == 'enable_visualization':
                global ENABLE_VISUALIZATION
                ENABLE_VISUALIZATION = config_item[1]
            # Очистить очередь кадров, чтобы применить новые настройки
            with self.frame_queue.mutex:
                self.frame_queue.queue.clear()

        frame = self.frame_queue.get()
        if frame is None:
            return None
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()

def start_streamer(frame_queue, configurator, config_queue):
    streamer = Streamer(frame_queue, configurator, config_queue)

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
        streamer.config_queue.put(('fps', fps))
        return ('', 204)

    @app.route('/set_scale', methods=['POST'])
    def set_scale():
        scale = float(request.form['scale'])
        configurator.set_scale(scale)
        streamer.config_queue.put(('scale', scale))
        return ('', 204)

    app.run(host='0.0.0.0', port=5000)

