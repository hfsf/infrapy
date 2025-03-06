import sys

#######################
#import PySide6 as PyQt6
#######################

from PySide6.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QPushButton, 
                             QFileDialog, 
                             QVBoxLayout, 
                             QHBoxLayout, 
                             QLabel, 
                             QWidget, 
                             QFrame, 
                             QMessageBox,
                             QLineEdit, 
                             QComboBox, 
                             QCheckBox,
                             QDialog,
                             QPushButton)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import matplotlib as mpl
#mpl.rcParams['text.usetex'] = True
#mpl.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}'] #for \text command
mpl.use('QtAgg')
from scipy.signal import find_peaks, find_peaks_cwt
import json

from src import smoothing

#TODO: Incluir 2 janelas: Zoom e Panning; Desabilitar por padrão salvamento de imagens
#TODO: Analisar a migração do MPL para geração de gráficos

class ConfigDialog(QDialog):
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.config_data = config_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Text inputs for X, Y, Z, W
        self.num_freq_min_input = QLineEdit(str(self.config_data.get('Num. freq. mínimo', '')))
        self.num_freq_max_input = QLineEdit(str(self.config_data.get('Num. freq. máximo', '')))
        self.t_percent_min_input = QLineEdit(str(self.config_data.get('T(%) mínimo', '')))
        self.t_percent_max_input = QLineEdit(str(self.config_data.get('T(%) máximo', '')))

        layout.addWidget(QLabel("Número de frequência mínimo:"))
        layout.addWidget(self.num_freq_min_input)
        layout.addWidget(QLabel("Número de frequência máximo:"))
        layout.addWidget(self.num_freq_max_input)
        layout.addWidget(QLabel("T(%) mínimo:"))
        layout.addWidget(self.t_percent_min_input)
        layout.addWidget(QLabel("T(%) máximo:"))
        layout.addWidget(self.t_percent_max_input)

        # Combo boxes for A, B, C
        self.normalizar_combo = QComboBox()
        self.normalizar_combo.addItems(["Sim", "Não"])
        self.normalizar_combo.setCurrentText(self.config_data.get('Normalizar', 'Sim'))

        self.suavizar_combo = QComboBox()
        self.suavizar_combo.addItems(["Nenhum",
                                      "Savitz-Golay ordem 2", 
                                      "Savitz-Golay ordem 3", 
                                      "Savitz-Golay ordem 5",
                                      "Savitz-Golay ordem 7",
                                      "Gaussiano sigma=0,5",
                                      "Gaussiano sigma=2", 
                                      "Gaussiano sigma=3", 
                                      "Gaussiano sigma=5",  
                                      "Média móvel"])
        self.suavizar_combo.setCurrentText(self.config_data.get('Suavizar', 'Savitz-Golay ordem 2'))

        self.c_combo = QComboBox()
        self.c_combo.addItems(["Method1", "Method2", "Method3"])
        self.c_combo.setCurrentText(self.config_data.get('C', 'Method3'))

        layout.addWidget(QLabel("Normalizar gráfico:"))
        layout.addWidget(self.normalizar_combo)
        layout.addWidget(QLabel("Aplicar método de suavização do sinal:"))
        layout.addWidget(self.suavizar_combo)
        layout.addWidget(QLabel("C:"))
        layout.addWidget(self.c_combo)

        # Checkboxes
        self.checkbox1 = QCheckBox("Checkbox 1")
        self.checkbox1.setChecked(self.config_data.get('Checkbox1', True))

        self.checkbox2 = QCheckBox("Checkbox 2")
        self.checkbox2.setChecked(self.config_data.get('Checkbox2', False))

        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)

        # Buttons for Reset, Save, Load
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Resetar")
        self.reset_button.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Carregar")
        self.load_button.clicked.connect(self.load_config)
        button_layout.addWidget(self.load_button)

        self.definir_button = QPushButton("Definir")
        self.definir_button.clicked.connect(self.store_config)
        button_layout.addWidget(self.definir_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def store_config(self):
        self.accept()

    def reset_config(self):
        """Reset configuration to default values."""
        default_data = self.parent().load_config(self.parent().default_config_file)
        self.num_freq_min_input.setText(str(default_data.get('Num. freq. mínimo', '')))
        self.num_freq_max_input.setText(str(default_data.get('Num. freq. máximo', '')))
        self.t_percent_min_input.setText(str(default_data.get('T(%) mínimo', '')))
        self.t_percent_max_input.setText(str(default_data.get('T(%) máximo', '')))
        self.normalizar_combo.setCurrentText(default_data.get('Normalizar', 'Sim'))
        self.suavizar_combo.setCurrentText(default_data.get('Suavizar', 'Nenhum'))
        self.c_combo.setCurrentText(default_data.get('C', 'Method3'))
        self.checkbox1.setChecked(default_data.get('Checkbox1', True))
        self.checkbox2.setChecked(default_data.get('Checkbox2', False))

    def save_config(self):
        """Save current configuration to a file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "JSON Files (*.json)")
        if file_name:
            config_data = {
                'Num. freq. mínimo': int(self.num_freq_min_input.text()),
                'Num freq. máximo': int(self.num_freq_max_input.text()),
                'T(%) mínimo': int(self.t_percent_min_input.text()),
                'T(%) máximo': int(self.t_percent_max_input.text()),
                'Normalizar': self.normalizar_combo.currentText(),
                'Suavizar': self.suavizar_combo.currentText(),
                'C': self.c_combo.currentText(),
                'Checkbox1': self.checkbox1.isChecked(),
                'Checkbox2': self.checkbox2.isChecked(),
            }
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    if file_name.endswith('.json'):
                        json.dump(config_data, file, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    def load_config(self, file_name=''):
        """Load configuration from a file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
        print("Arquivo de configurações: ", file_name)
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    config_data = json.load(file)
                self.num_freq_min_input.setText(str(config_data.get('Num. freq. mínimo', '')))
                self.num_freq_max_input.setText(str(config_data.get('Num. freq. máximo', '')))
                self.t_percent_min_input.setText(str(config_data.get('T(%) mínimo', '')))
                self.t_percent_max_input.setText(str(config_data.get('T(%) máximo', '')))
                self.normalizar_combo.setCurrentText(config_data.get('Normalizar', 'Sim'))
                self.b_combo.setCurrentText(config_data.get('Suavizar', 'Nenhum'))
                self.c_combo.setCurrentText(config_data.get('C', 'Method3'))
                self.checkbox1.setChecked(config_data.get('Checkbox1', True))
                self.checkbox2.setChecked(config_data.get('Checkbox2', False))
                QMessageBox.information(self, "Success", "Configuration loaded successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")
        

    def get_config(self):
        """Return the current configuration as a dictionary."""
        return {
            'Num. freq. mínimo': int(self.num_freq_min_input.text()),
            'Num. freq. máximo': int(self.num_freq_max_input.text()),
            'T(%) mínimo': int(self.t_percent_min_input.text()),
            'T(%) máximo': int(self.t_percent_max_input.text()),
            'Normalizar': self.normalizar_combo.currentText(),
            'Suavizar': self.suavizar_combo.currentText(),
            'C': self.c_combo.currentText(),
            'Checkbox1': self.checkbox1.isChecked(),
            'Checkbox2': self.checkbox2.isChecked(),
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("INFRA-π")
        self.setGeometry(100, 600, 1000, 800)

        self.data_loaded = False

        #Configuration flags and data
        self.default_config_file = "src/default_config.json"
        self.config_data = self.load_config(self.default_config_file)

        self.data = None
        self.ax = None
        self.fig = None

        main_layout = QVBoxLayout()

        # Adicionando a imagem do logotipo
        self.logo_label = QLabel()
        pixmap = QPixmap("src/INFRAPy_logo.png")
        self.logo_label.setPixmap(pixmap.scaled(int(self.width() * 0.60), int(self.height() * 0.35)))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.logo_label)

        # Layout para os botões
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Carregar dados")
        #self.load_button.setIcon(QIcon.fromTheme("document-open"))
        self.load_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.load_button)

        self.plot_button = QPushButton("Gerar gráfico")
        self.plot_button.setToolTip("Generate a plot from the loaded data")
        self.plot_button.setEnabled(False)  # Disabled until data is loaded
        #self.plot_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))  # Para uso PyQt5
        self.plot_button.clicked.connect(self.generate_plot)
        button_layout.addWidget(self.plot_button)

        self.peaks_button = QPushButton("Encontrar Picos")
        self.peaks_button.setToolTip("Find and annotate peaks in the data")
        self.peaks_button.setEnabled(False)  # Disabled until data is loaded
        #self.peaks_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))  # Para uso PyQt5
        self.peaks_button.clicked.connect(self.find_annotate_peaks)
        button_layout.addWidget(self.peaks_button)

        self.config_button = QPushButton("Configurar")
        self.config_button.setToolTip("Configure application settings")
        #self.exit_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))  # Para uso PyQt5
        self.config_button.clicked.connect(self.config)
        button_layout.addWidget(self.config_button)

        self.exit_button = QPushButton("Sair")
        self.exit_button.setToolTip("Exit the application")
        #self.exit_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))  # Para uso PyQt5
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        main_layout.addLayout(button_layout)

        # Espaço para exibição dos gráficos
        self.graph_frame = QFrame()
        #self.graph_frame.setFrameShape(QFrame.Box)  # Para uso PyQt5
        #self.graph_frame.setFrameShadow(QFrame.Plain)  # Para uso PyQt5
        self.graph_frame.setStyleSheet("QFrame { border: 1px solid gray; background-color: white; }")        
        self.graph_frame.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.graph_frame)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                   "Abrir arquivo", 
                                                   "", 
                                                   "Arquivos de Texto (*.txt);;Arquivos CSV (*.csv)")
        if file_name:
            try:
                self.data = pd.read_csv(file_name, sep='\t', skiprows=3, decimal=',', comment='#')
                self.data_loaded = True
                self.plot_button.setEnabled(True)
                self.peaks_button.setEnabled(True)
                print(f"Arquivo carregado: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo: {str(e)}")

    def load_config(self, file_path):
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Configuration file '{file_path}' not found. Loading defaults.")
            return self.load_config(self.default_config_file)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            return {}

    def config(self):
        #QMessageBox.information(self, "Configuração", "Funcionalidade de configuração não implementada.")
        dialog = ConfigDialog(self.config_data, self)
        if dialog.exec() == QDialog.Accepted:
            self.config_data = dialog.get_config()
            print("Updated configuration:", self.config_data)    

    def _check_for_normalization(self, x, y):
        y_norm = y
        if self.config_data['Normalizar'] == "Sim":
            print("Normalizando valores de transmitância.")
            print("\t Valores originais: ", y)
            if np.any(y > 100.):
                y_norm = 100. * ( y_norm / np.max(y) )
                print("\t Valores normalizados: ", y_norm)    
        return y_norm

    def _check_for_smoothing(self, x, y):
        y_smooth = y
        print("Tamanho de x: ", len(x))
        print("Tamanho de y: ", len(y))
        if self.config_data['Suavizar'] != "Nenhum":
            print("Suazivando valores de transmitância.")
            print("\t Valores originais: ", y)
            y_smooth = smoothing.smooth(x, y, type=self.config_data['Suavizar'])
            print("\t Valores suavizados: ", y_smooth)
        
        return y_smooth

    def generate_plot(self):
        if not self.data_loaded:
            QMessageBox.warning(self, "Erro", "Nenhum arquivo de dados carregado.")
            return

        print("Configuração atual: ", self.config_data)
        #Recarga das configurações

        # Assumindo que a primeira coluna é 'Frequência' e a segunda é 'Transmitância'
        frequencia = self.data.iloc[:, 0].to_numpy()
        transmitancia = self.data.iloc[:, 1].to_numpy()

        # Se o gráfico estiver definido para ser normalizado, normalize-o
        transmitancia = self._check_for_normalization(frequencia, transmitancia)
        # Se o gráfico estiver definido para ser suavizado, suavize-o
        transmitancia = self._check_for_smoothing(frequencia, transmitancia)

        print("\t Frequência = ", frequencia)
        print("\t Transmitância = ", transmitancia)

        fig, ax = plt.subplots(layout='constrained')
        ax.plot(frequencia, transmitancia)#, label='Frequência vs Transmitância')
        ax.set_title('')
        ax.set_xlabel('Número de onda (1/cm)', fontweight='bold')
        ax.set_xlim(400, 4000)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='x', rotation=90)
        ax.set_ylim(self.config_data['T(%) mínimo'], self.config_data['T(%) máximo'])
        ax.set_ylabel('Transmitância (%)', fontweight='bold')
        ax.grid(True)
        ax.legend()
        fig.savefig('grafico.png')
        print("Arquivo de imagem salvo.")
        # Limpar o layout anterior e adicionar o novo gráfico
        #for i in reversed(range(self.graph_frame.layout().count())):
        #    self.graph_frame.layout().itemAt(i).widget().setParent(None)

        self.ax = ax
        self.fig = fig

        self.__update_plot()

    def __update_plot(self, savename=False):
        if self.ax is None or self.fig is None:
            QMessageBox.warning(self, "Erro", "Nenhum gráfico foi previamente gerado.")
            return

        canvas = FigureCanvas(self.fig)

        if self.graph_frame.layout() is None:
            layout = QVBoxLayout(self.graph_frame)
        else:
            layout = self.graph_frame.layout()

        for i in reversed(range(layout.count())): 
            widgetToRemove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)  


        layout.addWidget(canvas)
        canvas.draw()

        if savename:
            self.fig.savefig('grafico_'+savename+'.png')

    def find_annotate_peaks(self):
        
        if not self.data_loaded:
            QMessageBox.warning(self, "Erro", "Nenhum arquivo de dados carregado.")
            return
        # Assumindo que a primeira coluna é 'Frequência' e a segunda é 'Transmitância'
        frequencia = self.data.iloc[:, 0].to_numpy()
        transmitancia = self.data.iloc[:, 1].to_numpy()
        
        # Se o gráfico estiver definido para ser normalizado, normalize-o
        transmitancia = self._check_for_normalization(frequencia, transmitancia)
        # Se o gráfico estiver definido para ser suavizado, suavize-o
        transmitancia = self._check_for_smoothing(frequencia, transmitancia)

        #Absorbância é o inverso da transmitância
        #absorbancia = max(100, max(transmitancia)) - transmitancia
        absorbancia = np.log10(np.power(transmitancia,-1))

        #Encontrando os vales de transmitância (picos de absorbância) usando CWT
        peaks_index = find_peaks_cwt(absorbancia, [20,100])#)

        print("\t Frequência dos picos = ", frequencia[peaks_index])
        print("\t Transmitância = ", transmitancia[peaks_index])

        self.ax.plot(frequencia[peaks_index], transmitancia[peaks_index], "x")

        for peak in peaks_index:
            self.ax.annotate(f"{frequencia[peak]:.0f}", xy=(frequencia[peak], transmitancia[peak]),
                             xytext=(0, 10), textcoords='offset points', ha='center', color='red')

        self.__update_plot('picos_anotados')

        print("Arquivo de imagem com picos anotados salvo.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
