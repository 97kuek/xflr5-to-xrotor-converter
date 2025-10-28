# -*- coding: utf-8 -*-

import math
import numpy as np
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ui_aero_section_tab import Ui_section
from logic import AeroLogic
from ui_error_dialog import Ui_error_dialog

class MplCanvas(FigureCanvas):
    """Matplotlib canvas widget."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = fig.add_subplot(121)
        self.axes2 = fig.add_subplot(122)
        super(MplCanvas, self).__init__(fig)
        self.plotted_line1 = None
        self.plotted_scatter1 = None
        self.plotted_scatter2 = None
        self.plotted_line2_1 = None
        self.plotted_line2_2 = None

class ErrorDialog(QtWidgets.QDialog, Ui_error_dialog):
    def __init__(self, *args, obj=None, **kwargs):
        super(ErrorDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

class TabSection(QtWidgets.QWidget, Ui_section):
    """Tab widget for each aerodynamic section."""
    def __init__(self, *args, obj=None, **kwargs):
        super(TabSection, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.aero_logic = AeroLogic()
        self.r_R = 0

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        self.aero_graph.setLayout(layout)

        self.connect_slot()

    def connect_slot(self):
        """Connect signals and slots."""
        self.import_aero_buttom_2.clicked.connect(self.import_polar)
        self.input_aerofile_path_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.zero_lift_alpha_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.dcl_dalpha_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.dcl_dalpha_at_stall_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.max_cl_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.min_cl_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.cl_increment_to_stall_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.min_cd_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.cl_at_min_cd_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.re_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.dcd_ddcl_lineEdit.editingFinished.connect(self.get_line_inputs)
        self.r_R_lineEdit.editingFinished.connect(self.get_line_inputs)

    def import_polar(self):
        """Import polar data from a file."""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open xflr5 polar file', '/home')
        if fname:
            self.input_aerofile_path_lineEdit.setText(fname)
            self.aero_logic.polar_file = fname
            self.calculate_model()

    def calculate_model(self):
        """Calculate the aerodynamic model and update the UI."""
        try:
            self.aero_logic.calculate_model()
            self.set_all_line_inputs()
            self.update_plot()
        except Exception as e:
            dialog = ErrorDialog()
            dialog.error_message.setText(f'error:{e}')
            dialog.exec_()

    def get_line_inputs(self):
        """Get input values from the line edits."""
        sender = self.sender()
        if sender == self.input_aerofile_path_lineEdit:
            self.aero_logic.polar_file = sender.text()
        elif sender == self.zero_lift_alpha_lineEdit:
            self.aero_logic.zero_lift_alpha = self.validate_input(sender.text(), float, sender)
        elif sender == self.dcl_dalpha_lineEdit:
            self.aero_logic.dcl_dalpha = self.validate_input(sender.text(), float, sender)
        elif sender == self.dcl_dalpha_at_stall_lineEdit:
            self.aero_logic.dcl_dalpha_stall = self.validate_input(sender.text(), float, sender)
        elif sender == self.max_cl_lineEdit:
            self.aero_logic.max_cl = self.validate_input(sender.text(), float, sender)
        elif sender == self.min_cl_lineEdit:
            self.aero_logic.min_cl = self.validate_input(sender.text(), float, sender)
        elif sender == self.cl_increment_to_stall_lineEdit:
            self.aero_logic.cl_increment_to_stall = self.validate_input(sender.text(), float, sender)
        elif sender == self.min_cd_lineEdit:
            self.aero_logic.min_cd = self.validate_input(sender.text(), float, sender)
        elif sender == self.cl_at_min_cd_lineEdit:
            self.aero_logic.cl_at_min_cd = self.validate_input(sender.text(), float, sender)
        elif sender == self.re_lineEdit:
            self.aero_logic.re = self.validate_input(sender.text(), float, sender)
        elif sender == self.dcd_ddcl_lineEdit:
            self.aero_logic.dcd_ddcl = self.validate_input(sender.text(), float, sender)
        elif sender == self.r_R_lineEdit:
            self.r_R = self.validate_input(sender.text(), float, sender)
        self.update_plot()

    def validate_input(self, text, type, line_edit):
        """Validate the input text."""
        try:
            return type(text)
        except ValueError:
            line_edit.setText('Error')
            return None

    def set_all_line_inputs(self):
        """Set all line edit widgets with the calculated values."""
        self.input_aerofile_path_lineEdit.setText(self.aero_logic.polar_file)
        self.zero_lift_alpha_lineEdit.setText(f'{self.aero_logic.zero_lift_alpha:.4f}')
        self.dcl_dalpha_lineEdit.setText(f'{self.aero_logic.dcl_dalpha:.4f}')
        self.dcl_dalpha_at_stall_lineEdit.setText(f'{self.aero_logic.dcl_dalpha_stall:.4f}')
        self.max_cl_lineEdit.setText(f'{self.aero_logic.max_cl:.4f}')
        self.min_cl_lineEdit.setText(f'{self.aero_logic.min_cl:.4f}')
        self.cl_increment_to_stall_lineEdit.setText(f'{self.aero_logic.cl_increment_to_stall:.4f}')
        self.min_cd_lineEdit.setText(f'{self.aero_logic.min_cd:.4f}')
        self.cl_at_min_cd_lineEdit.setText(f'{self.aero_logic.cl_at_min_cd:.4f}')
        self.re_lineEdit.setText(f'{self.aero_logic.re:.4f}')
        self.dcd_ddcl_lineEdit.setText(f'{self.aero_logic.dcd_ddcl:.4f}')
        self.r_R_lineEdit.setText(f'{self.r_R:.4f}')

    def update_plot(self):
        """Update the plot with the new data."""
        if self.canvas.plotted_line1 is not None:
            self.canvas.plotted_line1.remove()
        if self.canvas.plotted_line2_1 is not None:
            self.canvas.plotted_line2_1.remove()
        if self.canvas.plotted_line2_2 is not None:
            self.canvas.plotted_line2_2.remove()
        if self.canvas.plotted_scatter1 is not None:
            self.canvas.plotted_scatter1.remove()
        if self.canvas.plotted_scatter2 is not None:
            self.canvas.plotted_scatter2.remove()

        cl_model = np.linspace(self.aero_logic.min_cl, self.aero_logic.max_cl, 100)
        cd_model = [self.aero_logic.min_cd + self.aero_logic.dcd_ddcl * (self.aero_logic.cl_at_min_cd - y) ** 2 for y in cl_model]
        self.canvas.plotted_line1, = self.canvas.axes1.plot(cd_model, cl_model, 'r')
        self.canvas.plotted_scatter1 = self.canvas.axes1.scatter(self.aero_logic.cd_list, self.aero_logic.cl_list, c='b')

        alpha_model = [x for x in np.linspace(self.aero_logic.alpha_list[0], self.aero_logic.alpha_list[-1], 100, endpoint=True)
                       if self.aero_logic.min_cl <= self.aero_logic.dcl_dalpha * (x - self.aero_logic.zero_lift_alpha * math.pi / 180)
                       and self.aero_logic.dcl_dalpha * (x - self.aero_logic.zero_lift_alpha * math.pi / 180) <= self.aero_logic.max_cl]
        cl_model2 = [self.aero_logic.dcl_dalpha * (x - self.aero_logic.zero_lift_alpha * math.pi / 180) for x in alpha_model]
        cl_model_stall = np.linspace(self.aero_logic.max_cl, self.aero_logic.max_cl + self.aero_logic.cl_increment_to_stall, 50)
        alpha_model_stall = [(y - self.aero_logic.max_cl) / self.aero_logic.dcl_dalpha_stall + alpha_model[-1] for y in cl_model_stall]
        self.canvas.plotted_line2_1, = self.canvas.axes2.plot(alpha_model, cl_model2, 'r')
        self.canvas.plotted_line2_2, = self.canvas.axes2.plot(alpha_model_stall, cl_model_stall, 'g')
        self.canvas.plotted_scatter2 = self.canvas.axes2.scatter(self.aero_logic.alpha_list, self.aero_logic.cl_list, c='b')
        self.canvas.draw()
