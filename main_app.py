import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QProgressBar,
    QFrame, QGridLayout, QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

from cleaning import run_cleaning_pipeline
from deduplication import run_chained_classic_dedup, run_chained_fast_dedup
from manual_mapping import apply_manual_mapping

class ProcessingThread(QThread):
    progress = pyqtSignal(str)
    percent = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)

    def __init__(self, df, column):
        super().__init__()
        self.df = df.copy()
        self.column = column

    def run(self):
        try:
            self.progress.emit("Cleaning...")
            self.percent.emit(10)
            cleaned_df = run_cleaning_pipeline(self.df, self.column)

            self.progress.emit("Deduplicating: Classic phase (1/2)...")
            classic_thresholds = 17
            for i in range(classic_thresholds):
                run_chained_classic_dedup(cleaned_df, limit=i+1)
                self.percent.emit(10 + int(20 * (i+1)/classic_thresholds))

            self.progress.emit("Deduplicating: Fast phase (2/2)...")
            fast_thresholds = 6
            for i in range(fast_thresholds):
                run_chained_fast_dedup(cleaned_df, limit=i+1)
                self.percent.emit(50 + int(40 * (i+1)/fast_thresholds))

            self.progress.emit("Applying manual mapping...")
            self.percent.emit(95)
            final_df = apply_manual_mapping(cleaned_df)

            self.progress.emit("Finalizing...")
            self.percent.emit(100)
            self.finished.emit(final_df[["Record Index", "Original_Raw_Addresses", "manual_standardized"]])
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")

class AddressApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Address Cleaner - Professional Edition")
        
        # Updated dimensions for better display
        self.setMinimumSize(750, 650)  # Increased from 600x500
        self.resize(800, 700)          # Increased from 600x500
        
        # Enable maximize button and all window controls
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Optional: Set maximum size to prevent it from becoming too large
        # Comment out or remove the line below if you want unlimited maximize
        # self.setMaximumSize(1200, 900)
        
        self.setStyleSheet(self.get_stylesheet())
        
        # Initialize variables
        self.df = None
        self.init_ui()

    def get_stylesheet(self):
        return """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #e8f4f8, stop:1 #d1e7dd);
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QFrame.card {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e0e6ed;
            margin: 8px;
            padding: 20px;
        }
        
        QFrame.status-card {
            background-color: #d4edda;
            border-radius: 8px;
            border: 1px solid #c3e6cb;
            padding: 12px;
            margin: 5px;
        }
        
        QPushButton.primary {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #17a2b8, stop:1 #138496);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
            min-height: 40px;
        }
        
        QPushButton.primary:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #138496, stop:1 #117a8b);
        }
        
        QPushButton.primary:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #117a8b, stop:1 #0f6674);
        }
        
        QPushButton.success {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #28a745, stop:1 #218838);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
            min-height: 40px;
        }
        
        QPushButton.success:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #218838, stop:1 #1e7e34);
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
            color: #ffffff;
            opacity: 0.7;
        }
        
        QComboBox {
            background-color: white;
            border: 2px solid #ced4da;
            padding: 8px 12px;
            font-size: 14px;
            border-radius: 6px;
            min-height: 25px;
        }
        
        QComboBox:focus {
            border-color: #17a2b8;
        }
        
        QComboBox:disabled {
            background-color: #f8f9fa;
            color: #6c757d;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
            background-color: #17a2b8;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border: 2px solid white;
            width: 0px;
            height: 0px;
            border-top: 4px solid white;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: none;
        }
        
        QProgressBar {
            border: 2px solid #17a2b8;
            text-align: center;
            font-weight: bold;
            background-color: #f8f9fa;
            height: 25px;
            border-radius: 12px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #17a2b8, stop:1 #138496);
            border-radius: 10px;
        }
        
        QLabel.title {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        QLabel.section-title {
            color: #495057;
            font-size: 14px;
            font-weight: bold;
            margin: 8px 0;
        }
        
        QLabel.status {
            color: #155724;
            font-size: 13px;
            font-weight: bold;
        }
        """

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)  # Increased margins slightly

        # Title Card
        title_card = QFrame()
        title_card.setProperty("class", "card")
        title_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e6ed;
                margin: 8px;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon (using text as icon)
        icon_label = QLabel("📋")
        icon_label.setStyleSheet("font-size: 24px; margin-right: 10px;")
        title_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Address Data Cleaner")
        title_label.setStyleSheet("color: #2c3e50; font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addWidget(title_card)

        # Status Card (initially hidden)
        self.status_card = QFrame()
        self.status_card.setStyleSheet("""
            QFrame {
                background-color: #d4edda;
                border-radius: 8px;
                border: 1px solid #c3e6cb;
                padding: 12px;
                margin: 5px;
            }
        """)
        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        check_icon = QLabel("✅")
        check_icon.setStyleSheet("font-size: 16px; margin-right: 8px;")
        status_layout.addWidget(check_icon)
        
        self.status_label = QLabel("Selected: No file selected")
        self.status_label.setStyleSheet("color: #155724; font-size: 13px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.status_card.setVisible(False)
        main_layout.addWidget(self.status_card)

        # Browse File Button
        self.browse_button = QPushButton("🔍 Browse Excel File")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #17a2b8, stop:1 #138496);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #138496, stop:1 #117a8b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #117a8b, stop:1 #0f6674);
            }
        """)
        self.browse_button.clicked.connect(self.load_file)
        main_layout.addWidget(self.browse_button)

        # Column Selection Card
        self.column_card = QFrame()
        self.column_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e6ed;
                margin: 8px;
                padding: 20px;
            }
        """)
        column_layout = QVBoxLayout(self.column_card)
        column_layout.setContentsMargins(20, 15, 20, 15)
        column_layout.setSpacing(12)
        
        # Column selection header
        column_header = QHBoxLayout()
        column_icon = QLabel("📊")
        column_icon.setStyleSheet("font-size: 18px; margin-right: 8px;")
        column_header.addWidget(column_icon)
        
        column_title = QLabel("Select Column to Process:")
        column_title.setStyleSheet("color: #495057; font-size: 14px; font-weight: bold;")
        column_header.addWidget(column_title)
        column_header.addStretch()
        
        column_layout.addLayout(column_header)
        
        # Combo box
        self.column_selector = QComboBox()
        self.column_selector.setEnabled(False)
        self.column_selector.setMinimumHeight(35)  # Ensure combo box has good height
        column_layout.addWidget(self.column_selector)
        
        self.column_card.setVisible(False)
        main_layout.addWidget(self.column_card)

        # Process Button
        self.process_button = QPushButton("✨ CLEAN AND EXPORT ADDRESSES")
        self.process_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #28a745, stop:1 #218838);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-height: 45px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #218838, stop:1 #1e7e34);
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
                opacity: 0.7;
            }
        """)
        self.process_button.clicked.connect(self.process_data)
        self.process_button.setEnabled(False)
        self.process_button.setVisible(False)
        main_layout.addWidget(self.process_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)  # Ensure progress bar has good height
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Progress Status
        self.progress_status = QLabel("")
        self.progress_status.setStyleSheet("color: #495057; font-size: 12px; text-align: center; padding: 10px;")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_status.setVisible(False)
        main_layout.addWidget(self.progress_status)

        # Add stretch to bottom
        main_layout.addStretch()

        self.setLayout(main_layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Excel File", 
            "", 
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                filename = file_path.split('/')[-1]
                
                # Update status
                self.status_label.setText(f"Selected: {filename}")
                self.status_card.setVisible(True)
                
                # Show column selection
                self.column_selector.clear()
                self.column_selector.addItems(self.df.columns)
                self.column_selector.setEnabled(True)
                self.column_card.setVisible(True)
                
                # Show process button
                self.process_button.setEnabled(True)
                self.process_button.setVisible(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def process_data(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load an Excel file first.")
            return

        selected_column = self.column_selector.currentText()
        if not selected_column:
            QMessageBox.warning(self, "Warning", "Please select a column to process.")
            return

        # Update UI for processing
        self.progress_bar.setVisible(True)
        self.progress_status.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_status.setText("Initializing processing...")
        
        # Disable controls
        self.process_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.column_selector.setEnabled(False)
        
        # Update button text
        self.process_button.setText("⏳ Processing...")

        # Start processing thread
        self.thread = ProcessingThread(self.df, selected_column)
        self.thread.progress.connect(self.update_progress_status)
        self.thread.percent.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_processing_finished)
        self.thread.start()

    def update_progress_status(self, message):
        self.progress_status.setText(message)

    def on_processing_finished(self, result_df):
        # Reset UI
        self.progress_bar.setVisible(False)
        self.progress_status.setVisible(False)
        self.process_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.column_selector.setEnabled(True)
        self.process_button.setText("✨ CLEAN AND EXPORT ADDRESSES")

        # Save file dialog
        output_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Standardized Addresses", 
            "standardized_addresses.xlsx", 
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if output_path:
            try:
                result_df.to_excel(output_path, index=False)
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Address standardization completed!\n\nProcessed {len(result_df)} records.\nFile saved to: {output_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Address Cleaner - Professional Edition")
    app.setApplicationVersion("1.0")
    
    window = AddressApp()
    window.show()
    
    sys.exit(app.exec_())