import sys
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon ,QColor, QPalette, QBrush, QImage
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QInputDialog 
from common.base_app import BaseApp
from quiz_app import ChemistryQuizApp
from equation_app import EquationStudyApp

class MainControlPanel(BaseApp):
    def __init__(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.6)
        height = int(screen.height() * 0.6)
        super().__init__("开始学习化学啦！！！", width, height)
        # 禁用最大化按钮并固定窗口大小（防止全屏）
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # 移除最大化按钮
        #self.setFixedSize(self.size())  # 固定窗口尺寸，禁止调整大小
        # 原有代码保持不变
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.ico")
        self.setWindowIcon(QIcon(icon_path))
        self._init_ui()

    def _init_ui(self):
        bg_dir = os.path.join(os.path.dirname(__file__), "resources")
        bg_filename = "background.png"
        bg_path = os.path.join(bg_dir, bg_filename)
        
        if not os.path.isfile(bg_path):
            QMessageBox.warning(self, "错误", f"未找到背景图片文件：{bg_path}")
            return

        # 存储背景路径并初始化
        self.bg_path = bg_path
        self.update_background()

        # 主界面按钮样式（QSS兼容版）
        btn_style = """
            QPushButton {
                font-family: "微软雅黑";
                font-size: 24px;
                padding: 20px 50px;
                margin: 25px 0;
                border-radius: 12px;
                background-color: rgba(76, 175, 80, 0.9);  /* 纯色背景（半透明） */
                color: white;
                border: 2px solid rgba(255,255,255,0.3);  /* 浅色边框 */
            }
            QPushButton:hover {
                background-color: rgba(69, 160, 73, 0.95);  /* 悬停加深背景色 */
                border-color: rgba(255,255,255,0.5);  /* 边框变亮 */
            }
            QPushButton:pressed {
                background-color: rgba(60, 140, 63, 1.0);  /* 按下更深背景色 */
                border-color: rgba(255,255,255,0.7);  /* 边框更亮 */
            }
        """

        # 创建功能按钮（新增阴影效果）
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        def add_button_shadow(button):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)  # 阴影模糊半径
            shadow.setOffset(0, 5)    # 阴影偏移（x=0, y=5）
            shadow.setColor(QColor(76, 175, 80, 80))  # 绿色半透明阴影
            button.setGraphicsEffect(shadow)

        quiz_btn = QPushButton("开始选择题练习")
        quiz_btn.setStyleSheet(btn_style)
        quiz_btn.clicked.connect(self.start_quiz)
        add_button_shadow(quiz_btn)  # 添加阴影

        equation_btn = QPushButton("开始方程式背诵")
        equation_btn.setStyleSheet(btn_style)
        equation_btn.clicked.connect(self.start_equation_study)
        add_button_shadow(equation_btn)  # 添加阴影

        # 添加到主布局（原有代码保持不变）
        self.main_layout.addStretch()
        self.main_layout.addWidget(quiz_btn, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(equation_btn, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def start_quiz(self):
        # 先获取题库总题数
        try:
            # 加载所有题目（
            all_questions = ChemistryQuizApp.load_all_questions()
            total_questions = len(all_questions)
            if total_questions == 0:
                QMessageBox.warning(self, "提示", "当前题库无题目，请先添加题目！")
                return
        except FileNotFoundError as e:
            QMessageBox.warning(self, "错误", str(e))
            return

        # 弹出输入题数的弹窗
        question_count, ok = QInputDialog.getInt(
            self, 
            "设置题数", 
            f"当前题库共有 {total_questions} 题，请输入练习题数（1-{total_questions}）：",
            value=min(10, total_questions),  # 默认值取10和总题数的较小值
            min=1, 
            max=total_questions  # 最大值限制为总题数
        )
        if ok:
            self.quiz_window = ChemistryQuizApp(question_count)
            self.quiz_window.show()

    def start_equation_study(self):
        self.equation_window = EquationStudyApp()
        self.equation_window.show()

    # 新增窗口大小变化事件处理
    def resizeEvent(self, event):
        """处理窗口缩放事件"""
        super().resizeEvent(event)
        self.update_background()

    def update_background(self):
        """更新背景图片缩放"""
        palette = QPalette()
        bg_image = QImage(self.bg_path).scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation  # 添加平滑缩放
        )
        palette.setBrush(QPalette.Background, QBrush(bg_image))
        self.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_panel = MainControlPanel()
    main_panel.show()
    sys.exit(app.exec_())
