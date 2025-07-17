from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

class BaseApp(QMainWindow):
    """基础应用窗口类（所有子应用的公共基类）"""
    def __init__(self, title, width=1400, height=800):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, width, height)
        
        # 初始化中心控件和基础布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
