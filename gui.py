from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
import sys

# Asumiendo que get_fake_data proviene de data_simulator.py
# (Necesitaré ver data_simulator.py para asegurar compatibilidad)
from data_simulator import get_fake_data

# --- Indicador Circular Personalizado ---
class CircularIndicator(QWidget):
    def __init__(self, label_text, unit_text, max_value=100.0, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.unit_text = unit_text
        self.current_value = 0.0
        self.max_value = max_value
        self.setFixedSize(150, 150) # Tamaño fijo para el círculo

    def set_value(self, value):
        self.current_value = value
        self.update() # Redibuja el widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dibujar el fondo del círculo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2C3E50")) # Fondo oscuro para el círculo
        painter.drawEllipse(self.rect().adjusted(5, 5, -5, -5)) # Pequeño margen

        # Dibujar el arco de progreso
        angle_ratio = (self.current_value / self.max_value) if self.max_value > 0 else 0
        sweep_angle = int(360 * angle_ratio)

        # Determinar color basado en el valor (ejemplo para Corriente/Potencia)
        if "Corriente" in self.label_text or "Potencia" in self.label_text:
            if angle_ratio > 0.8:
                fill_color = QColor("#E74C3C") # Rojo si es alto
            elif angle_ratio > 0.5:
                fill_color = QColor("#F39C12") # Naranja si es medio
            else:
                fill_color = QColor("#2ECC71") # Verde si es bajo
        else:
            fill_color = QColor("#3498DB") # Azul por defecto

        painter.setPen(QPen(fill_color, 10, Qt.SolidLine, Qt.RoundCap))
        # El ángulo inicial es 90 * 16 (horas 3), pero queremos empezar en 90 grados (horas 12)
        # y dibujar en sentido horario, así que 90 * 16 es correcto para el inicio del arco en Qt.
        painter.drawArc(self.rect().adjusted(5, 5, -5, -5), 90 * 16, -sweep_angle * 16) # Arcos en sentido horario

        # Dibujar el texto del valor
        painter.setPen(QColor("#ECF0F1")) # Color del texto
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        text_rect = self.rect()
        painter.drawText(text_rect, Qt.AlignCenter | Qt.AlignBottom, f"{self.current_value:.2f} {self.unit_text}")

        # Dibujar el texto de la etiqueta
        font.setPointSize(10)
        font.setWeight(QFont.Normal)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.AlignTop, self.label_text)


# --- Monitor Widget Modernizado ---
class MonitorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Consumo Eléctrico - Hogar Inteligente")
        self.setGeometry(100, 100, 800, 600) # Tamaño inicial de la ventana

        self.setup_ui()
        self.apply_styles()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000) # cada 1 segundo

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Título de la aplicación ---
        title_label = QLabel("MONITOR DE ENERGÍA")
        title_label.setObjectName("titleLabel") # Para aplicar estilo CSS
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Indicadores Circulares ---
        indicators_layout = QHBoxLayout()
        indicators_layout.setAlignment(Qt.AlignCenter)
        indicators_layout.setSpacing(30)

        self.volt_indicator = CircularIndicator("Voltaje", "V", max_value=240.0)
        self.curr_indicator = CircularIndicator("Corriente", "A", max_value=20.0) # Ajusta max_value según tu caso
        self.pow_indicator = CircularIndicator("Potencia", "W", max_value=5000.0) # Ajusta max_value
        self.energy_indicator = CircularIndicator("Energía", "Wh", max_value=10000.0) # Energía acumulada puede tener un max muy grande

        indicators_layout.addWidget(self.volt_indicator)
        indicators_layout.addWidget(self.curr_indicator)
        indicators_layout.addWidget(self.pow_indicator)
        indicators_layout.addWidget(self.energy_indicator)

        main_layout.addLayout(indicators_layout)

        # --- Sección de Lecturas Detalladas (Opcional, pero bueno para la completitud) ---
        # Si queremos mantener los valores numéricos grandes y claros
        data_display_layout = QVBoxLayout()
        data_display_layout.setSpacing(10)
        data_display_layout.setAlignment(Qt.AlignCenter)

        self.volt_label = self._create_data_label("Voltaje")
        self.curr_label = self._create_data_label("Corriente")
        self.pow_label = self._create_data_label("Potencia")
        self.energy_label = self._create_data_label("Energía")

        data_display_layout.addWidget(self.volt_label)
        data_display_layout.addWidget(self.curr_label)
        data_display_layout.addWidget(self.pow_label)
        data_display_layout.addWidget(self.energy_label)

        main_layout.addLayout(data_display_layout)

        # --- Espaciador para empujar el contenido hacia arriba ---
        main_layout.addStretch()

    def _create_data_label(self, prefix):
        label = QLabel(f"{prefix}: -")
        label.setObjectName("dataLabel")
        label.setAlignment(Qt.AlignCenter)
        return label

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2F4F4F; /* Fondo oscuro principal */
                color: #ECF0F1; /* Texto claro */
                font-family: "Segoe UI", "Arial", sans-serif;
            }
            #titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ADD8E6; /* Azul claro para el título */
                margin-bottom: 20px;
                padding: 10px;
                border-bottom: 2px solid #5F9EA0; /* Línea decorativa */
            }
            #dataLabel {
                font-size: 20px;
                font-weight: bold;
                color: #D3D3D3; /* Gris claro para los datos */
                padding: 5px;
            }
            CircularIndicator {
                /* No se puede aplicar mucho estilo CSS directamente a un QWidget pintado con QPainter */
                /* Sus estilos se manejan en el paintEvent */
            }
        """)

    def update_data(self):
        data = get_fake_data()
        self.volt_indicator.set_value(data['voltaje'])
        self.curr_indicator.set_value(data['corriente'])
        self.pow_indicator.set_value(data['potencia'])
        self.energy_indicator.set_value(data['energia'])

        # Actualizar también las etiquetas de texto para una vista detallada
        self.volt_label.setText(f"Voltaje: {data['voltaje']:.2f} V")
        self.curr_label.setText(f"Corriente: {data['corriente']:.2f} A")
        self.pow_label.setText(f"Potencia: {data['potencia']:.2f} W")
        self.energy_label.setText(f"Energía: {data['energia']:.2f} Wh")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = MonitorWidget()
    monitor.show()
    sys.exit(app.exec_())
