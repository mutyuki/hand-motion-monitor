from receiver.events import EventProcessor
from receiver.server import serve


def main():
    serve(EventProcessor())
