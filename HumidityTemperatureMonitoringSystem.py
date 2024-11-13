import sys
import serial
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QSlider, QSpinBox, QTableWidget, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# # Serial port connection
ser = serial.Serial('/dev/cu.usbserial-1110', 9600)  # Customize to your own port

class TempHumidityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_temp_threshold = 30  # Default temperature warning limit
        self.current_hum_threshold = 50   # Default humidity warning limit 
        self.temp_data = []
        self.hum_data = []        
        self.initUI()
        
      

    def initUI(self):
        
        # Placeholder for a circular gauge, using a QLabel for simplicity
        self.temp_gauge = QLabel("🌡️ & 💧", self)
        self.temp_gauge.setStyleSheet("font-size: 25px; color:red;")
        gauge_layout = QHBoxLayout()
        gauge_layout.addStretch()  # Sol tarafı boşluk bırakmak için
        gauge_layout.addWidget(self.temp_gauge)  # temp_gauge sağa hizalanır        
        
        # Temperature and Humidity labels
        self.temp_label = QLabel("🌡️ Temperature: ---", self)
        self.hum_label = QLabel("💧 Humidity: ---", self)        
        
        self.warning_label = QLabel("", self)
        self.temp_label.setStyleSheet("font-size: 16px; color: darkred; font-weight: bold;")
        self.hum_label.setStyleSheet("font-size: 16px; color: darkblue; font-weight: bold;")
        self.warning_label.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 red, stop:1 orange); font-size: 14px;")        

        # Temperature limit determination part
        temp_threshold_layout = QHBoxLayout()
        self.temp_threshold_label = QLabel("Temperature Warning Limit:", self)
        self.temp_slider = QSlider(Qt.Horizontal, self)
        self.temp_slider.setRange(0, 50)
        self.temp_slider.setValue(30)

        self.temp_spin_box = QSpinBox(self)
        self.temp_spin_box.setRange(0, 50)
        self.temp_spin_box.setValue(30)

        self.temp_slider.valueChanged.connect(self.temp_spin_box.setValue)
        self.temp_spin_box.valueChanged.connect(self.temp_slider.setValue)

        temp_threshold_layout.addWidget(self.temp_threshold_label)
        temp_threshold_layout.addWidget(self.temp_slider)
        temp_threshold_layout.addWidget(self.temp_spin_box)

        # Humidity limit determination part
        hum_threshold_layout = QHBoxLayout()
        self.hum_threshold_label = QLabel("Humidity Warning Limit:", self)
        self.hum_slider = QSlider(Qt.Horizontal, self)
        self.hum_slider.setRange(0, 100)
        self.hum_slider.setValue(50)

        self.hum_spin_box = QSpinBox(self)
        self.hum_spin_box.setRange(0, 100)
        self.hum_spin_box.setValue(50)

        self.hum_slider.valueChanged.connect(self.hum_spin_box.setValue)
        self.hum_spin_box.valueChanged.connect(self.hum_slider.setValue)

        hum_threshold_layout.addWidget(self.hum_threshold_label)
        hum_threshold_layout.addWidget(self.hum_slider)
        hum_threshold_layout.addWidget(self.hum_spin_box)

        # Update button
        self.update_button = QPushButton("Update Thresholds", self)
        self.update_button.clicked.connect(self.update_thresholds)
        self.update_button.setStyleSheet("QPushButton:hover { background-color: #d3d3d3; }")        

        # Creating the table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["🌡 Temperature (°C)", "💧 Humidity (%)"])
        self.table.setStyleSheet("border-radius: 10px;")
        self.temp_slider.setStyleSheet("QSlider::handle:horizontal { border-radius: 5px; }")
        self.table.setStyleSheet("alternate-background-color: #f2f2f2;")
        
        
        

        # Graphics area
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)   
        self.ax.set_facecolor('#f0f4f5')  # Grafik arka planına yumuşak bir renk tonu ekleyin        

        # Layout settings
        layout = QVBoxLayout()
        layout.addLayout(gauge_layout)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.hum_label)
        layout.addWidget(self.warning_label)
        layout.addLayout(temp_threshold_layout)
        layout.addLayout(hum_threshold_layout)
        layout.addWidget(self.update_button)
        layout.addWidget(self.table)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.setWindowTitle("💧 Humidity and 🌡️ Temperature Monitoring System")
        self.setGeometry(100, 100, 600, 800)
        self.setStyleSheet("background-color: #F5F5F5; border: 1px solid #CCC; border-radius: 10px;")
        self.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #e6f7ff, stop:1 #ffffff);")
        
        # Starting animation
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_in_animation()

        # Data update process
        self.update_data()
        
    def fade_in_animation(self):
        if self.windowOpacity() < 1.0:
            self.setWindowOpacity(self.windowOpacity() + 0.1)
            QTimer.singleShot(100, self.fade_in_animation)

    def update_thresholds(self):
        self.current_temp_threshold = self.temp_slider.value()
        self.current_hum_threshold = self.hum_slider.value()
        print(f"New thresholds - Temperature: {self.current_temp_threshold}°C, Humidity: {self.current_hum_threshold}%")

    def update_data(self):
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            if "Temperature" in data:
                temp_str, hum_str = data.split("\t")
                try:
                    # Extract numeric values ​​from string and fix variables
                    hum = float(temp_str.split(": ")[1].split(" ")[0])   # "Humidity
                    temp = float(hum_str.split(": ")[1].split(" ")[0])   # Temperature

                    # Update labels in proper format
                    self.temp_label.setText(f"🌡 Temperature: {temp:.2f} °C")
                    self.hum_label.setText(f"💧 Humidity: {hum:.2f} %")

                    # Threshold control
                    warnings = []
                    if temp < self.current_temp_threshold:
                        warnings.append("Temperature below the limit!")
                    if hum < self.current_hum_threshold:
                        warnings.append("Humidity below the limit!")

                    if warnings:
                        self.warning_label.setText("Warning: " + " ve ".join(warnings))
                        self.warning_label.setStyleSheet("color: red;")
                    else:
                        self.warning_label.setText("")
                        self.warning_label.setStyleSheet("")

                    # Table and graph update
                    self.add_to_table_and_graph(temp, hum)

                except (ValueError, IndexError) as e:
                    print(f"Data reading error: {e}")
                    print(f"Raw data: {data}")  # Print raw data for debugging

        # Periodic update
        QTimer.singleShot(1000, self.update_data)

    def add_to_table_and_graph(self, temp, hum):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Add Temperature and Humidity data to the table
        if temp is not None:
            self.table.setItem(row_position, 0, QTableWidgetItem(f"{temp:.1f} °C"))
            self.temp_data.append(temp)
        else:
            self.table.setItem(row_position, 0, QTableWidgetItem("N/A"))

        if hum is not None:
            self.table.setItem(row_position, 1, QTableWidgetItem(f"{hum:.1f} %"))
            self.hum_data.append(hum)
        else:
            self.table.setItem(row_position, 1, QTableWidgetItem("N/A"))

        # Update chart
        self.ax.clear()
        if len(self.temp_data) > 0:

            # Set Y-axis range
            self.ax.set_ylim([0, max(max(self.temp_data), max(self.hum_data)) + 10])

            # Update x-axis labels
            x_points = list(range(len(self.temp_data)))

            # Draw the lines
            self.ax.plot(x_points, self.temp_data, label="Temperature (°C)", color="red")
            self.ax.plot(x_points, self.hum_data, label="Humidity (%)", color="blue")

            self.ax.legend()
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Value")
            self.ax.grid(True)

        self.canvas.draw()
    def start_warning_animation(self):
        self.warning_blink_timer = QTimer(self)
        self.warning_blink_timer.timeout.connect(self.blink_warning)
        self.blink_state = False
        self.warning_blink_timer.start(500)
    
    def blink_warning(self):
        if self.blink_state:
            self.warning_label.setStyleSheet("color: red;")
        else:
            self.warning_label.setStyleSheet("color: orange;")
        self.blink_state = not self.blink_state
    
    def stop_warning_animation(self):
        if hasattr(self, 'warning_blink_timer'):
            self.warning_blink_timer.stop()
            self.warning_label.setStyleSheet("color: red;")    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TempHumidityApp()
    ex.show()
    sys.exit(app.exec_()) 