import os
import json
import random 
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QLabel, QPushButton, QRadioButton, QButtonGroup,QVBoxLayout,QDialog,
                             QMessageBox, QHBoxLayout, QProgressBar)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from common.base_app import BaseApp
from common.config import MATHJAX_PATH, render_mathjax

class ChemistryQuestion:
    def __init__(self, question, options, correct_index, explanation):
        self.question = question
        self.options = options
        self.correct_index = correct_index
        self.explanation = explanation

class ChemistryQuizApp(BaseApp):
    # 加载所有题目（供main_control调用）
    @staticmethod
    def load_all_questions():
        """加载所有题目数据（静态方法，用于获取总题数）"""
        json_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "sql", "questions.json"
        ))
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"未找到题目数据文件：{json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)
        return [ChemistryQuestion(
            question=data["question"],
            options=data["options"],
            correct_index=data["correct_index"],
            explanation=data["explanation"]
        ) for data in data_list]

    def __init__(self, question_count):
        super().__init__("化学方程式选择题练习", 1575, 950)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # 移除最大化按钮
        self.setFixedSize(self.size())  # 固定窗口尺寸，禁止调整大小
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.question_count = question_count
        self.all_questions = self.load_all_questions()  # 加载所有题目
        self._random_select_questions()  # 随机抽题（带验证）
        self.current_question_index = 0
        self.score = 0
        self.answered_questions = set()
        self.user_answers = {}
        self.init_ui()
        self.load_question(0)

    def _random_select_questions(self):
        """随机抽取不重复题目（带验证逻辑）"""
        actual_count = min(self.question_count, len(self.all_questions))
        if self.question_count > len(self.all_questions):
            QMessageBox.information(self, "提示", f"题库仅{len(self.all_questions)}题，将练习全部题目")
        
        # 随机抽取（不重复）
        self.questions = random.sample(self.all_questions, actual_count)

    def init_ui(self):
        # 分数显示（保留原有变量）
        self.score_label = QLabel(f"分数: {self.score}/{len(self.questions)}")
        self.score_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #ecf0f1;
                background: rgba(44, 62, 80, 0.9);
                border-radius: 8px;
                padding: 12px 20px;
                margin: 10px 0;
                border: 2px solid #3498db;
            }
        """)
        self.main_layout.addWidget(self.score_label)

        # 进度条（保留原有功能）
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 25px;
                background: rgba(255,255,255,0.15);
                border-radius: 12px;
                border: 2px solid #2980b9;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1abc9c, stop:1 #16a085);
                border-radius: 10px;
            }
        """)
        self.main_layout.addWidget(self.progress_bar)

        # 题目显示区（保留QWebEngineView）
        self.question_view = QWebEngineView()
        self.question_view.setMinimumHeight(150)
        self.question_view.setStyleSheet("""
            QWebEngineView {
                background: rgba(255,255,255,0.92);
                border-radius: 10px;
                border: 2px solid #ecf0f1;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        self.main_layout.addWidget(self.question_view)

        # 选项区域（保留原有RadioButton逻辑）
        self.options_group = QButtonGroup()
        self.options_layout = QVBoxLayout()
        self.option_widgets = []
        for i in range(4):
            option_widget = QWebEngineView()
            option_widget.setMinimumHeight(100)
            self.option_widgets.append(option_widget)
            radio = QRadioButton()
            # 单选按钮样式
            radio.setStyleSheet("""
                QRadioButton::indicator {
                    width: 24px;
                    height: 24px;
                    border-radius: 12px;
                    border: 2px solid #95a5a6;
                }
                QRadioButton::indicator:checked {
                    background: #2ecc71;
                    border-color: #27ae60;
                }
            """)
            self.options_group.addButton(radio, i)
            radio_layout = QHBoxLayout()
            radio_layout.addWidget(radio)
            radio_layout.addWidget(option_widget)
            radio_layout.setStretch(1, 1)
            self.options_layout.addLayout(radio_layout)
        self.main_layout.addLayout(self.options_layout)

        # 按钮区域（保留原有功能）
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("上一题")
        self.next_button = QPushButton("下一题")
        self.submit_button = QPushButton("提交答案")
        
        # 按钮样式（保留原有事件连接）
        button_style = """
            QPushButton {
                font-size: 20px;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                margin: 8px;
                min-width: 120px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3aa3ff, stop:1 #2980b9);
            }
        """
        self.prev_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)
        self.submit_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
                margin: 8px;
                min-width: 120px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #32ff7e, stop:1 #3ae374);
            }
        """)

        # 保留原有事件连接
        self.prev_button.clicked.connect(self.prev_question)
        self.next_button.clicked.connect(self.next_question)
        self.submit_button.clicked.connect(self.check_answer)

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.next_button)
        self.main_layout.addLayout(button_layout)

        # 解释区域（保留原有显示逻辑）
        self.explanation_view = QWebEngineView()
        self.explanation_view.setMinimumHeight(150)
        self.explanation_view.setVisible(False)
        self.explanation_view.setStyleSheet("""
            QWebEngineView {
                background: rgba(255,255,255,0.95);
                border-radius: 10px;
                border: 2px solid #bdc3c7;
                padding: 20px;
            }
        """)
        self.main_layout.addWidget(self.explanation_view)

    def load_question(self, index):
        """加载指定题目"""
        if index < 0 or index >= len(self.questions):
            return
        
        # 在加载新题之前重置滚动条
        self.explanation_view.page().runJavaScript("window.scrollTo(0,0);")

        self.current_question_index = index
        question = self.questions[index]
        base_url = QUrl.fromLocalFile(os.path.join(MATHJAX_PATH, "../"))

        # 题目HTML
        cartoo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "img", "cartoon.gif"
        )).replace('\\', '/')
        question_html = f"""
            <p style="font-size: 22px;"><strong>题目 {index+1}/{len(self.questions)}：</strong> {question.question}
                <img src="file:///{cartoo_path}" 
                     style="position: relative; right: 10px; bottom: -5px;
                            width: auto; height: 75px; opacity: 0.8;">
            </p>
        """
        self.question_view.setHtml(render_mathjax(question_html), base_url)

        # 选项HTML
        for i, option in enumerate(question.options):
            option_gif_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "resources", "img", f"{chr(65+i)}.gif"
            )).replace('\\', '/')
            option_html = f"""
                <div style="position: relative; height: 100%;">
                    <p>{chr(65+i)}. {option}</p>
                    <img src="file:///{option_gif_path}" 
                         style="position: absolute; right: 10px; bottom: 10px;
                                width: auto; height: 80px; opacity: 0.8;">
                </div>
            """
            self.option_widgets[i].setHtml(render_mathjax(option_html), base_url)

        # 控制选项状态和解析显示（修复显示逻辑）
        if index in self.answered_questions:
            selected = self.user_answers.get(index, -1)
            if selected != -1:
                self.options_group.button(selected).setChecked(True)
            for button in self.options_group.buttons():
                button.setEnabled(False)
            
            # 显示已保存的解析内容
            is_correct = (selected == question.correct_index)
            result = "正确！" if is_correct else "错误！"
            color = "green" if is_correct else "red"
            explanation_html = f"""
                <p style="font-weight: bold; color: {color}; font-size: 25px;">{result}</p>
                <p style="font-size: 20px;">{question.explanation}</p>
            """
            self.explanation_view.setHtml(render_mathjax(explanation_html), QUrl.fromLocalFile(MATHJAX_PATH))
            self.explanation_view.setVisible(True)
        else:
            self.options_group.setExclusive(False)
            for button in self.options_group.buttons():
                button.setChecked(False)
                button.setEnabled(True)
            self.options_group.setExclusive(True)
            self.explanation_view.setVisible(False)

        # 删除原有的setVisible(False)调用
        self.prev_button.setEnabled(index > 0)
        self.next_button.setEnabled(index < len(self.questions) - 1)
        self.progress_bar.setValue(index + 1)

    def check_answer(self):
        """检查答案"""
        selected_index = self.options_group.checkedId()
        if selected_index == -1:
            QMessageBox.warning(self, "提示", "请选择一个答案！")
            return
        
        question = self.questions[self.current_question_index]
        is_correct = (selected_index == question.correct_index)
        
        # 仅首次答对时加分
        if is_correct and self.current_question_index not in self.answered_questions:
            self.score += 1
            self.score_label.setText(f"分数: {self.score}/{len(self.questions)}")
        
        # 记录已作答状态和用户选择
        self.answered_questions.add(self.current_question_index)
        self.user_answers[self.current_question_index] = selected_index
        
        # 显示解释
        result = "正确！" if is_correct else "错误！"
        color = "green" if is_correct else "red"
        explanation_html = f"""
            <p style="font-weight: bold; color: {color}; font-size: 25px;">{result}</p>
            <p style="font-size: 20px;">{question.explanation}</p>
        """
        self.explanation_view.setHtml(render_mathjax(explanation_html), QUrl.fromLocalFile(MATHJAX_PATH))
        self.explanation_view.setVisible(True)
        
        # 如果是最后一题，显示最终得分
        if self.current_question_index == len(self.questions) - 1:
            self.show_final_score()

    def show_final_score(self):
        """显示最终得分对话框（修复关闭逻辑）"""
        score_percent = (self.score / len(self.questions)) * 100
        message_html = f"""
            <div style="text-align: center; font-size: 18px;">
                <h2>练习完成！</h2>
                <p>最终得分: <strong>{self.score}/{len(self.questions)} ({score_percent:.1f}%)</strong></p>
        """
        
        # 根据得分添加评价
        if score_percent >= 80:
            message_html += "<p style='color: green;'>太棒了！超级棒棒哒！</p>"
        elif score_percent >= 60:
            message_html += "<p style='color: orange;'>哦豁！还不错哦！</p>"
        else:
            message_html += "<p style='color: red;'>偷懒了吧，再接再厉！</p>"
        message_html += "</div>"

        # 创建自定义对话框并保存为实例变量
        self.result_dialog = QDialog(self)
        self.result_dialog.setWindowTitle("练习结果")
        layout = QVBoxLayout(self.result_dialog)

        # 添加消息内容
        msg_label = QLabel(message_html)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        # 添加按钮
        btn_layout = QHBoxLayout()
        restart_btn = QPushButton("重新开始")
        # 连接信号时传递对话框实例
        restart_btn.clicked.connect(lambda: self.restart_quiz(self.result_dialog))
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.result_dialog.close)  # 直接关闭对话框
        btn_layout.addWidget(restart_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(btn_layout)

        self.result_dialog.setMinimumWidth(400)
        self.result_dialog.exec_()

    def restart_quiz(self, dialog=None):
        """带对话框关闭的完整重置逻辑"""
        # 弹出确认对话框
        reply = QMessageBox.question(
            self, 
            "确认重新开始", 
            "是否确认重新开始练习？\n取消可继续查看已做题目",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 重新随机抽取题目
            self._random_select_questions()
            # 完整重置状态
            self.current_question_index = 0
            self.score = 0
            self.answered_questions = set()
            self.user_answers = {}
            self.score_label.setText(f"分数: {self.score}/{len(self.questions)}")
            self.progress_bar.setValue(0)
            # 重置选项按钮状态（
            for button in self.options_group.buttons():
                button.setEnabled(True)
                button.setChecked(False)
            # 加载新题目并关闭结果对话框
            self.load_question(0)
            if dialog:
                dialog.close()  # 关闭结果对话框

    def prev_question(self):
        """切换到上一题"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question(self.current_question_index)

    def next_question(self):
        """切换到下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question(self.current_question_index)