import sys
import os
import json

# 新增Qt插件路径配置
os.environ['QT_QPA_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(os.__file__), 
    'site-packages', 
    'PyQt5', 
    'Qt', 
    'plugins'
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QMessageBox, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

# 本地MathJax配置（确保在程序目录中有mathjax文件夹）
MATHJAX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "mathjax"))
if not os.path.exists(MATHJAX_PATH):
    raise Exception(f"MathJax路径错误: {MATHJAX_PATH}")

class ChemistryQuestion:
    def __init__(self, question, options, correct_index, explanation):
        self.question = question
        self.options = options
        self.correct_index = correct_index
        self.explanation = explanation

class ChemistryQuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("化学方程式选择题练习")
        self.setGeometry(100, 100, 1400, 800)
        
        # 初始化题目数据（修改为从文件加载）
        try:
            self.questions = self.load_questions()
        except Exception as e:
            QMessageBox.critical(self, "数据加载失败", f"题目数据加载错误：{str(e)}")
            sys.exit(1)
        self.current_question_index = 0
        self.score = 0
        # 新增：记录已作答的题目索引（无论对错）
        self.answered_questions = set()
        # 新增：记录用户对每道题的选择结果（索引）
        self.user_answers = {}
        
        # 创建主控件和布局（保持原逻辑）
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建分数和进度显示（再次增大字体）
        self.score_label = QLabel(f"分数: {self.score}/{len(self.questions)}")
        # 原18px → 20px
        self.score_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.score_label)
        
        # 进度条（保持原逻辑）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        # 创建题目显示区域（增大最小高度）
        self.question_view = QWebEngineView()
        # 原120 → 150
        self.question_view.setMinimumHeight(150)
        self.layout.addWidget(self.question_view)
        
        # 创建选项区域（再次增大选项高度）
        self.options_group = QButtonGroup()
        self.options_layout = QVBoxLayout()
        self.option_widgets = []
        
        for i in range(4):
            # 移除单独添加option_widget到布局的操作（原问题根源）
            option_widget = QWebEngineView()
            option_widget.setMinimumHeight(100)
            self.option_widgets.append(option_widget)
            
            radio = QRadioButton()
            self.options_group.addButton(radio, i)
            # 保持水平布局，但仅添加一次组合布局
            radio_layout = QHBoxLayout()
            radio_layout.addWidget(radio)  # 单选框
            radio_layout.addWidget(option_widget)  # 选项内容
            radio_layout.setStretch(1, 1)  # 让选项内容占据剩余空间
            self.options_layout.addLayout(radio_layout)  # 只添加组合后的水平布局
        
        self.layout.addLayout(self.options_layout)
        
        # 创建按钮区域（增大按钮字体）
        self.button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("上一题")
        self.prev_button.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px 16px;")  # 添加font-weight
        self.prev_button.clicked.connect(self.prev_question)
        self.button_layout.addWidget(self.prev_button)
        
        self.submit_button = QPushButton("提交答案")
        self.submit_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 25px; font-weight: bold; padding: 8px 16px;")  # 添加font-weight
        self.submit_button.clicked.connect(self.check_answer)
        self.button_layout.addWidget(self.submit_button)
        
        self.next_button = QPushButton("下一题")
        self.next_button.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px 16px;")  # 添加font-weight
        self.next_button.clicked.connect(self.next_question)
        self.button_layout.addWidget(self.next_button)
        
        self.layout.addLayout(self.button_layout)
        
        # 创建解释区域（再次增大显示高度）
        self.explanation_view = QWebEngineView()
        # 原120 → 150
        self.explanation_view.setMinimumHeight(150)
        self.explanation_view.setVisible(False)
        self.layout.addWidget(self.explanation_view)
        
        # 加载第一题（保持原逻辑）
        self.load_question(self.current_question_index)
    
    def load_questions(self):
        """从JSON文件加载题目数据"""
        # 构建JSON文件路径（项目根目录/sources/questions.json）
        json_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),  # 当前脚本所在目录
            "resources",
            "sql", 
            "questions.json"
        ))
        
        # 检查文件是否存在
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"未找到题目数据文件：{json_path}\n请在该路径创建resources/sql/questions.json文件")

        
        # 读取并解析JSON
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data_list = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON文件格式错误：{str(e)}")
        
        # 转换为ChemistryQuestion对象列表
        questions = []
        for data in data_list:
            questions.append(
                ChemistryQuestion(
                    question=data["question"],
                    options=data["options"],
                    correct_index=data["correct_index"],
                    explanation=data["explanation"]
                )
            )
        return questions

    def render_mathjax(self, content):
        """生成包含MathJax渲染的HTML内容（修复版本兼容性问题）"""
        # 确保路径包含完整的MathJax目录结构
        mathjax_url = f"file:///{MATHJAX_PATH}/es5/tex-chtml-full.js".replace('\\', '/')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script type="text/javascript" src="{mathjax_url}?config=TeX-AMS-MML_HTMLorMML"></script>
            <script>
                // MathJax 3.x 配置方式
                MathJax = {{
                    tex: {{
                        inlineMath: [['$','$'], ['\\\\(','\\\\)']],  // 注意转义反斜杠
                        processEscapes: true,
                        packages: {{'[+]': ['mhchem']}} // 加载 mhchem 扩展
                    }},
                    loader: {{
                        load: ['[tex]/mhchem'] // 显式加载扩展
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
                    font-size: 20px;
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

    def check_answer(self):
        """检查答案"""
        selected_index = self.options_group.checkedId()
        if selected_index == -1:
            QMessageBox.warning(self, "提示", "请选择一个答案！")
            return
        
        question = self.questions[self.current_question_index]
        is_correct = (selected_index == question.correct_index)
        
        # 仅首次答对时加分（关键修改）
        if is_correct and self.current_question_index not in self.answered_questions:
            self.score += 1
            self.score_label.setText(f"分数: {self.score}/{len(self.questions)}")
        
        # 记录已作答状态和用户选择（关键修改）
        self.answered_questions.add(self.current_question_index)
        self.user_answers[self.current_question_index] = selected_index
        
        # 显示解释
        result = "正确！" if is_correct else "错误！"
        color = "green" if is_correct else "red"
        explanation_html = f"""
            <p style="font-weight: bold; color: {color};">{result}</p>
            {question.explanation}
        """
        self.explanation_view.setHtml(self.render_mathjax(explanation_html), QUrl("file:///"))
        self.explanation_view.setVisible(True)
        
        # 如果是最后一题，检查是否完成
        if self.current_question_index == len(self.questions) - 1:
            self.show_final_score()
    
    def show_final_score(self):
        """显示最终分数"""
        score_percent = (self.score / len(self.questions)) * 100
        message = f"""
        <p style="font-size: 18px; text-align: center;">
            练习完成！<br>
            您的最终得分: <strong>{self.score}/{len(self.questions)} ({score_percent:.1f}%)</strong>
        </p>
        """
        
        if score_percent >= 80:
            message += "<p style='color: green; text-align: center;'>太棒了！超级棒棒哒！</p>"
        elif score_percent >= 60:
            message += "<p style='color: orange; text-align: center;'>哦豁！还不错哦！</p>"
        else:
            message += "<p style='color: red; text-align: center;'>偷懒了吧，再接再厉！</p>"
        
        # 添加重新开始按钮
        message += """
        <div style="text-align: center; margin-top: 20px;">
            <button style="padding: 10px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;"
                    onclick="window.pyqt.restartQuiz()">
                重新开始
            </button>
        </div>
        """
        
        # 创建结果对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("练习完成")
        dialog.setTextFormat(Qt.RichText)
        dialog.setText(message)
        
        # 添加重新开始功能
        dialog.buttonClicked.connect(self.restart_quiz)
        dialog.exec_()
    
    def restart_quiz(self):
        """重新开始测验"""
        self.current_question_index = 0
        self.score = 0
        # 重置答题状态（关键修改）
        self.answered_questions = set()
        self.user_answers = {}
        self.score_label.setText(f"分数: {self.score}/{len(self.questions)}")
        self.load_question(0)

    def load_question(self, index):
        """加载指定索引的题目"""
        if index < 0 or index >= len(self.questions):
            return
        
        self.current_question_index = index
        question = self.questions[index]
        
        # 更新题目显示（添加cartoo.gif）
        cartoo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "resources",
            "img",
            "cartoon.gif"
        )).replace('\\', '/')
        
        question_html = f"""
        <p style="font-size: 22px;"><strong>题目 {index+1}/{len(self.questions)}：</strong> {question.question}
            <img src="file:///{cartoo_path}" 
                 style="position: relative; right: 10px; bottom: -5px;
                        width: auto; height: 75px; opacity: 0.8;">
        </p>
        """
        base_url = QUrl.fromLocalFile(os.path.join(MATHJAX_PATH, "../"))
        self.question_view.setHtml(self.render_mathjax(question_html), base_url)
        
        # 更新选项显示（修改为img文件）
        for i, option in enumerate(question.options):
            # 构建选项img路径（修改目录为img）
            option_gif_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "resources",
                "img",  # 修改目录名称
                f"{chr(65+i)}.gif"
            )).replace('\\', '/')
            
            option_html = f"""
            <div style="position: relative; height: 100%;">
                <p>{chr(65+i)}. {option}</p>
                <img src="file:///{option_gif_path}" 
                     style="position: absolute; right: 10px; bottom: 10px;
                            width: auto; height: 80px; opacity: 0.8;">
            </div>
            """
            self.option_widgets[i].setHtml(self.render_mathjax(option_html), base_url)
        
        # 控制选项状态（关键修改）
        if index in self.answered_questions:
            # 已作答：显示用户选择并禁用选项
            selected = self.user_answers.get(index, -1)
            if selected != -1:
                self.options_group.button(selected).setChecked(True)
            for button in self.options_group.buttons():
                button.setEnabled(False)  # 禁用选择
        else:
            # 未作答：重置选择并启用选项
            self.options_group.setExclusive(False)
            for button in self.options_group.buttons():
                button.setChecked(False)
                button.setEnabled(True)  # 启用选择
            self.options_group.setExclusive(True)
        
        # 隐藏解释
        self.explanation_view.setVisible(False)
        
        # 更新按钮状态
        self.prev_button.setEnabled(index > 0)
        self.next_button.setEnabled(index < len(self.questions) - 1)
        
        # 更新进度条（关键修改：当前索引+1表示已完成题目数）
        self.progress_bar.setValue(index + 1)  # 原index改为index+1

    def prev_question(self):
        """加载上一题"""
        if self.current_question_index > 0:
            self.load_question(self.current_question_index - 1)

    def next_question(self):
        """加载下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self.load_question(self.current_question_index + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 检查MathJax路径是否存在
    if not os.path.exists(MATHJAX_PATH):
        QMessageBox.critical(
            None, 
            "MathJax缺失", 
            f"未找到MathJax库。请将MathJax放在以下路径：\n{MATHJAX_PATH}\n"
            "您可以从 https://mathjax.org/ 下载MathJax"
        )
        sys.exit(1)
    
    window = ChemistryQuizApp()
    window.show()
    sys.exit(app.exec_())
