# license.py
import requests
from PySide6.QtWidgets import QMessageBox
from datetime import datetime

# 获取远程 JSON 数据的函数
def fetch_license_data():
    try:
        # 服务器上的json文件
        url = "https://www.ssproxy.one/licenses/licenses_VideoDown_win.json"
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except Exception as e:
        print(f"获取授权数据失败：{e}")
        return None

# 检查用户的授权时间
def check_user_license(user_id):
    # 获取远程的授权数据
    license_data = fetch_license_data()

    if not license_data:
        # 如果获取数据失败，提示用户并退出
        QMessageBox.critical(None, "授权验证失败", "无法获取授权数据，请检查网络连接或联系开发者。")
        return False

    # 获取当前用户的授权信息
    user_license = license_data.get(user_id)

    if not user_license:
        # 如果用户 ID 不在授权列表中，提示用户并退出
        QMessageBox.critical(None, "授权失败", "未找到该用户的授权信息。")
        return False

    # 解析授权到期日期
    expiration_date_str = user_license.get("expiration_date")
    expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")

    # 获取当前日期
    current_date = datetime.now()

    # 检查授权是否过期
    if current_date > expiration_date:
        QMessageBox.critical(None, "授权已过期", "您的授权已过期，请联系开发者获取新的授权。")
        return False  # 已过期
    return True  # 未过期
