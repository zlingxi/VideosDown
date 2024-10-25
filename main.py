import sys
import subprocess
import os
import requests  # 需要安装requests库
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox)
from PySide6.QtGui import QFont  # 导入 QFont

class VideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("YouTube/Vimeo视频下载器")
        self.setGeometry(800, 300, 400, 200)

        # 设置全局字体为微软雅黑
        font = QFont("Microsoft YaHei", 8)
        QApplication.setFont(font)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # 输入URL
        self.url_label = QLabel("视频链接:")
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # 选择保存路径
        self.save_path_label = QLabel("保存路径:")
        self.save_path_input = QLineEdit()
        self.save_path_btn = QPushButton("浏览...")
        self.save_path_btn.clicked.connect(self.select_save_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.save_path_input)
        path_layout.addWidget(self.save_path_btn)

        layout.addWidget(self.save_path_label)
        layout.addLayout(path_layout)

        # 下载按钮
        self.download_btn = QPushButton("下载视频")
        self.download_btn.clicked.connect(self.download_video)
        layout.addWidget(self.download_btn)

        # 检测按钮
        self.check_button = QPushButton("检测科学上网")
        self.check_button.clicked.connect(self.check_google_access)
        layout.addWidget(self.check_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def select_save_path(self):
        """选择保存路径"""
        save_path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if save_path:
            self.save_path_input.setText(save_path)

    def download_video(self):
        """下载视频"""
        url = self.url_input.text().strip()
        save_path = self.save_path_input.text().strip()

        if not url or not save_path:
            QMessageBox.warning(self, "错误", "请输入视频链接并选择保存路径！")
            return

        # 检查yt-dlp.exe和ffmpeg.exe是否存在
        ytdlp_path = os.path.join("resource", "yt-dlp.exe")
        ffmpeg_path = os.path.join("resource", "ffmpeg.exe")

        if not os.path.exists(ytdlp_path) or not os.path.exists(ffmpeg_path):
            QMessageBox.critical(self, "错误", "yt-dlp.exe或ffmpeg.exe未找到，请确保它们位于resource文件夹中！")
            return

        # yt-dlp下载命令
        output_template = os.path.join(save_path, "%(title)s.%(ext)s")
        command = [
            ytdlp_path,
            url,
            "--ffmpeg-location", ffmpeg_path,
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", output_template
        ]

        # 执行下载
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                QMessageBox.information(self, "完成", "视频下载完成！")
            else:
                QMessageBox.critical(self, "错误", f"下载失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"下载出错: {str(e)}")

    def check_google_access(self):
        """检测是否可以访问Google"""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                QMessageBox.information(self, "成功", "系统提示：您可以科学上网！")
            else:
                QMessageBox.warning(self, "失败", "系统提示：您无法科学上网，请检查您的网络、魔法、代理等！，状态码: {}".format(response.status_code))
        except requests.ConnectionError:
            QMessageBox.critical(self, "错误", "系统提示：您无法科学上网，请检查您的网络、魔法、代理等！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"系统提示：发生错误: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = VideoDownloader()
    downloader.show()
    sys.exit(app.exec())
