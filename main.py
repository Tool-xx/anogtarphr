import sys
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebChannel import QWebChannel

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(32)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QLabel {
                color: #58a6ff;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                min-width: 32px;
                max-width: 32px;
                min-height: 24px;
                max-height: 24px;
                border-radius: 3px;
                color: #8b949e;
                font-size: 14px;
                padding: 0;
                margin: 1px;
            }
            QPushButton:hover {
                background-color: #21262d;
                color: #ffffff;
            }
            #minimizeBtn:hover { background-color: #238636; }
            #maximizeBtn:hover { background-color: #58a6ff; }
            #closeBtn:hover { background-color: #f85149; }
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)
        
        self.title_label = QLabel("anoGOVmaster")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #58a6ff;
                font-size: 11px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                padding-left: 4px;
            }
        """)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.toggleBtn = QPushButton("▼")
        self.toggleBtn.setCursor(Qt.PointingHandCursor)
        self.toggleBtn.setObjectName("maximizeBtn")
        self.toggleBtn.setToolTip("Развернуть/Свернуть контент")
        self.toggleBtn.clicked.connect(self.toggleContent)
        
        self.minimizeBtn = QPushButton("—")
        self.minimizeBtn.setCursor(Qt.PointingHandCursor)
        self.minimizeBtn.setObjectName("minimizeBtn")
        self.minimizeBtn.setToolTip("Свернуть в панель задач")
        self.minimizeBtn.clicked.connect(self.parent.showMinimized)
        
        self.closeBtn = QPushButton("✕")
        self.closeBtn.setCursor(Qt.PointingHandCursor)
        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setToolTip("Закрыть приложение")
        self.closeBtn.clicked.connect(self.parent.closeApp)
        
        layout.addWidget(self.title_label)
        layout.addWidget(spacer)
        layout.addWidget(self.toggleBtn)
        layout.addWidget(self.minimizeBtn)
        layout.addWidget(self.closeBtn)
        
    def toggleContent(self):
        if self.parent.contentVisible:
            self.toggleBtn.setText("▼")
            self.parent.content.hide()
            self.parent.setMinimumHeight(32)
            self.parent.setMaximumHeight(32)
            self.parent.setFixedHeight(32)
            self.parent.resize(400, 32)
        else:
            self.toggleBtn.setText("▲")
            self.parent.content.show()
            self.parent.setMinimumHeight(450)
            self.parent.setMaximumHeight(16777215)
            self.parent.setFixedHeight(16777215)
            self.parent.resize(800, 550)
        self.parent.contentVisible = not self.parent.contentVisible

class CounterHandler(QObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    @pyqtSlot(str)
    def saveCounters(self, data):
        try:
            counters = json.loads(data)
            self.parent.counters = counters
            self.parent.saveCountersToFile()
        except Exception as e:
            print(f"Ошибка при сохранении счетчиков: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.contentVisible = False
        self.counters = {"weapon": 0, "hunt": 0, "fishing": 0}
        self.loadCountersFromFile()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("anoGOVmaster - Памятка Лицензиара")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMinimumSize(300, 32)
        self.resize(400, 32)
        self.setMaximumHeight(32)
        self.setFixedHeight(32)
        
        self.centerWindow()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)
        
        self.content = QWebEngineView()
        self.loadHTML()
        layout.addWidget(self.content)
        self.content.hide()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
            }
        """)
        
        self.drag_pos = None
        
    def centerWindow(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 4)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.title_bar.geometry().contains(event.pos()) or not self.contentVisible:
                self.drag_pos = event.globalPos()
                event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            delta = event.globalPos() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPos()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()
        
    def loadCountersFromFile(self):
        try:
            if os.path.exists("base.txt"):
                with open("base.txt", "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        self.counters = json.loads(data)
                        print(f"Загружены счетчики: {self.counters}")
            else:
                self.saveCountersToFile()
        except Exception as e:
            print(f"Ошибка при загрузке счетчиков: {e}")
            self.saveCountersToFile()
    
    def saveCountersToFile(self):
        try:
            with open("base.txt", "w", encoding="utf-8") as f:
                json.dump(self.counters, f, ensure_ascii=False, indent=2)
            print(f"Счетчики сохранены: {self.counters}")
        except Exception as e:
            print(f"Ошибка при сохранении счетчиков: {e}")
    
    def loadHTML(self):
        counters_json = json.dumps(self.counters)
        
        html_content = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Памятка Лицензиара - GTA 5 RP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #121212; 
            color: #e0e0e0; 
            line-height: 1.4; 
            padding: 12px;
            font-size: 13px;
        }}
        .container {{ 
            max-width: 1000px; 
            margin: 0 auto; 
            background: #1e1e1e; 
            border: 1px solid #333; 
            border-radius: 5px;
        }}
        .header {{ 
            background: #0d1117; 
            color: #fff; 
            padding: 12px; 
            text-align: center; 
            border-bottom: 1px solid #30363d; 
        }}
        .header h1 {{ font-size: 1.2em; font-weight: 600; margin-bottom: 4px; }}
        .header p {{ font-size: 0.8em; opacity: 0.8; }}
        .header .credit {{
            margin-top: 4px;
            font-size: 0.75em;
            opacity: 0.7;
        }}
        .header .credit a {{
            color: #58a6ff;
            text-decoration: none;
            transition: color 0.2s ease;
        }}
        .header .credit a:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}
        .tabs {{ display: flex; background: #161b22; border-bottom: 1px solid #30363d; }}
        .tab-btn {{ 
            flex: 1; padding: 8px 12px; border: none; background: none; 
            color: #8b949e; font-size: 0.85em; font-weight: 500; cursor: pointer; 
            border-bottom: 2px solid transparent; transition: all 0.2s ease; 
        }}
        .tab-btn:hover {{ color: #fff; background: #21262d; }}
        .tab-btn.active {{ color: #fff; border-bottom-color: #58a6ff; background: #1e1e1e; }}
        .tab-content {{ display: none; padding: 15px; }}
        .tab-content.active {{ display: block; }}
        .licenses-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 12px; 
            margin-top: 8px; 
        }}
        .license-card {{ 
            border: 1px solid #30363d; border-radius: 5px; padding: 12px; 
            background: #161b22; height: 100%; display: flex; flex-direction: column; 
        }}
        .license-title {{ 
            font-size: 0.9em; font-weight: 600; color: #fff; margin-bottom: 8px; 
            padding-bottom: 4px; border-bottom: 1px solid #58a6ff; line-height: 1.1; 
        }}
        .counter-section {{ display: flex; flex-direction: column; gap: 12px; }}
        .counter-row {{ 
            display: flex; align-items: center; gap: 10px; padding: 10px; 
            background: #21262d; border-radius: 5px; border: 1px solid #30363d; 
        }}
        .counter-label {{ font-size: 0.95em; font-weight: 600; color: #fff; min-width: 90px; }}
        .counter-controls {{ display: flex; gap: 6px; align-items: center; }}
        .counter-btn {{ 
            width: 28px; height: 28px; border: 1px solid #58a6ff; background: #161b22; 
            color: #58a6ff; border-radius: 3px; cursor: pointer; font-size: 1em; 
            font-weight: bold; display: flex; align-items: center; justify-content: center; 
        }}
        .counter-btn:hover {{ background: #58a6ff; color: #fff; }}
        .counter-value {{ 
            min-width: 40px; text-align: center; font-size: 1.1em; font-weight: 700; 
            color: #3fb950; font-family: 'Courier New', monospace; 
        }}
        .stats-panel {{ 
            background: #0d1117; padding: 12px; border-radius: 5px; 
            border: 1px solid #30363d; margin-top: 12px; 
        }}
        .stats-title {{ font-size: 0.95em; font-weight: 600; color: #fff; margin-bottom: 10px; text-align: center; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }}
        .stat-item {{ text-align: center; padding: 10px; background: #21262d; border-radius: 5px; }}
        .stat-label {{ font-size: 0.8em; color: #8b949e; margin-bottom: 4px; }}
        .stat-value {{ font-size: 1.2em; font-weight: 700; color: #fff; font-family: 'Courier New', monospace; }}
        .copy-btn {{ 
            width: 100%; padding: 8px; background: #3fb950; color: #fff; 
            border: none; border-radius: 5px; font-size: 0.9em; font-weight: 500; 
            cursor: pointer; transition: background 0.2s ease; 
        }}
        .copy-btn:hover {{ background: #2ea44f; }}
        .copy-success {{ background: #f85149 !important; animation: pulse 0.5s ease-in-out; }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        .qa-section {{ flex: 1; overflow-y: auto; max-height: 350px; padding-right: 3px; }}
        .question {{ margin-bottom: 8px; }}
        .question-text {{ font-weight: 500; color: #d2d2d2; font-size: 0.82em; margin-bottom: 3px; }}
        .answer {{ color: #b0b0b0; font-size: 0.78em; line-height: 1.3; padding-left: 8px; border-left: 2px solid #58a6ff; }}
        .requirements {{ margin-bottom: 8px; }}
        .requirements h3 {{ font-size: 0.82em; font-weight: 600; margin-bottom: 4px; color: #d2d2d2; }}
        .requirements ul {{ list-style: none; padding-left: 0; }}
        .requirements li {{ 
            padding: 1px 0; position: relative; padding-left: 14px; 
            font-size: 0.8em; color: #b0b0b0; line-height: 1.2; 
        }}
        .requirements li:before {{ content: "•"; position: absolute; left: 0; font-weight: bold; color: #58a6ff; }}
        .costs {{ background: #21262d; padding: 8px; border-left: 3px solid #f85149; border-radius: 0 3px 3px 0; margin-top: auto; }}
        .costs h3 {{ font-size: 0.82em; font-weight: 600; margin-bottom: 4px; color: #f85149; }}
        .cost-item {{ display: flex; justify-content: space-between; margin: 3px 0; font-size: 0.8em; font-weight: 500; color: #d2d2d2; }}
        .total {{ border-top: 1px solid #30363d; padding-top: 3px; margin-top: 3px; font-weight: 600; font-size: 0.85em; color: #f0f6fc; }}
        .treasury {{ color: #3fb950; font-weight: 600; }}
        .qa-section ul {{ list-style: none; padding-left: 0; margin-top: 2px; }}
        .qa-section li {{ margin: 1px 0; padding-left: 14px; position: relative; font-size: 0.78em; }}
        .qa-section li:before {{ content: "•"; position: absolute; left: 0; color: #58a6ff; font-weight: bold; }}
    </style>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Памятка Лицензиара</h1>
            <p>HR Менеджер | GTA 5 RP</p>
            <div class="credit">by <a href="https://t.me/anocode_gr" target="_blank" onclick="openTelegram()">@anocode_gr</a></div>
        </div>

        <div class="tabs">
            <button class="tab-btn" onclick="switchTab(0)">Лицензии</button>
            <button class="tab-btn" onclick="switchTab(1)">Вопросы</button>
            <button class="tab-btn active" onclick="switchTab(2)">Счетчик</button>
        </div>

        <!-- Вкладка Лицензии -->
        <div class="tab-content" id="tab-0">
            <div class="licenses-grid">
                <div class="license-card">
                    <div class="license-title">Лицензия на лёгкое/среднее оружие</div>
                    <div class="requirements">
                        <h3>Для получения лицензии необходимо:</h3>
                        <ul>
                            <li>Иметь мед. карту с пометкой "A"</li>
                            <li>Знать закон "Оружие в штате SA"</li>
                        </ul>
                    </div>
                    <div class="costs">
                        <h3>Стоимость:</h3>
                        <div class="cost-item"><span>Лицензия</span><span>10.000$</span></div>
                        <div class="cost-item"><span>Экзамен</span><span>10.000$</span></div>
                        <div class="cost-item total"><span>Общая сумма</span><span>20.000$</span></div>
                        <div class="cost-item"><span class="treasury">В казну</span><span class="treasury">5.000$</span></div>
                    </div>
                </div>

                <div class="license-card">
                    <div class="license-title">Лицензия на профессиональную рыбалку</div>
                    <div class="requirements">
                        <h3>Для получения лицензии необходимо:</h3>
                        <ul>
                            <li>Знать закон "О добыче и сохранении биологических и охотничьих ресурсов"</li>
                        </ul>
                    </div>
                    <div class="costs">
                        <h3>Стоимость:</h3>
                        <div class="cost-item"><span>Лицензия</span><span>10.000$</span></div>
                        <div class="cost-item"><span>Экзамен</span><span>8.000$</span></div>
                        <div class="cost-item total"><span>Общая сумма</span><span>18.000$</span></div>
                        <div class="cost-item"><span class="treasury">В казну</span><span class="treasury">5.000$</span></div>
                    </div>
                </div>

                <div class="license-card">
                    <div class="license-title">Лицензия на охоту</div>
                    <div class="requirements">
                        <h3>Для получения лицензии необходимо:</h3>
                        <ul>
                            <li>Иметь мед. карту с пометкой "A"</li>
                            <li>Иметь лицензию на оружие</li>
                            <li>Знать закон "О добыче и сохранении биологических и охотничьих ресурсов"</li>
                        </ul>
                    </div>
                    <div class="costs">
                        <h3>Стоимость:</h3>
                        <div class="cost-item"><span>Лицензия</span><span>10.000$</span></div>
                        <div class="cost-item"><span>Экзамен</span><span>20.000$</span></div>
                        <div class="cost-item total"><span>Общая сумма</span><span>30.000$</span></div>
                        <div class="cost-item"><span class="treasury">В казну</span><span class="treasury">15.000$</span></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Вкладка Вопросы -->
        <div class="tab-content" id="tab-1">
            <div class="licenses-grid">
                <div class="license-card">
                    <div class="license-title">ЛИЦЕНЗИЯ НА ОРУЖИЕ</div>
                    <div class="qa-section">
                        <div class="question">
                            <div class="question-text">В каких случаях гражданским лицам разрешено использование оружия?</div>
                            <div class="answer">Гражданским лицам разрешено использование оружия исключительно в целях самообороны.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Расскажите, пожалуйста, правила ношения оружия с собой.</div>
                            <div class="answer">Оружие гражданскими лицами переносится на специальном ремне, в кобуре, а также в сумке, рюкзаке или под одеждой и обязательно должно находиться на предохранителе.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Где разрешена покупка гражданского оружия в штате?</div>
                            <div class="answer">Покупка гражданского оружия разрешена только в специализированных оружейных магазинах.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Расскажите, пожалуйста, правила хранения оружия дома.</div>
                            <div class="answer">Хранение оружия осуществляется в сейфе, в разряженном состоянии и на предохранителе.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Разрешено ли гражданским лицам использование специальных средств (например, электрошокового оружия)?</div>
                            <div class="answer">Нет. Использование специальных средств разрешено исключительно государственным сотрудникам.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Разрешено ли гражданским лицам хранение легально приобретённого оружия в своём транспортном средстве?</div>
                            <div class="answer">Да, разрешено.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Расскажите, пожалуйста, правила хранения оружия в транспортном средстве.</div>
                            <div class="answer">Оружие должно храниться в оружейном сейфе, быть разряженным и на предохранителе.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Как распознать нелегальное оружие?</div>
                            <div class="answer">Нелегальным считается оружие с нечитаемым либо частично читаемым серийным номером.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Разрешено ли гражданским лицам использовать крупнокалиберное оружие?</div>
                            <div class="answer">Гражданским лицам запрещено использование крупнокалиберного оружия.</div>
                        </div>
                    </div>
                </div>

                <div class="license-card">
                    <div class="license-title">ЛИЦЕНЗИЯ НА ПРОФЕССИОНАЛЬНОЕ РЫБОЛОВСТВО</div>
                    <div class="qa-section">
                        <div class="question">
                            <div class="question-text">Где в штате разрешено любительское рыболовство без соответствующей лицензии?</div>
                            <div class="answer">Любительская рыбная ловля без лицензии разрешена на специально оборудованных городских пирсах.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Сколько разрешено добывать водных биоресурсов без лицензии?</div>
                            <div class="answer">До 15 кг.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое наказание предусмотрено за превышение установленной нормы?</div>
                            <div class="answer">Штраф в размере $17.000.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Где разрешена добыча водных ресурсов при наличии лицензии на «Профессиональное рыболовство»?</div>
                            <div class="answer">
                                <ul>
                                    <li>Тихий океан</li>
                                    <li>Озеро округа Блейн (прибрежная зона)</li>
                                    <li>Остров в округе Лос-Сантос</li>
                                    <li>Специально оборудованные места (пирсы)</li>
                                </ul>
                            </div>
                        </div>
                        <div class="question">
                            <div class="question-text">Сколько разрешено добывать водных биоресурсов с лицензией «Профессиональное рыболовство»?</div>
                            <div class="answer">До 70 кг.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое наказание предусмотрено за превышение нормы до 85 кг?</div>
                            <div class="answer">Штраф $800 за каждый лишний килограмм.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое наказание предусмотрено за превышение нормы свыше 85 кг?</div>
                            <div class="answer">Штраф $15.000, а также изъятие лицензии на добычу рыбы.</div>
                        </div>
                    </div>
                </div>

                <div class="license-card">
                    <div class="license-title">ЛИЦЕНЗИЯ НА ОХОТУ</div>
                    <div class="qa-section">
                        <div class="question">
                            <div class="question-text">Разрешена ли в нашем штате охота без лицензии?</div>
                            <div class="answer">Нет. Охота разрешена исключительно при наличии специализированной лицензии.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое оружие разрешено использовать для охоты?</div>
                            <div class="answer">Разрешено использование специализированных охотничьих ружей. Использование иных видов оружия, а также средств и приспособлений для убийства животных расценивается как браконьерство.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какая установлена норма добычи охотничьих ресурсов?</div>
                            <div class="answer">До 40 кг.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое наказание предусмотрено за превышение установленной нормы до 50 кг?</div>
                            <div class="answer">Штраф $1.000 за каждый лишний килограмм.</div>
                        </div>
                        <div class="question">
                            <div class="question-text">Какое наказание предусмотрено за превышение установленной нормы свыше 50 кг?</div>
                            <div class="answer">
                                <ul>
                                    <li>Изъятие лицензии на охоту</li>
                                    <li>Конфискация всей добычи, превышающей установленную норму</li>
                                    <li>Штраф в размере $10.000</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Вкладка Счетчик -->
        <div class="tab-content active" id="tab-2">
            <div class="counter-section">
                <div class="counter-row">
                    <div class="counter-label">Оружие</div>
                    <div class="counter-controls">
                        <button class="counter-btn" onclick="changeCounter('weapon', -1)">−</button>
                        <div class="counter-value" id="weapon-count">{self.counters['weapon']}</div>
                        <button class="counter-btn" onclick="changeCounter('weapon', 1)">+</button>
                    </div>
                </div>

                <div class="counter-row">
                    <div class="counter-label">Охота</div>
                    <div class="counter-controls">
                        <button class="counter-btn" onclick="changeCounter('hunt', -1)">−</button>
                        <div class="counter-value" id="hunt-count">{self.counters['hunt']}</div>
                        <button class="counter-btn" onclick="changeCounter('hunt', 1)">+</button>
                    </div>
                </div>

                <div class="counter-row">
                    <div class="counter-label">Рыбалка</div>
                    <div class="counter-controls">
                        <button class="counter-btn" onclick="changeCounter('fishing', -1)">−</button>
                        <div class="counter-value" id="fishing-count">{self.counters['fishing']}</div>
                        <button class="counter-btn" onclick="changeCounter('fishing', 1)">+</button>
                    </div>
                </div>

                <div class="stats-panel">
                    <div class="stats-title">Статистика лицензий</div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">охота</div>
                            <div class="stat-value" id="stat-hunt">{self.counters['hunt']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">оружие</div>
                            <div class="stat-value" id="stat-weapon">{self.counters['weapon']}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">рыбалка</div>
                            <div class="stat-value" id="stat-fishing">{self.counters['fishing']}</div>
                        </div>
                    </div>
                    <button class="copy-btn" onclick="copyStats()">📋 Скопировать статистику</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let counters = {counters_json};
        
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            window.pyHandler = channel.objects.pyHandler;
        }});
        
        function updateDisplay() {{
            document.getElementById('weapon-count').textContent = counters.weapon;
            document.getElementById('hunt-count').textContent = counters.hunt;
            document.getElementById('fishing-count').textContent = counters.fishing;
            
            document.getElementById('stat-weapon').textContent = counters.weapon;
            document.getElementById('stat-hunt').textContent = counters.hunt;
            document.getElementById('stat-fishing').textContent = counters.fishing;
        }}
        
        updateDisplay();

        function changeCounter(type, delta) {{
            counters[type] = Math.max(0, counters[type] + delta);
            updateDisplay();
            
            if (window.pyHandler) {{
                window.pyHandler.saveCounters(JSON.stringify(counters));
            }} else {{
                localStorage.setItem('licenseCounters', JSON.stringify(counters));
            }}
        }}

        function copyStats() {{
            const text = `охота: ${{counters.hunt}}\\nоружие: ${{counters.weapon}}\\nрыбалка: ${{counters.fishing}}`;
            
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(() => {{
                    showCopySuccess();
                }}).catch(() => {{
                    fallbackCopy(text);
                }});
            }} else {{
                fallbackCopy(text);
            }}
        }}
        
        function fallbackCopy(text) {{
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                document.execCommand('copy');
                showCopySuccess();
            }} catch (err) {{
                console.error('Не удалось скопировать текст:', err);
            }}
            document.body.removeChild(textArea);
        }}
        
        function showCopySuccess() {{
            const btn = document.querySelector('.copy-btn');
            const originalText = btn.textContent;
            btn.textContent = '✓ Скопировано!';
            btn.classList.add('copy-success');
            setTimeout(() => {{
                btn.textContent = originalText;
                btn.classList.remove('copy-success');
            }}, 1500);
        }}

        function switchTab(index) {{
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(`tab-${{index}}`).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function openTelegram() {{
            // Открываем ссылку в браузере по умолчанию
            window.open('https://t.me/anocode_gr', '_blank');
            return false;
        }}
    </script>
</body>
</html>'''
        
        self.content.setHtml(html_content)
        
        self.handler = CounterHandler(self)
        self.channel = QWebChannel()
        self.channel.registerObject("pyHandler", self.handler)
        self.content.page().setWebChannel(self.channel)
    
    def closeApp(self):
        self.saveCountersToFile()
        QApplication.quit()
    
    def closeEvent(self, event):
        self.saveCountersToFile()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("anoGOVmaster")
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
