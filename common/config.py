import os

# Qt插件路径配置（公共）
os.environ['QT_QPA_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # 指向项目根目录的site-packages
    'site-packages', 
    'PyQt5', 
    'Qt', 
    'plugins'
)

# MathJax公共路径（项目根目录下的mathjax文件夹）
MATHJAX_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # 项目根目录
    "mathjax"
))

def render_mathjax(content):
    """通用MathJax渲染函数（两个程序共享）"""
    mathjax_url = f"file:///{MATHJAX_PATH}/es5/tex-chtml-full.js".replace('\\', '/')
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script type="text/javascript" src="{mathjax_url}?config=TeX-AMS-MML_HTMLorMML"></script>
        <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['$','$'], ['\\\\(','\\\\)']],
                    processEscapes: true,
                    packages: {{'[+]': ['mhchem']}}
                }},
                loader: {{
                    load: ['[tex]/mhchem']
                }},
                options: {{
                    showMathMenu: false,
                    messageStyle: "none"
                }},
                startup: {{
                    ready: () => {{
                        MathJax.startup.defaultReady();
                        MathJax.typeset();
                    }}
                }}
            }};
        </script>
        <style>
            body {{ font-size: 20px; line-height: 1.7; margin: 15px; }}
            .content {{ padding: 15px; }}
        </style>
    </head>
    <body>
        <div class="content">{content}</div>
        <script>window.onerror = function(msg) {{ console.error(msg); }}</script>
    </body>
    </html>
    """
