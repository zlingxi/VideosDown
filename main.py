import sys
import subprocess
import os
import requests  # 需要安装requests库
import json  # 用于解析yt-dlp输出的JSON数据
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox, QComboBox, QTextEdit)
from PySide6.QtGui import QFont  # 导入 QFont
from PySide6.QtCore import QThread, Signal  # 导入多线程和信号

class VideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("VideosDown v3.0 By@lingxi")
        self.setGeometry(800, 300, 400, 320)  # 调整窗口高度以容纳新元素

        # 设置全局字体为微软雅黑
        font = QFont("Microsoft YaHei", 8)
        QApplication.setFont(font)

        central_widget = QWidget()
        layout = QVBoxLayout()

        # 检测按钮
        self.check_button = QPushButton("检测科学上网")
        self.check_button.clicked.connect(self.check_google_access)
        layout.addWidget(self.check_button)


        # 输入URL
        self.url_label = QLabel("视频链接:")
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # 检测分辨率按钮
        self.check_res_btn = QPushButton("检测可下载分辨率")
        self.check_res_btn.clicked.connect(self.check_video_resolutions)
        layout.addWidget(self.check_res_btn)

        # 可用分辨率下拉框
        self.resolution_combo = QComboBox()
        layout.addWidget(QLabel("选择分辨率:"))
        layout.addWidget(self.resolution_combo)

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


        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("下载日志:"))
        layout.addWidget(self.log_text)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def select_save_path(self):
        """选择保存路径"""
        save_path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if save_path:
            self.save_path_input.setText(save_path)

    def check_video_resolutions(self):
        """检测可下载分辨率"""
        url = self.url_input.text().strip()
        ytdlp_path = os.path.join("resource", "yt-dlp.exe")

        if not url:
            QMessageBox.warning(self, "错误", "请输入视频链接！")
            return

        command = [
            ytdlp_path,
            "--dump-json",
            url
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                formats = video_info.get("formats", [])

                self.resolution_combo.clear()  # 清空下拉框
                resolutions = set()
                for fmt in formats:
                    resolution = fmt.get("height")
                    if resolution:
                        resolutions.add(resolution)

                if resolutions:
                    sorted_resolutions = sorted(resolutions, reverse=True)  # 从高到低排序
                    formatted_resolutions = [f"{res}p" for res in sorted_resolutions]
                    self.resolution_combo.addItems(formatted_resolutions)
                else:
                    QMessageBox.warning(self, "没有可用分辨率", "未找到可用的视频分辨率！")
            else:
                QMessageBox.critical(self, "错误", f"获取分辨率失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取分辨率出错: {str(e)}")

    def download_video(self):
        """下载视频"""
        url = self.url_input.text().strip()
        save_path = self.save_path_input.text().strip()
        selected_resolution = self.resolution_combo.currentText()

        if not url or not save_path:
            QMessageBox.warning(self, "错误", "请输入视频链接并选择保存路径！")
            return

        if not selected_resolution:
            QMessageBox.warning(self, "错误", "请选择一个分辨率进行下载！")
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
            "-f", f"bestvideo[height<={selected_resolution[:-1]}]+bestaudio",
            "--merge-output-format", "mp4",
            "-o", output_template
        ]

        # 创建并启动下载线程
        self.log_text.clear()  # 清空日志
        self.download_thread = DownloadThread(command)
        self.download_thread.progress_signal.connect(self.update_log)
        self.download_thread.finished_signal.connect(self.download_finished)  # 连接下载完成信号
        self.download_thread.start()

    def update_log(self, log):
        """更新日志文本框"""
        self.log_text.append(log)

    def download_finished(self):
        """下载完成后提示成功"""
        QMessageBox.information(self, "完成", "视频下载完成！")

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

class DownloadThread(QThread):
    progress_signal = Signal(str)
    finished_signal = Signal()  # 添加下载完成信号

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        """运行下载命令并处理输出"""
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.progress_signal.emit(output.strip())

        # 获取错误输出
        stderr_output = process.stderr.read()
        if stderr_output:
            self.progress_signal.emit(stderr_output.strip())

        self.finished_signal.emit()  # 下载完成后发出信号

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = VideoDownloader()
    downloader.show()
    sys.exit(app.exec())
