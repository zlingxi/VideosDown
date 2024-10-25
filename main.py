import sys
import subprocess
import os
import requests  # 需要安装requests库
import json  # 用于解析yt-dlp输出的JSON数据
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox, QComboBox, QTextEdit, QInputDialog)
from PySide6.QtGui import QFont, QIcon  # 导入 QIcon
from PySide6.QtCore import QThread, Signal  # 导入多线程和信号

# 将当前目录的 src 子目录添加到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from help import show_help_message # 导入帮助模块
from about import show_about_message  # 导入关于模块
import license  # 导入license模块

LICENSE_FILE = 'config.json'  # 本地授权文件路径

def save_license(user_id, expiration_date):
    """保存用户授权信息到本地JSON文件"""
    license_data = {user_id: {"expiration_date": expiration_date}}
    with open(LICENSE_FILE, 'w') as f:
        json.dump(license_data, f, indent=4)

def load_license():
    """从本地文件加载用户授权信息"""
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    return None


class VideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("VideosDown v3.0 By@lingxi")
        self.setGeometry(800, 300, 600, 340)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 创建一个水平布局来放置两个按钮
        button_layout = QHBoxLayout()

        # 检测按钮
        self.check_button = QPushButton("网络检测")
        self.check_button.setFixedSize(80, 25)
        self.check_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.check_button.clicked.connect(self.check_google_access)
        button_layout.addWidget(self.check_button)

        # 帮助按钮
        self.help_button = QPushButton("帮助")
        self.help_button.setFixedSize(80, 25)
        self.help_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        # 关于按钮
        self.about_button = QPushButton("关于")
        self.about_button.setFixedSize(80, 25)
        self.about_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.about_button.clicked.connect(self.show_about)
        button_layout.addWidget(self.about_button)

        button_layout.addStretch(1)  # 添加弹性空间，确保按钮左对齐
        layout.addLayout(button_layout)  # 将按钮布局添加到主布局

        # 输入URL和检测分辨率按钮
        url_layout = QHBoxLayout()
        self.url_label = QLabel("视频链接:")
        self.url_input = QLineEdit()
        self.check_res_btn = QPushButton("检测可下载分辨率")
        self.check_res_btn.setFixedSize(130, 25)
        self.check_res_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.check_res_btn.clicked.connect(self.check_video_resolutions)

        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.check_res_btn)

        layout.addLayout(url_layout)

        # 选择分辨率的标签和下拉框
        res_layout = QHBoxLayout()
        self.resolution_label = QLabel("选择分辨率:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.setFixedWidth(80)

        res_layout.addWidget(self.resolution_label)
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch(1)

        layout.addLayout(res_layout)

        # 选择保存路径和下载按钮
        path_layout = QHBoxLayout()
        self.save_path_label = QLabel("保存路径:")
        self.save_path_input = QLineEdit()
        self.save_path_btn = QPushButton("浏览...")
        self.save_path_btn.setFixedSize(80, 25)
        self.save_path_btn.setStyleSheet("background-color: #FF9800; color: white;")
        self.save_path_btn.clicked.connect(self.select_save_path)

        self.download_btn = QPushButton("下载视频")
        self.download_btn.setFixedSize(100, 25)
        self.download_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.download_btn.clicked.connect(self.download_video)

        path_layout.addWidget(self.save_path_label)
        path_layout.addWidget(self.save_path_input)
        path_layout.addWidget(self.save_path_btn)
        path_layout.addWidget(self.download_btn)

        layout.addLayout(path_layout)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel("下载日志:"))
        layout.addWidget(self.log_text)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def show_help(self):
        """显示帮助与关于信息"""
        show_help_message(self)  # 调用 about.py 中的函数

    def show_about(self):
        """显示帮助与关于信息"""
        show_about_message(self)  # 调用 about.py 中的函数



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

    # 设置全局字体为微软雅黑与全局ico
    font = QFont("Microsoft YaHei", 8)
    app.setFont(font)  # 将字体设置为全局字体
    app.setWindowIcon(QIcon("img/app.ico"))

    # 尝试加载本地授权信息
    license_info = load_license()

    if license_info:
        user_id = next(iter(license_info))  # 获取第一个用户ID
        expiration_date = license_info[user_id]["expiration_date"]

        # 检查授权是否过期
        if license.check_user_license(user_id):
            # 如果授权有效，正常启动应用
            window = VideoDownloader()  # 创建主窗口
            window.show()  # 显示窗口
            sys.exit(app.exec())  # 进入主循环
        else:
            os.remove(LICENSE_FILE)  # 删除过期的授权文件

    # 创建一个输入对话框，让用户输入他们的用户 ID
    user_id, ok = QInputDialog.getText(None, "用户验证", "请输入您的用户ID：")

    if not ok or not user_id:
        QMessageBox.warning(None, "用户验证失败", "您必须输入一个有效的用户ID来启动程序。")
        sys.exit(0)

    # 检查该用户的授权信息
    if not license.check_user_license(user_id):
        # 如果授权验证失败，直接退出应用
        sys.exit(0)

    # 如果授权有效，保存用户授权信息到本地文件
    expiration_date = license.fetch_license_data().get(user_id, {}).get("expiration_date")
    if expiration_date:
        save_license(user_id, expiration_date)

    VideosDown = VideoDownloader()
    VideosDown.show()
    sys.exit(app.exec())
