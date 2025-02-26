import sys

from PyQt5.QtWidgets import QApplication

from VideoPlayer import VideoPlayer


class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.player = VideoPlayer()

    def run(self):
        self.player.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    main = Main()
    main.run()
