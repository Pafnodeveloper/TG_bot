
from pytube import Search
import logging
from logging.handlers import TimedRotatingFileHandler
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(message)s")

file_handler = TimedRotatingFileHandler("youtube_log", when="midnight", interval=1)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y%m%d"

logger.addHandler(file_handler)


def initialize(func):
    def inner(*args, **kwargs):
        g = func(*args, **kwargs)
        g.send(None)
        return g
    return inner


@initialize
def get_audio():
    song_name = yield
    logger.info(f"Ищу {song_name}")
    s = Search(song_name)
    if os.path.exists("songs")==False:
        os.makedirs("songs", 0o700)
    results = s.results
    try:
        for result in results:
            video = result.streams.filter(only_audio=True).first()
            out_file = video.download(output_path='./songs')

            base, ext = os.path.splitext(out_file)
            new_file = base + ".mp3"
            os.rename(out_file, new_file)
            logger.info(f"Нашел {new_file}")
            yield new_file
    except GeneratorExit as err:
        logger.info(f"Закрываем генератор")
        return

