import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QToolButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QMenuBar
)
from PySide6.QtGui import QPixmap, QAction, QIcon
from PySide6.QtCore import Qt, QSize
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("INFRA-π v.0.2")
        self.setGeometry(100, 100, 1200, 800)

        # Criar menu superior
        self.create_menus()

        #Vetor dos botões conectados
        self.conected_btns = []

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central_widget)

        # Coluna esquerda (33%)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        self.list_widget = QListWidget()
        left_layout.addWidget(self.list_widget)
        main_layout.addWidget(left_column)

        # Coluna direita (67%)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_logo("src/INFRAPy_logo.png")  # Substitua pelo caminho da sua imagem
        right_layout.addWidget(self.logo_label)

        # Container para os botões com ícones
        self.create_icon_buttons(right_layout)

        ######################
        #self.btn_load = QPushButton("Carregar Dados")
        #self.btn_process = QPushButton("Processar Dados")
        #self.btn_plot = QPushButton("Gerar Gráfico")
        #self.btn_export = QPushButton("Exportar Resultados")
        
        #buttons_layout.addWidget(self.btn_load)
        #buttons_layout.addWidget(self.btn_process)
        #buttons_layout.addWidget(self.btn_plot)
        #buttons_layout.addWidget(self.btn_export)
        #right_layout.addLayout(buttons_layout)
        ####################

        # Área do gráfico
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Pronto")
        right_layout.addWidget(self.status_bar)

        main_layout.addWidget(right_column, stretch=80)  # 80% do espaço

    def create_icon_buttons(self, parent_layout):
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 10)  # Margens vertical

        # Botões com ícones
        buttons = [
            ("Carregar Dados", "load_icon.png", "Clique para carregar dados", self.load_data),
            ("Processar Dados", "process_icon.png", "Clique para processar dados", self.process_data),
            ("Gerar Gráfico", "chart_icon.png", "Clique para gerar gráficos", self.plot_data),
            ("Exportar Resultados", "export_icon.png", "Clique para exportar dados", self.export_data)
        ]

        for text, icon, tooltip, conect_func in buttons:
            btn = self.create_tool_button(text, icon, tooltip)
            button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            btn.clicked.connect(conect_func)
            self.conected_btns.append(btn)

        parent_layout.addWidget(button_container)

    def create_tool_button(self, text, icon_path, tooltip):
        button = QToolButton()
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(40, 40))
        button.setText(text)
        button.setToolTip(tooltip)
        button.setFixedSize(100, 110)
        button.setStyleSheet("""
            QToolButton {
                padding: 5px;
                border-radius: 8px;
                background-color: #f5f5f5;
                margin: 2px;
                font-size: 7pt;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
          
            QToolButton::text {
                text-align: center;
                padding: 2px;
                white-space: pre-wrap;
            }
        """)

        return button

    def create_menus(self):
        menu_bar = QMenuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        file_menu.addAction(QAction("Novo", self))
        file_menu.addAction(QAction("Abrir", self))
        file_menu.addAction(QAction("Salvar", self))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Sair", self, triggered=self.close))

        # Menu Tratamento de dados
        data_menu = menu_bar.addMenu("Tratamento de Dados")
        data_menu.addAction(QAction("Filtrar Dados", self))
        data_menu.addAction(QAction("Normalizar", self))
        data_menu.addAction(QAction("Remover Outliers", self))

        # Menu Gráficos
        plot_menu = menu_bar.addMenu("Gráficos")
        plot_menu.addAction(QAction("Linha", self))
        plot_menu.addAction(QAction("Barras", self))
        plot_menu.addAction(QAction("Histograma", self))
        plot_menu.addAction(QAction("Dispersão", self))

        self.setMenuBar(menu_bar)

    def load_logo(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(300, 100, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))

    #def connect_signals(self):
    #    self.btn_load.clicked.connect(self.load_data)
    #    self.btn_process.clicked.connect(self.process_data)
    #    self.btn_plot.clicked.connect(self.plot_data)
    #    self.btn_export.clicked.connect(self.export_data)

    def load_data(self):
        self.list_widget.addItem("Dados carregados: dataset.csv")
        self.status_bar.showMessage("Dados carregados com sucesso!")

    def process_data(self):
        self.list_widget.addItem("Dados processados: normalização aplicada")
        self.status_bar.showMessage("Processamento concluído")

    def plot_data(self):
        # Exemplo simples de plotagem
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot([1,2,3,4], [1,4,9,16])
        ax.set_title("Gráfico de Exemplo")
        self.canvas.draw()
        self.status_bar.showMessage("Gráfico gerado")

    def export_data(self):
        self.list_widget.addItem("Resultados exportados: output.csv")
        self.status_bar.showMessage("Exportação concluída")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())