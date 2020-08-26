

import threading

import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.views.generic import TemplateView

print(cv2.getBuildInformation())


class VideoCapture(object):
    def __init__(self):
        self.video = cv2.VideoCapture("videotestsrc ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


video = VideoCapture()


def gen(camera):
    while True:
        frame = video.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def livefe(request):
    try:
        return StreamingHttpResponse(gen(VideoCapture()), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print(e)


class LiveFeedTemplateView(TemplateView):
    template_name = "stream/stream.html"
