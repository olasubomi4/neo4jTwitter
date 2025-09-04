import logging


class LoggingProxy:
    def __init__(self):
        self.logging = logging
        self.logger = logging.getLogger("Neo4jTwitter")
        self.logging.basicConfig(level=logging.DEBUG,   format="%(asctime)s - %(name)s - %(levelname)s- %(funcName)s - %(message)s")


