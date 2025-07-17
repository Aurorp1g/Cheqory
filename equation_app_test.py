import sys
import os
import json
import random

# 配置Qt插件路径
os.environ['QT_QPA_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(os.__file__),
    'site-packages',
    'PyQt5',
    'Qt',
    'plugins'
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

# MathJax配置
MATHJAX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "mathjax"))
if not os.path.exists(MATHJAX_PATH):
    raise Exception(f"MathJax路径错误: {MATHJAX_PATH}")

class ChemistryCategory:
    def __init__(self, name, equations, knowledge):
        self.name = name
        # 新增：校验方程式列表非空
        if not isinstance(equations, list) or len(equations) == 0:
            raise ValueError(f"分类 {name} 的方程式列表无效")
        self.equations = equations
        self.knowledge = knowledge  # 知识点允许空字符串，但需为字符串类型

class EquationStudyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("化学方程式背诵系统")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化数据
        try:
            self.categories = self.load_categories()
        except Exception as e:
            QMessageBox.critical(self, "数据加载失败", f"数据加载错误：{str(e)}")
            sys.exit(1)
            
        # 创建界面组件（此时 category_box 尚未触发信号）
        self.init_ui()
        
        # 关键调整：手动触发一次分类加载（确保初始化时按钮状态正确）
        self.on_category_changed(0)

    def init_ui(self):
        # 主控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 分类选择（添加初始未选择状态）
        self.category_box = QComboBox()
        # 新增：添加"请选择分类"作为第一个选项
        self.category_box.addItem("请选择分类")
        # 添加实际分类名称（原逻辑）
        self.category_box.addItems([c.name for c in self.categories])
        self.category_box.currentIndexChanged.connect(self.on_category_changed)
        self.category_box.setStyleSheet("font-size: 20px; padding: 6px;")
        self.category_box.setMinimumHeight(60)
        main_layout.addWidget(self.category_box)
        
        # 方程式显示区（初始隐藏内容）
        self.equation_view = QWebEngineView()
        self.equation_view.setMinimumHeight(350)
        self.equation_view.setVisible(False)  # 初始隐藏
        main_layout.addWidget(self.equation_view)
        
        # 知识点显示区（初始隐藏内容）
        self.knowledge_view = QWebEngineView()
        self.knowledge_view.setMinimumHeight(250)
        self.knowledge_view.setVisible(False)  # 初始隐藏
        main_layout.addWidget(self.knowledge_view)
        
        # 导航按钮（初始禁用）
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一个 (←)")
        self.prev_btn.setStyleSheet("font-size: 18px; padding: 8px;")
        self.prev_btn.clicked.connect(self.prev_equation)
        self.prev_btn.setEnabled(False)  # 初始禁用
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("下一个 (→)")
        self.next_btn.setStyleSheet("font-size: 18px; padding: 8px;")
        self.next_btn.clicked.connect(self.next_equation)
        self.next_btn.setEnabled(False)  # 初始禁用
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)

    def on_category_changed(self, index):
        """切换分类时的处理（新增未选择状态判断）"""
        # 当选择第一个选项（"请选择分类"）时
        if index == 0:
            self.current_category = None
            self.current_index = 0
            # 清空并隐藏显示区
            self.equation_view.setHtml("")
            self.knowledge_view.setHtml("")
            self.equation_view.setVisible(False)
            self.knowledge_view.setVisible(False)
            # 禁用导航按钮
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.setWindowTitle("化学方程式背诵系统")  # 重置窗口标题
            return
        
        # 选择实际分类时（index ≥ 1）
        self.current_category = self.categories[index - 1]  # 因为第一个选项是"请选择分类"，实际分类从index=1开始
        self.current_index = 0
        self.update_equation()
        self.update_nav_buttons()
        # 显示内容区
        self.equation_view.setVisible(True)
        self.knowledge_view.setVisible(True)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("化学方程式背诵系统")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化数据
        try:
            self.categories = self.load_categories()
        except Exception as e:
            QMessageBox.critical(self, "数据加载失败", f"数据加载错误：{str(e)}")
            sys.exit(1)
            
        # 创建界面组件（此时 category_box 尚未触发信号）
        self.init_ui()
        
        # 关键调整：手动触发一次分类加载（确保初始化时按钮状态正确）
        self.on_category_changed(0)

    def load_categories(self):
        """加载分类数据（增强校验）"""
        json_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "resources",
            "sql",
            "equation_data.json"
        ))
        
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"未找到数据文件：{json_path}")
            
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"数据文件格式错误：{str(e)}")
        
        # 新增：校验顶层是否有 "categories" 字段
        if "categories" not in data:
            raise KeyError("数据文件缺少 'categories' 顶层字段")
        
        categories = []
        for idx, category_data in enumerate(data["categories"]):
            # 校验每个分类的必要字段
            required_fields = ["name", "equations", "knowledge"]
            for field in required_fields:
                if field not in category_data:
                    raise KeyError(f"第 {idx+1} 个分类缺少必要字段：{field}")
            # 转换为 ChemistryCategory 对象
            categories.append(ChemistryCategory(**category_data))
        
        # 注意：返回的categories列表顺序与QComboBox中实际分类的顺序一致（index=1对应第一个实际分类）
        return categories

    def render_mathjax(self, content):
        """生成包含MathJax渲染的HTML内容（修复版本兼容性问题）"""
        # 确保路径包含完整的MathJax目录结构
        mathjax_url = f"file:///{MATHJAX_PATH}/es5/tex-chtml.js".replace('\\', '/')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script type="text/javascript" src="{mathjax_url}?config=TeX-AMS-MML_HTMLorMML"></script>
            <script>
                // MathJax 3.x 配置方式（替代原2.x的Hub.Config）
                MathJax = {{
                    tex: {{
                        inlineMath: [['$','$'], ['\\\\(','\\\\)']],  // 注意转义反斜杠
                        processEscapes: true
                    }},
                    options: {{
                        showMathMenu: false,
                        messageStyle: "none"
                    }},
                    startup: {{
                        ready: () => {{
                            MathJax.startup.defaultReady();  // 保持默认初始化
                            MathJax.typeset();  // 手动触发公式渲染
                        }}
                    }}
                }};
            </script>
            <style>
                body {{
                    font-size: 30px;
                    line-height: 1.7;
                    color: #333;
                    margin: 15px;
                }}
                .content {{
                    padding: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {content}
            </div>
            <script>window.onerror = function(msg) {{ console.error(msg); }}</script>
        </body>
        </html>
        """
    def update_equation(self):
        """更新当前方程式显示（新增右下角img）"""
        if not self.current_category:
            return
            
        equation = self.current_category.equations[self.current_index]
        knowledge = self.current_category.knowledge
        
        # 构建MathJax基URL（保持原有逻辑）
        base_url = QUrl.fromLocalFile(os.path.join(MATHJAX_PATH, "../"))
        
        # 构建img路径（假设img文件存放在resources/img目录下）
        gif_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "resources",
            "img",
            "wusaqi.gif"  # 替换为实际img文件名
        )).replace('\\', '/')  # 处理Windows路径分隔符
        
        # 方程式显示区HTML（新增右下角img）
        eq_html = f"""
            <div class="equation" style="position: relative; height: 100%;">
                {equation}  <!-- 原有方程式内容 -->
                <!-- 新增：右下角img -->
                <img src="file:///{gif_path}" 
                     style="position: absolute; right: 10px; bottom: -230px;
                            width: auto; height: 200px; opacity: 0.8;">
            </div>
        """
        self.equation_view.setHtml(self.render_mathjax(eq_html), base_url)
        
        # 知识点显示区HTML
        know_html = f"""
            <div class="knowledge" style="position: relative; height: 100%;">
                <h3>📚 相关知识点</h3>
                <p>{knowledge}</p>
            </div>
        """
        self.knowledge_view.setHtml(self.render_mathjax(know_html), base_url)

    def next_equation(self):
        """下一个方程式（修复索引边界判断）"""
        if not self.current_category:
            return
        # 原条件：self.current_index < len(...) - 1 → 改为 < len(...)
        # 允许索引从 0 递增到 len(equations)-1（总共有 N 个方程式时，索引范围 0~N-1）
        if self.current_index < len(self.current_category.equations) - 1:
            self.current_index += 1
            self.update_equation()
            self.update_nav_buttons()  # 确保按钮状态同步更新

    def prev_equation(self):
        """上一个方程式（修复索引边界判断）"""
        if not self.current_category:
            return
        # 原条件：self.current_index > 0 → 允许索引递减到 0（第一个方程式）
        if self.current_index > 0:
            self.current_index -= 1
            self.update_equation()
            self.update_nav_buttons()  # 确保按钮状态同步更新

    def update_nav_buttons(self):
        """更新导航按钮状态（明确边界提示）"""
        total = len(self.current_category.equations)
        # 上一个按钮：仅当索引 > 0 时启用
        self.prev_btn.setEnabled(self.current_index > 0)
        # 下一个按钮：仅当索引 < 总数-1 时启用（最后一个方程式时禁用）
        self.next_btn.setEnabled(self.current_index < total - 1)
        # 窗口标题显示当前进度（如：硫及其化合物 - 2/2）
        self.setWindowTitle(f"{self.current_category.name} - {self.current_index + 1}/{total}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 检查MathJax路径
    if not os.path.exists(MATHJAX_PATH):
        QMessageBox.critical(
            None,
            "MathJax缺失",
            f"MathJax未找到，请放置在：\n{MATHJAX_PATH}"
        )
        sys.exit(1)
        
    window = EquationStudyApp()
    window.show()
    sys.exit(app.exec_())
