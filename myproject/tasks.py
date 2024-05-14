from __future__ import absolute_import, unicode_literals
from celery import shared_task
import ffmpeg
import os
from pytube import YouTube
from tempfile import NamedTemporaryFile

@shared_task
def process_video_task(video_url):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    except Exception as e:
        return f"Failed to process video URL: {str(e)}"

    with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        stream.download(output_path=os.path.dirname(temp_video.name), filename=os.path.basename(temp_video.name))
        temp_video_path = temp_video.name

    output_path = temp_video_path.replace('.mp4', '_vertical.mp4')
    try:
        (
            ffmpeg
            .input(temp_video_path)
            .filter('scale', 'iw*9/16', 'ih')
            .filter('pad', 'iw', 'ih', '(ow-iw)/2', '(oh-ih)/2')
            .output(output_path)
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        os.remove(temp_video_path)
        return f"FFmpeg error: {e.stderr.decode('utf-8') if e.stderr else str(e)}"

    os.remove(temp_video_path)
    return output_path
