#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit, QShortcut, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import pyqtSlot, QRect
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
import traceback  # better way to handle exceptions
import pathlib
path_of_the_current_file = str(os.path.dirname(os.path.realpath(__file__)))
os.chdir(path_of_the_current_file)
sys.path.append('/afs/ipp/aug/ads-diags/common/python/lib')
sys.path.append(path_of_the_current_file + '/modules')
import my_funcs_class as my_funcs
import ECI_Load_osam as ECI
import TDI_Load_osam as TDI
import EQH_Load_osam as EQH
importlib.reload(TDI)
importlib.reload(ECI)
importlib.reload(EQH)
importlib.reload(my_funcs)


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ECEI_plot'
        self.left = 100
        self.top = 100
        self.width = 1400
        self.height = 900
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tabs ----------------------------------
        self.tabs = QTabWidget()
        self.Load_data = QWidget()  # create tab 1
        self.SettRzPlot_tab = QWidget()   # create tab 2
        self.Rz_tab = QWidget()   # create tab 3
        self.tabs.resize(300, 200)

        # Add tabs to the Main WIndow
        self.tabs.addTab(self.Load_data, "Load data")  # tab 1
        self.tabs.addTab(self.SettRzPlot_tab, "Rz plot Settings")     # tab 2
        self.tabs.addTab(self.Rz_tab, "Rz plot")     # tab 3

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.show()
        # ----------------------------------------------------------------------------------

        # Load_data tab - content
        self.data_loaded = False
        layout_load = QtWidgets.QVBoxLayout(self.Load_data)  # main layout
        sublayout_load = QtWidgets.QGridLayout()  # layout for inputs
        layout_load.addLayout(sublayout_load)

        # Input widgets
        # Shot
        self.Shot_lbl_load = QLabel(self.Load_data)
        self.Shot_lbl_load.setText('Shot # ')
        self.Shot_ed_load = QLineEdit(self.Load_data)
        self.Shot_ed_load.setText('25781')
        # Diag
        self.Diag_lbl_load = QLabel(self.Load_data)
        self.Diag_lbl_load.setText('Diag: ')
        self.Diag_load = QComboBox(self.Load_data)
        self.Diag_load.addItems(['ECI', 'TDI'])
        self.Diag_lbl_EQ_load = QLabel(self.Load_data)
        self.Diag_lbl_EQ_load.setText('Equilibrium: ')
        self.Diag_EQ_load = QComboBox(self.Load_data)
        self.Diag_EQ_load.addItems(['EQH'])
        # Load button
        self.Butt_load = QPushButton("Load ECEI and equilibrium data",
                                     self.Load_data)
        self.Butt_load.clicked.connect(self.Load_ECEI_data)
        # Monitor
        self.Monitor_load = QtWidgets.QTextBrowser(self.Load_data)
        self.Monitor_load.setText("Status:\nECEI data is not loaded")

        # Add widgets to layout
        sublayout_load.setSpacing(5)
        sublayout_load.addWidget(self.Shot_lbl_load, 0, 0)
        sublayout_load.addWidget(self.Diag_lbl_load, 1, 0)
        sublayout_load.addWidget(self.Diag_lbl_EQ_load, 2, 0)
        sublayout_load.addWidget(self.Shot_ed_load, 0, 1)
        sublayout_load.addWidget(self.Diag_load, 1, 1)
        sublayout_load.addWidget(self.Diag_EQ_load, 2, 1)
        sublayout_load.addWidget(self.Butt_load, 3, 1)

        sublayout_2_load = QtWidgets.QGridLayout()  # layout for inputs
        layout_load.addLayout(sublayout_2_load)
        sublayout_2_load.addWidget(self.Monitor_load, 1, 0)

        # stretch free space (compress widgets at the top)
        layout_load.addStretch()

# ----------------------------------------------------------------------------------
        # Rz plot tab - content
        # Create layouts
        layout_RzPl = QtWidgets.QVBoxLayout(self.Rz_tab)  # main layout
        sublayout_RzPl = QtWidgets.QGridLayout()  # layout for inputs
        layout_RzPl.addLayout(sublayout_RzPl)

        # Input widgets
        # labels
        self.tB_lbl_RzPl = QLabel(self.Rz_tab)
        self.tB_lbl_RzPl.setText('tB [s]:')
        self.tE_lbl_RzPl = QLabel(self.Rz_tab)
        self.tE_lbl_RzPl.setText('tE [s]:')
        self.tCnt_lbl_RzPl = QLabel(self.Rz_tab)
        self.tCnt_lbl_RzPl.setText('tCenter [s] (optional):')
        self.dt_lbl_RzPl = QLabel(self.Rz_tab)
        self.dt_lbl_RzPl.setText('dt [s](optional) :')
        # filter labels
        self.Fourier_lbl0_RzPl = QLabel(self.Rz_tab)
        self.Fourier_lbl0_RzPl.setText('Fourier lowpass f [kHz]:')
        self.Fourier2_lbl0_RzPl = QLabel(self.Rz_tab)
        self.Fourier2_lbl0_RzPl.setText('Fourier highpass f [kHz]:')
        self.SavGol_lbl0_RzPl = QLabel(self.Rz_tab)
        self.SavGol_lbl0_RzPl.setText('SavGol win_len:')
        self.SavGol_lbl1_RzPl = QLabel(self.Rz_tab)
        self.SavGol_lbl1_RzPl.setText('SavGol pol_ord:')
        self.Binning_lbl_RzPl = QLabel(self.Rz_tab)
        self.Binning_lbl_RzPl.setText('Binning [kHz]:')
        self.Contour_lbl_RzPl = QLabel(self.Rz_tab)
        self.Contour_lbl_RzPl.setText('Contour [1 or 0]')
        self.NNcont_lbl_RzPl = QLabel(self.Rz_tab)
        self.NNcont_lbl_RzPl.setText('NNcont:')
        self.tplot_lbl_RzPl = QLabel(self.Rz_tab)
        self.tplot_lbl_RzPl.setText('t_plot [s](within tB and tE):')
        self.dtplot_lbl_RzPl = QLabel(self.Rz_tab)
        self.dtplot_lbl_RzPl.setText('dt_plot [s]:')
        self.FourMult_lbl_RzPl = QLabel(self.Rz_tab)
        self.FourMult_lbl_RzPl.setText('Fourier multiple f [kHz]:')

        # plot params labels
        self.vmin_lbl_RzPl = QLabel(self.Rz_tab)
        self.vmin_lbl_RzPl.setText('vmin:')
        self.vmax_lbl_RzPl = QLabel(self.Rz_tab)
        self.vmax_lbl_RzPl.setText('vmax:')
        self.chzz_lbl_RzPl = QLabel(self.Rz_tab)
        self.chzz_lbl_RzPl.setText('Remove LOS:')
        self.chRR_lbl_RzPl = QLabel(self.Rz_tab)
        self.chRR_lbl_RzPl.setText('Remove R chs:')

        # line edits
        # time edits
        self.tB_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tB_ed_RzPl.setText('4.488525')
        self.tB_ed_RzPl.setMinimumSize(QtCore.QSize(55, 0))
        self.tE_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tE_ed_RzPl.setText('4.489525')
        self.tE_ed_RzPl.setMinimumSize(QtCore.QSize(55, 0))
        self.tCnt_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tCnt_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.dt_ed_RzPl = QLineEdit(self.Rz_tab)
        self.dt_ed_RzPl.setText('0.001')
        self.dt_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        self.Butt_dt_RzPl = QPushButton("Calc t", self.Rz_tab)
        self.Butt_dt_RzPl.clicked.connect(lambda: self.tBE_from_tCnt(9))
        # plot params edits
        self.vmin_ed_RzPl = QLineEdit(self.Rz_tab)
        self.vmin_ed_RzPl.setText('None')
        self.vmin_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.vmax_ed_RzPl = QLineEdit(self.Rz_tab)
        self.vmax_ed_RzPl.setText('None')
        self.vmax_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.chzz_ed_RzPl = QLineEdit(self.Rz_tab)
        self.chzz_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        self.chRR_ed_RzPl = QLineEdit(self.Rz_tab)
        self.chRR_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))
        # Filters edits
        self.Fourier_cut_RzPl = QLineEdit(self.Rz_tab)
        self.Fourier_cut_RzPl.setText('30.0')
        self.Fourier2_cut_RzPl = QLineEdit(self.Rz_tab)
        self.Fourier2_cut_RzPl.setText('2.0')
        self.SavGol_ed0_RzPl = QLineEdit(self.Rz_tab)
        self.SavGol_ed0_RzPl.setText('11')
        self.SavGol_ed0_RzPl.setMinimumSize(QtCore.QSize(20, 0))
        self.SavGol_ed1_RzPl = QLineEdit(self.Rz_tab)
        self.SavGol_ed1_RzPl.setText('3')
        self.Binning_ed_RzPl = QLineEdit(self.Rz_tab)
        self.Binning_ed_RzPl.setText('60.0')
        self.Binning_ed_RzPl.setMinimumSize(QtCore.QSize(40, 0))
        self.Contour_ed_RzPl = QLineEdit(self.Rz_tab)
        self.Contour_ed_RzPl.setText('0')
        self.NNcont_ed_RzPl = QLineEdit(self.Rz_tab)
        self.NNcont_ed_RzPl.setText('60')
        self.tplot_ed_RzPl = QLineEdit(self.Rz_tab)
        self.tplot_ed_RzPl.setText('4.488550')
        self.tplot_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.dtplot_ed_RzPl = QLineEdit(self.Rz_tab)
        self.dtplot_ed_RzPl.setText('5.0e-6')
        self.dtplot_ed_RzPl.setMinimumSize(QtCore.QSize(50, 0))
        self.FourMult_ed_RzPl = QLineEdit(self.Rz_tab)
        self.FourMult_ed_RzPl.setText('13.0,15.0;26,30')
        self.FourMult_ed_RzPl.setMinimumSize(QtCore.QSize(100, 0))

        # what to plot (type of filter)
        self.ImgType_plot_RzPl = QComboBox(self.Rz_tab)
        self.ImgType_plot_RzPl.addItems(
            ['no Image filter', 'Gaussian', 'Median', 'Bilateral', 'Conservative_smoothing'])
        self.type_plot_RzPl = QComboBox(self.Rz_tab)
        self.type_plot_RzPl.addItems(['no 1D filter',
                                      'Fourier highpass',
                                      'Fourier lowpass',
                                      'Fourier both',
                                      'Fourier multiple',
                                      'SavGol',
                                      'Binning'])
        self.Interp_plot_RzPl = QComboBox(self.Rz_tab)
        self.Interp_plot_RzPl.addItems(
            ['no interpolation', 'with interpolation', 'set to zero'])
        # self.Interp_plot_RzPl.setMaximumSize(QtCore.QSize(90, 0))
        self.Save_plot_RzPl = QComboBox(self.Rz_tab)
        self.Save_plot_RzPl.addItems(
            ['do not save', 'save as pdf', 'save as png'])
        # plot buttom
        self.MinusTplot_butt_RzPl = QPushButton("< -dt", self.Rz_tab)
        self.PlusTplot_butt_RzPl = QPushButton("+dt >", self.Rz_tab)
        self.tplot_butt_RzPl = QPushButton("plot time", self.Rz_tab)
        self.MinusTplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(1))
        self.PlusTplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(2))
        self.tplot_butt_RzPl.clicked.connect(lambda: self.f_Rz_plot(3))

        # Shortcuts
        shortcut_plot_Rz = QShortcut(QKeySequence("Ctrl+p"),
                                     self.tplot_butt_RzPl)
        shortcut_plot_Rz.activated.connect(lambda: self.f_Rz_plot(3))
        shortcut_plot_Rz.setEnabled(True)

        shortcut_next_Rz = QShortcut(QKeySequence("Ctrl+j"),
                                     self.PlusTplot_butt_RzPl)
        shortcut_next_Rz.activated.connect(lambda: self.f_Rz_plot(2))
        shortcut_next_Rz.setEnabled(True)

        shortcut_prev_Rz = QShortcut(QKeySequence("Ctrl+k"),
                                     self.MinusTplot_butt_RzPl)
        shortcut_prev_Rz.activated.connect(lambda: self.f_Rz_plot(1))
        shortcut_prev_Rz.setEnabled(True)

        shortcut_tC_Rz = QShortcut(QKeySequence("Ctrl+t"),
                                   self.Butt_dt_RzPl)
        shortcut_tC_Rz.activated.connect(lambda: self.tBE_from_tCnt(9))
        shortcut_tC_Rz.setEnabled(True)
        # Add widgets to layout
        # First row
        sublayout_RzPl.setSpacing(2)
        sublayout_RzPl.addWidget(self.tB_lbl_RzPl, 0, 0)
        sublayout_RzPl.addWidget(self.tB_ed_RzPl, 0, 1)
        sublayout_RzPl.addWidget(self.tE_lbl_RzPl, 0, 2)
        sublayout_RzPl.addWidget(self.tE_ed_RzPl, 0, 3)
        sublayout_RzPl.addWidget(self.tCnt_lbl_RzPl, 0, 4)
        sublayout_RzPl.addWidget(self.tCnt_ed_RzPl, 0, 5)
        sublayout_RzPl.addWidget(self.dt_lbl_RzPl, 0, 6)
        sublayout_RzPl.addWidget(self.dt_ed_RzPl, 0, 7)
        sublayout_RzPl.addWidget(self.Butt_dt_RzPl, 0, 8)
        # Second row
        sublayout_RzPl.addWidget(self.Fourier2_lbl0_RzPl, 1, 0)
        sublayout_RzPl.addWidget(self.Fourier2_cut_RzPl, 1, 1)
        sublayout_RzPl.addWidget(self.Fourier_lbl0_RzPl, 1, 2)
        sublayout_RzPl.addWidget(self.Fourier_cut_RzPl, 1, 3)
        sublayout_RzPl.addWidget(self.FourMult_lbl_RzPl, 1, 4)
        sublayout_RzPl.addWidget(self.FourMult_ed_RzPl, 1, 5)
        ######
        sublayout_RzPl.addWidget(self.SavGol_lbl0_RzPl, 1, 6)
        sublayout_RzPl.addWidget(self.SavGol_ed0_RzPl, 1, 7)
        sublayout_RzPl.addWidget(self.SavGol_lbl1_RzPl, 1, 8)
        sublayout_RzPl.addWidget(self.SavGol_ed1_RzPl, 1, 9)
        sublayout_RzPl.addWidget(self.Binning_lbl_RzPl, 1, 10)
        sublayout_RzPl.addWidget(self.Binning_ed_RzPl, 1, 11)
        ######
        sublayout_RzPl.addWidget(self.chzz_lbl_RzPl, 2, 0)
        sublayout_RzPl.addWidget(self.chzz_ed_RzPl, 2, 1)
        sublayout_RzPl.addWidget(self.chRR_lbl_RzPl, 2, 2)
        sublayout_RzPl.addWidget(self.chRR_ed_RzPl, 2, 3)
        ######
        sublayout_RzPl.addWidget(self.vmin_lbl_RzPl, 2, 4)
        sublayout_RzPl.addWidget(self.vmin_ed_RzPl, 2, 5)
        sublayout_RzPl.addWidget(self.vmax_lbl_RzPl, 2, 6)
        sublayout_RzPl.addWidget(self.vmax_ed_RzPl, 2, 7)
        sublayout_RzPl.addWidget(self.Contour_lbl_RzPl, 2, 8)
        sublayout_RzPl.addWidget(self.Contour_ed_RzPl, 2, 9)
        sublayout_RzPl.addWidget(self.NNcont_lbl_RzPl, 2, 10)
        sublayout_RzPl.addWidget(self.NNcont_ed_RzPl, 2, 11)
        #####
        ######
        # Third row
        sublayout_RzPl.addWidget(self.tplot_lbl_RzPl, 3, 0)
        sublayout_RzPl.addWidget(self.tplot_ed_RzPl, 3, 1)
        sublayout_RzPl.addWidget(self.dtplot_lbl_RzPl, 3, 2)
        sublayout_RzPl.addWidget(self.dtplot_ed_RzPl, 3, 3)
        # Plot control
        sublayout_RzPl.addWidget(self.ImgType_plot_RzPl, 1, 12)
        sublayout_RzPl.addWidget(self.type_plot_RzPl, 2, 12)
        sublayout_RzPl.addWidget(self.Save_plot_RzPl, 3, 7)
        # sublayout_RzPl.addWidget(self.Info2_lbl_RzPl, 3, 8)
        sublayout_RzPl.addWidget(self.Interp_plot_RzPl, 3, 8)
        sublayout_RzPl.addWidget(self.MinusTplot_butt_RzPl, 3, 10)
        sublayout_RzPl.addWidget(self.PlusTplot_butt_RzPl, 3, 11)
        sublayout_RzPl.addWidget(self.tplot_butt_RzPl, 3, 12)

        # Add matplotlib plot
        self.figure_RzPl = Figure(figsize=(5, 3), constrained_layout=False)
        self.static_canvas_RzPl = FigureCanvas(self.figure_RzPl)
        layout_RzPl.addWidget(
            self.static_canvas_RzPl,
            QtCore.Qt.AlignTop)  # align the plot up
        layout_RzPl.addStretch()  # stretch plot in all free space
        self.toolbar = NavigationToolbar(
            self.static_canvas_RzPl,
            self.Rz_tab,
            coordinates=True)  # add toolbar below the plot
        layout_RzPl.addWidget(self.toolbar)
        self._static_ax = self.static_canvas_RzPl.figure.subplots()  # add axes


# ----------------------------------------------------------------------------------
        # SettRz tab - content
        # Create layouts
        layout_RzSet = QtWidgets.QVBoxLayout(
            self.SettRzPlot_tab)  # main layout
        sublayout_RzSet = QtWidgets.QGridLayout()  # layout for inputs
        layout_RzSet.addLayout(sublayout_RzSet)

        # Input widgets
        # labels
        self.one_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.one_lbl_RzSet.setText('Gaussian filter:')
        self.two_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.two_lbl_RzSet.setText('Median filter:')
        self.three_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.three_lbl_RzSet.setText('Bilateral filter:')
        self.four_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.four_lbl_RzSet.setText('Conservative smoothing filter:')
        # filters parameters
        self.BilKernSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilKernSize_lbl_RzSet.setText('Kernel size:')
        self.BilS0_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilS0_lbl_RzSet.setText('s0:')
        self.BilS1_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.BilS1_lbl_RzSet.setText('s1:')
        self.MedKernSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.MedKernSize_lbl_RzSet.setText('Kernel size:')
        self.ConsSize_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.ConsSize_lbl_RzSet.setText('Neighborhood size:')
        self.GausSigma_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.GausSigma_lbl_RzSet.setText('sigma:')

        # Line edits (inputs)
        self.GausSigma_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.GausSigma_ed_RzSet.setText('1.0')
        self.BilKern_type_RzSet = QComboBox(self.SettRzPlot_tab)
        self.BilKern_type_RzSet.addItems(['disk', 'square'])
        self.BilKernSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilKernSize_ed_RzSet.setText('1')
        self.BilS0_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilS0_ed_RzSet.setText('100')
        self.BilS1_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.BilS1_ed_RzSet.setText('100')

        self.MedKern_type_RzSet = QComboBox(self.SettRzPlot_tab)
        self.MedKern_type_RzSet.addItems(['disk', 'square'])
        self.MedKernSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.MedKernSize_ed_RzSet.setText('1')
        self.ConsSize_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.ConsSize_ed_RzSet.setText('2')

        sublayout_RzSet.setSpacing(2)
        # First row
        sublayout_RzSet.addWidget(self.one_lbl_RzSet, 0, 0)
        sublayout_RzSet.addWidget(self.GausSigma_lbl_RzSet, 0, 2)
        sublayout_RzSet.addWidget(self.GausSigma_ed_RzSet, 0, 3)
        # Second row
        sublayout_RzSet.addWidget(self.two_lbl_RzSet, 1, 0)
        sublayout_RzSet.addWidget(self.MedKern_type_RzSet, 1, 1)
        sublayout_RzSet.addWidget(self.MedKernSize_lbl_RzSet, 1, 2)
        sublayout_RzSet.addWidget(self.MedKernSize_ed_RzSet, 1, 3)
        # Third row
        sublayout_RzSet.addWidget(self.three_lbl_RzSet, 2, 0)
        sublayout_RzSet.addWidget(self.BilKern_type_RzSet, 2, 1)
        sublayout_RzSet.addWidget(self.BilKernSize_lbl_RzSet, 2, 2)
        sublayout_RzSet.addWidget(self.BilKernSize_ed_RzSet, 2, 3)
        sublayout_RzSet.addWidget(self.BilS0_lbl_RzSet, 2, 4)
        sublayout_RzSet.addWidget(self.BilS0_ed_RzSet, 2, 5)
        sublayout_RzSet.addWidget(self.BilS1_lbl_RzSet, 2, 6)
        sublayout_RzSet.addWidget(self.BilS1_ed_RzSet, 2, 7)
        # Fourth row
        sublayout_RzSet.addWidget(self.four_lbl_RzSet, 3, 0)
        sublayout_RzSet.addWidget(self.ConsSize_lbl_RzSet, 3, 2)
        sublayout_RzSet.addWidget(self.ConsSize_ed_RzSet, 3, 3)

        sublayout1_RzSet = QtWidgets.QVBoxLayout()  # one more layout for title
        layout_RzSet.addLayout(sublayout1_RzSet)

        self.Info1_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.Info1_lbl_RzSet.setText(
            '====== Matrix for interpolation (scipy.interpolate.interp2d, type = cubic) or "set to zero" options ======')
        sublayout1_RzSet.addWidget(self.Info1_lbl_RzSet)

        sublayout2_RzSet = QtWidgets.QGridLayout()  # one more layout for interpolation
        layout_RzSet.addLayout(sublayout2_RzSet)

        LOSlabels = {}
        self.LOSlabels = {}
        for i_L in range(20):
            LOSlabels['%d' % (i_L)] = (i_L, 0)
        for sText, pos in LOSlabels.items():
            # QLabels
            self.LOSlabels[sText] = QLabel("LOS: %d" % (int(sText) + 1))
            sublayout2_RzSet.addWidget(
                self.LOSlabels[sText], pos[0] + 1, pos[1])

        checks = {}
        self.checks = {}
        for i_L in range(20):
            for i_R in range(8):
                checks['%d,%d' % (i_L, i_R)] = (i_L, i_R)
        for sText, pos in checks.items():
            # QCheckBoxes
            self.checks[sText] = QCheckBox("%d,%d" % (pos[0] + 1, pos[1] + 1))
            sublayout2_RzSet.addWidget(
                self.checks[sText], pos[0] + 1, pos[1] + 1)
        sublayout2_RzSet.setSpacing(2)

        sublayout3_RzSet = QtWidgets.QHBoxLayout()  # one more layout for path
        layout_RzSet.addLayout(sublayout3_RzSet)

        self.path_lbl_RzSet = QLabel(self.SettRzPlot_tab)
        self.path_lbl_RzSet.setText(
            'Path to save Rz plots (path should end with "/" symbol):')

        self.path_ed_RzSet = QLineEdit(self.SettRzPlot_tab)
        self.path_ed_RzSet.setText('/afs/ipp/home/o/osam/Documents/output/')
        sublayout3_RzSet.addWidget(self.path_lbl_RzSet)
        sublayout3_RzSet.addWidget(self.path_ed_RzSet)

        layout_RzSet.addStretch()  # stretch free space (compress widgets at the top)
# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
    # ---------------METHODS-------------


    def tBE_from_tCnt(self, number):
        try:
            if (number == 9):
                t = float(self.tCnt_ed_RzPl.text())
                dt = float(self.dt_ed_RzPl.text())
                tB = t - dt / 2.0
                tE = t + dt / 2.0
                self.tB_ed_RzPl.setText('%0.7g' % (tB))
                self.tE_ed_RzPl.setText('%0.7g' % (tE))
                self.tplot_ed_RzPl.setText('%0.7g' % (np.mean([tB, tE])))
                self.f_Rz_plot(3)

        except Exception as exc:
            print("!!! Incorrect input. ERROR: %s" % (exc))
        pass

    def Load_ECEI_data(self):
        try:
            self.Shot = int(self.Shot_ed_load.text())
            self.Diag = self.Diag_load.currentText()
            self.Diag_EQ = self.Diag_EQ_load.currentText()
            self.Monitor_load.setText(
                "Status:\nLoading %s: #%d ... " %
                (self.Diag, self.Shot))
            allow_to_load = True
        except Exception as exc:
            print("!!! Incorrect input. ERROR: %s" % (exc))
            self.Monitor_load.setText("Status:\nPlease enter shot number.")
            allow_to_load = False

        if (self.Diag_EQ == 'EQH') & (allow_to_load):
            try:
                # load EQH
                self.Monitor_load.setText("")
                EQ = EQH.EQH()
                EQ.Load(self.Shot)
                self.Monitor_load.insertPlainText("EQH data has been loaded succesfully.\n")
            except Exception as exc:
                traceback.print_exc()
                print("!!! Coudn't load EQH. ERROR: %s" % (exc))
                self.Monitor_load.setText(
                    "Status:\nError in loading ECI data.")
                self.Monitor_load.insertPlainText("!!! EQH data NOT loaded.")
                print("+++ EQH has been loaded +++")

        if (self.Diag == 'TDI') & (allow_to_load):
            try:
                TD = TDI.TDI()
                TD.Load(self.Shot)
                TD.Load_FakeRz()
                self.ECEId = TD.ECEId.copy()
                self.ECEId_time = TD.time.copy()
                self.ECEId_RR = TD.RR_fake.copy()
                self.ECEId_zz = TD.zz_fake.copy()
                self.ECEId_R = TD.R_fake.copy()
                self.ECEId_z = TD.z_fake.copy()
                self.Monitor_load.insertPlainText("Status:\nTDI #%d\ntB = %g, tE = %g s\nLoaded succesfully." % (
                    self.Shot, TD.time[0], TD.time[-1]))

                self.data_loaded = True
                print("+++ The data has been loaded succesfully. +++")
            except Exception as exc:
                print("!!! Coudn't load TDI. ERROR: %s" % (exc))
                self.Monitor_load.insertPlainText(
                    "Status:\nError in loading ECI data.")

        if (self.Diag == 'ECI') & (allow_to_load):
            try:
                EI = ECI.ECI()
                EI.Load(self.Shot)
                EI.Load_FakeRz()
                self.ECEId = EI.ECEId.copy()
                self.ECEId_time = EI.time.copy()
                self.ECEId_RR = EI.RR_fake.copy()
                self.ECEId_zz = EI.zz_fake.copy()
                self.ECEId_R = EI.R_fake.copy()
                self.ECEId_z = EI.z_fake.copy()
                self.Monitor_load.insertPlainText("Status:\nECI #%d\ntB = %g, tE = %g s\nLoaded succesfully." % (
                    self.Shot, EI.time[0], EI.time[-1]))
                self.data_loaded = True
                print("+++ The data has been loaded succesfully. +++")
            except Exception as exc:
                print("!!! Coudn't load ECI. ERROR: %s" % (exc))
                self.Monitor_load.insertPlainText(
                    "Status:\nError in loading ECI data.")





    def f_Rz_plot(self, which_plot):
        if (self.data_loaded):  # check whether ECEI data is loaded
            try:
                import matplotlib.pyplot as plt
                plt.rcParams.update({'font.size': 10})
                # data preparation
                self.tB_ed_RzPl
                tB = float(self.tB_ed_RzPl.text())
                tE = float(self.tE_ed_RzPl.text())
                if (which_plot == 1):
                    tplot_old = float(self.tplot_ed_RzPl.text())
                    dtplot = float(self.dtplot_ed_RzPl.text())
                    tplot = tplot_old - dtplot
                    self.tplot_ed_RzPl.setText("%0.7g" % tplot)
                if (which_plot == 2):
                    tplot_old = float(self.tplot_ed_RzPl.text())
                    dtplot = float(self.dtplot_ed_RzPl.text())
                    tplot = tplot_old + dtplot
                    self.tplot_ed_RzPl.setText("%0.7g" % tplot)
                if (which_plot == 3):
                    tplot = float(self.tplot_ed_RzPl.text())
                    self.counter_save = 0

                dtplot = float(self.dtplot_ed_RzPl.text())
                contour_check = self.Contour_ed_RzPl.text()
                mf = my_funcs.my_funcs()
                mf.CutDataECEI(self.ECEId_time, self.ECEId, tBegin=tB, tEnd=tE)
                mf.relECEI(mf.ECEId_C)
                time_plot, data_plot = mf.time_C, mf.ECEId_rel
                
                filter_status = "None"

                if (self.type_plot_RzPl.currentText() == 'Fourier lowpass'):
                    f_cut = float(self.Fourier_cut_RzPl.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier lowpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier highpass'):
                    f_cut = float(self.Fourier2_cut_RzPl.text()) * 1.0e3
                    noise_ampl = 1.0
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl, f_cut)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier highpass, freq_cut = %g kHz" % (
                        f_cut * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier both'):
                    f_cut_lp = float(self.Fourier_cut_RzPl.text()) * 1.0e3
                    noise_ampl_lp = 1.0
                    f_cut_hp = float(self.Fourier2_cut_RzPl.text()) * 1.0e3
                    noise_ampl_hp = 1.0
                    mf.Fourier_analysis_ECEI_lowpass(
                        time_plot, data_plot, noise_ampl_lp, f_cut_lp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    mf.Fourier_analysis_ECEI_highpass(
                        time_plot, data_plot, noise_ampl_hp, f_cut_hp)
                    data_plot = mf.ECEId_fft_f_ifft.copy()
                    filter_status = "Fourier high and low pass, freq_cut_hp = %g kHz, freq_cut_lp = %g kHz" % (
                        f_cut_hp * 1.0e-3, f_cut_lp * 1.0e-3)

                if (self.type_plot_RzPl.currentText() == 'Fourier multiple'):
                    string = self.FourMult_ed_RzPl.text()
                    freq_num = len(string.split(";"))
                    f_hp = np.zeros(freq_num)
                    f_lp = np.zeros(freq_num)
                    for i in range(freq_num):
                        f_hp[i] = string.split(";")[i].split(",")[0]
                        f_hp[i] *= 1.0e3
                        f_lp[i] = string.split(";")[i].split(",")[1]
                        f_lp[i] *= 1.0e3
                    mf.Fourier_analysis_ECEI_multiple(
                        time_plot, data_plot, f_hp, f_lp)
                    data_plot = mf.ECEId_fft_f_ifft
                    filter_status = "Fourier multiple, freqs: %s kHz" % (
                        string)

                if (self.type_plot_RzPl.currentText() == 'SavGol'):
                    win_len = int(self.SavGol_ed0_RzPl.text())
                    pol_ord = int(self.SavGol_ed1_RzPl.text())
                    mf.SavGol_filter_ECEI(data_plot, win_len, pol_ord)
                    data_plot = mf.ECEId_savgol
                    filter_status = "Savgol, win_len = %g, pol_ord = %g" % (
                        win_len, pol_ord)

                if (self.type_plot_RzPl.currentText() == 'Binning'):
                    binning_freq = float(self.Binning_ed_RzPl.text())
                    time_plot, data_plot = mf.dataBinningECEI(
                        time_plot, data_plot, binning_freq)
                    filter_status = "Binning, freq = %g kHz" % (binning_freq)

                RR_plot, zz_plot = self.ECEId_RR, self.ECEId_zz

                removeLOS_ch = self.chzz_ed_RzPl.text()
                if removeLOS_ch:
                    removeLOS_ch = np.array(
                        self.chzz_ed_RzPl.text().split(','))
                    removeLOS_ch = removeLOS_ch.astype(int) - 1
                else:
                    removeLOS_ch = []
                removeRR_ch = self.chRR_ed_RzPl.text()
                if removeRR_ch:
                    removeRR_ch = np.array(self.chRR_ed_RzPl.text().split(','))
                    removeRR_ch = removeRR_ch.astype(int) - 1
                else:
                    removeRR_ch = []

                NN_LOS, NN_R = data_plot.shape[1], data_plot.shape[2]
                ch_zz = np.arange(NN_LOS)
                ch_zz = np.delete(ch_zz, removeLOS_ch)
                ch_RR = np.arange(NN_R)
                ch_RR = np.delete(ch_RR, removeRR_ch)

                trace_1D = data_plot[:, 6, 3]
                # remove channels
                RR_plot = np.delete(RR_plot, removeLOS_ch, axis=0)
                RR_plot = np.delete(RR_plot, removeRR_ch, axis=1)
                zz_plot = np.delete(zz_plot, removeLOS_ch, axis=0)
                zz_plot = np.delete(zz_plot, removeRR_ch, axis=1)
                data_plot = np.delete(data_plot, removeLOS_ch, axis=1)
                data_plot = np.delete(data_plot, removeRR_ch, axis=2)

                check_vmin_vmax = 0
                if (self.vmin_ed_RzPl.text().replace(
                        '-', '', 1).replace('.', '', 1).isdigit()):
                    vmin = float(self.vmin_ed_RzPl.text())
                    check_vmin_vmax = 1
                else:
                    vmin = None

                if (self.vmax_ed_RzPl.text().replace('.', '', 1).isdigit()):
                    vmax = float(self.vmax_ed_RzPl.text())
                    check_vmin_vmax = 1
                else:
                    vmax = None

                if (self.NNcont_ed_RzPl.text().replace('.', '', 1).isdigit()):
                    NN_cont = int(self.NNcont_ed_RzPl.text())
                else:
                    NN_cont = 20

                # find time index of plot
                idx_tplot = mf.find_nearest_idx(time_plot, tplot)
                time_plot_t, data_plot_t = time_plot[idx_tplot], data_plot[idx_tplot, :, :]

                if (self.Interp_plot_RzPl.currentText() == 'with interpolation'):
                    interp_mask = np.full((NN_LOS, NN_R), False)
                    for i_L in range(NN_LOS):
                        for i_R in range(NN_R):
                            interp_mask[i_L, i_R] = self.checks['%d,%d' % (
                                i_L, i_R)].isChecked()

                    interp_mask = np.delete(interp_mask, removeLOS_ch, axis=0)
                    interp_mask = np.delete(interp_mask, removeRR_ch, axis=1)
                    data_to_interp = data_plot_t.copy()
                    data_to_interp[interp_mask] = np.NaN
                    data_plot_t = mf.nan_interp_2d(data_to_interp)

                if (self.Interp_plot_RzPl.currentText() == 'set to zero'):
                    interp_mask = np.full((NN_LOS, NN_R), False)
                    for i_L in range(NN_LOS):
                        for i_R in range(NN_R):
                            interp_mask[i_L, i_R] = self.checks['%d,%d' % (
                                i_L, i_R)].isChecked()

                    interp_mask = np.delete(interp_mask, removeLOS_ch, axis=0)
                    interp_mask = np.delete(interp_mask, removeRR_ch, axis=1)
                    data_plot_t[interp_mask] = 0.0

                if (self.ImgType_plot_RzPl.currentText() == 'Gaussian'):
                    sigma = float(self.GausSigma_ed_RzSet.text())
                    data_plot_t = mf.gaussian_filter(data_plot_t, sigma)
                    filter_status += "; Img filt: Gaussian, sigma=%g" % (sigma)

                if (self.ImgType_plot_RzPl.currentText() == 'Bilateral'):
                    kernel = self.BilKern_type_RzSet.currentText()
                    kern_size = int(self.BilKernSize_ed_RzSet.text())
                    s0 = int(self.BilS0_ed_RzSet.text())
                    s1 = int(self.BilS1_ed_RzSet.text())
                    data_plot_t = mf.bilateral_filter(
                        data_plot_t, kernel, kern_size, s0, s1)
                    filter_status += "; Img filt: Bilateral, %s, kern_size=%g, s0=%g, s1=%g" % (
                        kernel, kern_size, s0, s1)

                if (self.ImgType_plot_RzPl.currentText() == 'Median'):
                    kernel = self.MedKern_type_RzSet.currentText()
                    kern_size = int(self.MedKernSize_ed_RzSet.text())
                    data_plot_t = mf.median_filter(
                        data_plot_t, kernel, kern_size)
                    filter_status += "; Img filt: Median, %s, kern_size=%g" % (
                        kernel, kern_size)

                if (self.ImgType_plot_RzPl.currentText()
                        == 'Conservative_smoothing'):
                    size_filt = int(self.ConsSize_ed_RzSet.text())
                    data_plot_t = mf.conservative_smoothing_filter(
                        data_plot_t, size_filt)
                    filter_status += "; Img filt: Conservative smoothing, filt_size=%g" % (
                        size_filt)

                # plotting
                # initiate plot
                self.figure_RzPl.clf()  # clear previous figure and axes
                self._static_ax = self.static_canvas_RzPl.figure.subplots(
                    1, 2, sharex=False, sharey=False)  # add axes
                if (check_vmin_vmax == 1):
                    levels_to_plot = np.linspace(vmin, vmax, NN_cont)
                if (check_vmin_vmax == 0):
                    levels_to_plot = NN_cont
                contours = self._static_ax[0].contourf(
                    RR_plot,
                    zz_plot,
                    data_plot_t,
                    vmin=vmin,
                    vmax=vmax,
                    levels=levels_to_plot,
                    cmap='jet')
                cbar = self.figure_RzPl.colorbar(
                    contours, ax=self._static_ax[0], pad=0.07)
                cbar.ax.set_ylabel('deltaTrad/<Trad>', rotation=90)
                if contour_check == '1':
                    self._static_ax[0].contour(
                        RR_plot,
                        zz_plot,
                        data_plot_t,
                        vmin=vmin,
                        vmax=vmax,
                        levels=levels_to_plot,
                        cmap='binary')
                # cbar.ax.tick_params(labelsize=8, rotation=90)
                self._static_ax[0].plot(RR_plot, zz_plot, "ko", ms=2)

                if (self.Interp_plot_RzPl.currentText() == 'set to zero') | (
                        self.Interp_plot_RzPl.currentText() == 'with interpolation'):
                    self._static_ax[0].plot(
                        RR_plot[interp_mask], zz_plot[interp_mask], "wo", ms=6)

                self._static_ax[0].set_xlabel("R [m]")
                self._static_ax[0].set_ylabel("z [m]")
                self._static_ax[0].set_title("t = %0.7g" % (time_plot_t))

                for i, txt in enumerate(ch_zz):
                    self._static_ax[0].annotate(
                        txt + 1, (RR_plot[i, 0], zz_plot[i, 0]), fontsize=8)

                for i, txt in enumerate(ch_RR):
                    self._static_ax[0].annotate(
                        txt + 1, (RR_plot[0, i], zz_plot[0, i]), fontsize=8)

                self._static_ax[1].plot(time_plot, trace_1D)
                self._static_ax[1].set_xlabel("t [s]")
                self._static_ax[1].set_ylabel("deltaTrad/<Trad>")
                self._static_ax[1].set_title(
                    "LOS = 7, R_ch = 4, dt resolut = %g s" %
                    (time_plot[1] - time_plot[0]))
                self._static_ax[1].axvline(x=time_plot_t, color="k")

                self.figure_RzPl.suptitle(
                    "ECEI, Shot #%d, Filter: %s" %
                    (self.Shot, filter_status), fontsize=10)
                if (self.Save_plot_RzPl.currentText() == 'save as pdf') | (
                        (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                    path_to_save = self.path_ed_RzSet.text()
                    self.figure_RzPl.savefig(
                        path_to_save + 'p_%03d.pdf' %
                        (self.counter_save), bbox_inches='tight')
                    self.counter_save += 1
                if (self.Save_plot_RzPl.currentText() == 'save as png') | (
                        (self.Save_plot_RzPl.currentText() == 'save as pdf') & (self.counter_save == 0)):
                    path_to_save = self.path_ed_RzSet.text()
                    self.figure_RzPl.savefig(
                        path_to_save + 'p_%03d.png' %
                        (self.counter_save), bbox_inches='tight')
                    self.counter_save += 1
                click_coord = self.static_canvas_RzPl.mpl_connect(
                    'button_press_event', self.mouse_click_Rz)
                self.static_canvas_RzPl.draw()
                # self.sync_tabs(9)
                print("+++ The data has been plotted succesfully. +++")

            except Exception as exc:
                traceback.print_exc()
                print("!!! Cannot plot. ERROR: %s" % (exc))
        else:
            print("Please load the ECEI data (first tab)")

    def mouse_click_Rz(self, event):
        ix, iy = event.xdata, event.ydata
        print('x = %07g, y = %07g' % (
            ix, iy))
        self.tplot_ed_RzPl.setText("%0.7g" % (ix))
        if (event.dblclick == True) & (event.button == 1):
            self.f_Rz_plot(3)

    def sync_tabs(self, number):
        try:

            if (number == 9):
                tB_ed = self.tB_ed_RzPl.text()
                tE_ed = self.tE_ed_RzPl.text()
                tCnt_ed = self.tCnt_ed_RzPl.text()
                dt_ed = self.dt_ed_RzPl.text()
                Fourier_cut = self.Fourier_cut_RzPl.text()
                Fourier2_cut = self.Fourier2_cut_RzPl.text()
                Savgol_ed0 = self.SavGol_ed0_RzPl.text()
                Savgol_ed1 = self.SavGol_ed1_RzPl.text()
                Binning_ed = self.Binning_ed_RzPl.text()
            # 9
            self.tB_ed_RzPl.setText(tB_ed)
            self.tE_ed_RzPl.setText(tE_ed)
            self.tCnt_ed_RzPl.setText(tCnt_ed)
            self.dt_ed_RzPl.setText(dt_ed)
            self.Fourier_cut_RzPl.setText(Fourier_cut)
            self.Fourier2_cut_RzPl.setText(Fourier2_cut)
            self.SavGol_ed0_RzPl.setText(Savgol_ed0)
            self.SavGol_ed1_RzPl.setText(Savgol_ed1)
            self.Binning_ed_RzPl.setText(Binning_ed)

        except Exception as exc:
            print("!!! Couldn't synchronize tabs. ERROR: %s" % (exc))


# -------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
