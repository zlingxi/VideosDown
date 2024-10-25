# src/about.py

from PySide6.QtWidgets import QMessageBox


def show_help_message(parent):
    """显示帮助对话框"""
    help_text = (

        "<b>【重要提示】</b><br>"
        "请务必在使用软件前开启代理网络。<br>"
        "打开软件后，请务必点击网络检测按钮，检测自己的网络代理、科学上网是否正常。<br>"
        "如果代理出现问题或切换节点，请重新启动软件并确保全局代理生效。<br>"
        "下载的视频仅供学习使用，禁止用于传播非法或不文明内容，所有下载及使用过程中产生的后果与本软件无关。<br><br>"
 
        "<b>【使用方法】</b><br>"
        " 1. 输入YouTube或者Vimeo的免费视频链接。<br>"
        " 2. 点击‘检测可下载分辨率’，获取可下载的视频分辨率。<br>"
        " 3. 点击下来按钮，选择自己想要的分辨率。<br>"
        " 4. 点击‘浏览按钮’选择自己想要保存的路径。<br>"
        " 5. 点击‘下载视频’按钮进行视频下载，日志框可以看到下载日志。<br>"
    )
    QMessageBox.information(parent, "帮助", help_text)

