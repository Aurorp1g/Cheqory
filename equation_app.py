import os
import json

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QHBoxLayout,QPushButton, QComboBox, QApplication, QGraphicsDropShadowEffect
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from common.base_app import BaseApp
from common.config import MATHJAX_PATH, render_mathjax

class ChemistryCategory:
    def __init__(self, name, equations, knowledge):
        self.name = name
        self.equations = equations
        self.knowledge = knowledge

class EquationStudyApp(BaseApp):
    def __init__(self):
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.6)
        height = int(screen.height() * 0.6)
        super().__init__("化学方程式背诵", width, height)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # 移除最大化按钮
        #self.setFixedSize(self.size())  # 固定窗口尺寸，禁止调整大小
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.categories = self.load_categories()
        self.current_category = None
        self.current_index = 0
        self.init_ui()
        self.on_category_changed(0)  # 初始化时触发分类选择

    def init_ui(self):
        # 分类选择框（优化样式）
        self.category_box = QComboBox()
        self.category_box.addItem("请选择分类")
        self.category_box.addItems([c.name for c in self.categories])
        self.category_box.currentIndexChanged.connect(self.on_category_changed)
        # 新增：QSS样式（兼容PyQt）
        self.category_box.setStyleSheet("""
            QComboBox {
                font-family: "微软雅黑";
                font-size: 20px;
                padding: 6px 15px;
                margin: 10px 0;
                border: 2px solid #e0e0e0;  /* 浅色边框 */
                border-radius: 8px;        /* 圆角 */
                background: white;         /* 白色背景 */
                color: #333;
            }
            QComboBox::drop-down {
                width: 30px;
                border-left: 1px solid #e0e0e0;  /* 下拉箭头分隔线 */
            }
            QComboBox QAbstractItemView::item {
                padding: 12px 15px;        /* 增大选项内边距 */
                font-size: 18px;
                background: white;         /* 选项背景 */
            }
            QComboBox QAbstractItemView::item:selected {
                background: #4CAF50;       /* 选中项绿色背景 */
                color: white;
            }
        """)
        self.category_box.setMinimumHeight(60)
        self.main_layout.addWidget(self.category_box)

        # 方程式显示区（新增样式）
        self.equation_view = QWebEngineView()
        self.equation_view.setMinimumHeight(350)
        self.equation_view.setVisible(False)
        # 新增：半透明背景+圆角边框
        self.equation_view.setStyleSheet("""
            QWebEngineView {
                background: rgba(255,255,255,0.95);
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
            }
        """)
        self.main_layout.addWidget(self.equation_view)

        # 知识点显示区（新增样式）
        self.knowledge_view = QWebEngineView()
        self.knowledge_view.setMinimumHeight(250)
        self.knowledge_view.setVisible(False)
        # 新增：与方程式区统一的样式
        self.knowledge_view.setStyleSheet("""
            QWebEngineView {
                background: rgba(255,255,255,0.95);
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
            }
        """)
        self.main_layout.addWidget(self.knowledge_view)

        # 导航按钮（优化样式+阴影）
        def add_button_effect(button):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)   # 阴影模糊半径
            shadow.setOffset(0, 3)    # 阴影偏移
            shadow.setColor(QColor(0,0,0,30))  # 浅灰色阴影
            button.setGraphicsEffect(shadow)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← 上一个")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                font-family: "微软雅黑";
                font-size: 22px;
                padding: 12px 25px;
                border-radius: 8px;
                background: #f0f0f0;     /* 浅灰背景 */
                color: #333;
                border: none;
            }
            QPushButton:hover {
                background: #e0e0e0;     /* 悬停加深 */
            }
            QPushButton:pressed {
                background: #d0d0d0;     /* 按下更深 */
            }
        """)
        add_button_effect(self.prev_btn)  # 添加阴影
        self.prev_btn.clicked.connect(self.prev_equation)

        self.next_btn = QPushButton("下一个 →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                font-family: "微软雅黑";
                font-size: 22px;
                padding: 12px 25px;
                border-radius: 8px;
                background: #4CAF50;      /* 绿色背景 */
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #45A049;      /* 悬停加深 */
            }
            QPushButton:pressed {
                background: #3D8B40;      /* 按下更深 */
            }
        """)
        add_button_effect(self.next_btn)  # 添加阴影
        self.next_btn.clicked.connect(self.next_equation)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.setSpacing(20)  # 按钮间距
        self.main_layout.addLayout(nav_layout)

        # 调整主布局边距（新增）
        self.main_layout.setContentsMargins(30, 30, 30, 30)  # 上下左右边距30px
        self.main_layout.setSpacing(25)  # 控件间间距25px

    def load_categories(self):
        """加载分类数据"""
        json_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "sql","equation_data.json"
        ))
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"未找到数据文件：{json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "categories" not in data:
            raise KeyError("数据文件缺少 'categories' 顶层字段")
        categories = []
        for idx, category_data in enumerate(data["categories"]):
            required_fields = ["name", "equations", "knowledge"]
            for field in required_fields:
                if field not in category_data:
                    raise KeyError(f"第 {idx+1} 个分类缺少必要字段：{field}")
            categories.append(ChemistryCategory(**category_data))
        return categories

    def on_category_changed(self, index):
        """分类选择变化处理"""
        if index == 0:
            self.current_category = None
            self.equation_view.setHtml("")
            self.knowledge_view.setHtml("")
            self.equation_view.setVisible(False)
            self.knowledge_view.setVisible(False)
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        self.current_category = self.categories[index - 1]
        self.current_index = 0
        self.update_equation()
        self.update_nav_buttons()
        self.equation_view.setVisible(True)
        self.knowledge_view.setVisible(True)

    def update_equation(self):
        """更新当前方程式显示"""
        if not self.current_category:
            return
        equation = self.current_category.equations[self.current_index]
        knowledge = self.current_category.knowledge
        base_url = QUrl.fromLocalFile(os.path.join(MATHJAX_PATH, "../"))
        
        # 方程式HTML
        gif_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "img", "wusaqi.gif"
        )).replace('\\', '/')
        eq_html = f"""
            <div class="equation" style="position: relative; height: 100%; font-size: 30px;">  <!-- 新增字体大小 -->
                {equation}  <!-- 原有方程式内容 -->
                <!-- 右下角图片保持不变 -->
                <img src="file:///{gif_path}" 
                     style="position: absolute; right: 10px; bottom: -230px;
                            width: auto; height: 200px; opacity: 0.8;">
            </div>
        """
        self.equation_view.setHtml(render_mathjax(eq_html), base_url)
        
        # 知识点HTML
        lay_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "img", "lay.png"
        )).replace('\\', '/')
        knowledge_html = f"""
            <div class="knowledge" style="position: relative; height: 100%; font-size: 25px;">  <!-- 新增字体大小 -->
                <h3>📚 相关知识点</h3>
                <p>{knowledge}</p>
                <!-- 右下角图片保持不变 -->
                <img src="file:///{lay_path}" 
                     style="position: absolute; right: 10px; bottom: -170px;
                            width: auto; height: 100px; opacity: 0.8;">
            </div>
        """
        self.knowledge_view.setHtml(render_mathjax(knowledge_html), base_url)

    def prev_equation(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_equation()
            self.update_nav_buttons()

    def next_equation(self):
        total = len(self.current_category.equations)
        if self.current_index < total - 1:
            self.current_index += 1
            self.update_equation()
            self.update_nav_buttons()

    def update_nav_buttons(self):
        total = len(self.current_category.equations)
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < total - 1)
        self.setWindowTitle(f"{self.current_category.name} - {self.current_index + 1}/{total}")