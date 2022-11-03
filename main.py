# Mercier Wilfried - IRAP

import time
import copy
import sys
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import os
import os.path               as     opath
import numpy                 as     np

from   astropy.io                         import fits
from   typing                             import List, Optional, Any
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from   matplotlib.backend_bases           import MouseButton
from   matplotlib.figure                  import Figure

from   PyQt5.QtWidgets       import QFrame, QMainWindow, QApplication, QMenuBar, QAction, QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog, QShortcut, QSizePolicy, QSlider
from   PyQt5.QtCore          import Qt, pyqtSlot, QSize
from   PyQt5.QtGui           import QKeySequence, QPalette, QColor,  QFont, QIcon

class SpecImage(FigureCanvas):
   '''
   ..codeauthor:: Lina Issa & Wilfried Mercier

   Class that describes the spectrum figure.

   :param parent: parent object
   '''

   def __init__(self, parent: Any):

      self.parent = parent

      # Matplotlib figure object
      self.figure = Figure()
      self.figure.patch.set_facecolor("None")

      # Init figure canvas that holds the figure object
      FigureCanvas.__init__(self, self.figure)

      FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)

#      self.setStyleSheet("background-color:transparent;")

      FigureCanvas.updateGeometry(self)
      self.plot()

   def plot(self):
      data = [1, 2, 3, 4]
      ax   = self.figure.add_subplot(111)
      ax.tick_params(which='both', direction='in', bottom=True, top=True, right=True, left=True, labeltop=True, labelbottom=False)
      ax.plot(data, 'b-')
      self.draw()

class FigImage(FigureCanvas):

   def __init__(self, parent: Any):

      # Parent object
      self.parent      = parent

      # Zoom value (1 to begin with)
      self.zoom        = 1

      # Mouse left button press location (in asbolute pixel unit) used when panning (None means mouse button is released)
      self.clickLoc    = None

      # Matplotlib figure object and main axis
      self.figure      = Figure()
      self.figure.tight_layout(pad=0)
      self.figure.patch.set_facecolor("None")

      self.ax          = self.figure.add_subplot(111)

      # Init figure canvas that holds the figure object
      FigureCanvas.__init__(self, self.figure)

      FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
#      self.setStyleSheet("background-color:transparent;")
      FigureCanvas.updateGeometry(self)

      # XXX For test purposes
      self.plot()

      ######################################
      #          Signals handling          #
      ######################################

      # Listening to when the mouse is moved within the figure
      self.mpl_connect('motion_notify_event', self.mouseMoveImageEvent)

      # Listening to when the mouse is scrolled on the figure
      self.mpl_connect('scroll_event', self.mouseScrollImageEvent)

      # Listening to when a mouse button is pressed
      self.mpl_connect('button_press_event', self.mousePressImageEvent)

      # Listening to when a mouse button is released
      self.mpl_connect('button_release_event', self.mouseReleaseImageEvent)

   def plot(self):
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Plot used to debug.
      '''

      data = [1, 2, 3, 4]
      self.ax.tick_params(which='both', direction='in', bottom=True, top=True, right=True, left=True)
      self.ax.plot(data, 'r-')
      self.draw()

   def setImage(self, image: np.ndarray) -> None:
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Set an image for the plot.

      :param image: 2D data to show
      :type image: numpy ndarray
      '''

      if not isinstance(image, np.ndarray):
         return print(f'Error: image has type {type(image)} but it must be a np.ndarray.')

      if image.ndim != 2:
         return print(f'Error: image has {image.ndim} dimensions but it must have two only.')

      # Shape of the image drawn used as reference for the zoom
      self.imShape = image.shape

      self.ax.clear()
      self.ax.imshow(image, origin='lower', cmap='rainbow')
      return

   #######################################
   #       Mouse & Keyboard events       #
   #######################################

   def mouseMoveImageEvent(self, event, *args, **kwargs):
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Method that activates each time the mouse moves in the image.
      '''

      # If the left mouse button is pressed, then we pan the image
      if None not in [event.xdata, event.ydata, self.clickLoc]:

         # Offset from previous location
         dy = -(event.y - self.clickLoc[0])/200
         dx = -(event.x - self.clickLoc[1])/200

         xlen = self._xlim[1] - self._xlim[0]
         ylen = self._ylim[1] - self._ylim[0]

         # Update xlim and ylim
         self.ax.set_xlim(self._xlim[0] + dx*xlen, self._xlim[1] + dx*xlen)
         self.ax.set_ylim(self._ylim[0] + dy*ylen, self._ylim[1] + dy*ylen)

         # Update the figure so that the result is visble
         self.draw()

      return

   def mouseScrollImageEvent(self, event, *args, **kwargs):
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Method that activates each time the mouse is scrolled.
      '''

      print(event)

      zoom = event.step

      xmin = self.ax.get_xlim()[0]
      xmax = self.ax.get_xlim()[1]
      ymin = self.ax.get_ylim()[0]
      ymax = self.ax.get_ylim()[1]

      xcen = (xmax - xmin)/2
      ycen = (ymax - ymin)/2

      # Zoom in or out by changing the xlim and ylim
      self.ax.set_xlim([xmin - xcen*zoom, xmax+xcen*zoom])
      self.ax.set_ylim([ymin - ycen*zoom, ymax+ycen*zoom])

      # Update the figure so that the result is visible
      self.draw()
      return

   def mousePressImageEvent(self, event, *args, **kwargs):
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Method that activates each time one of the mouse buttons is pressed.
      '''

      if event.button is MouseButton.LEFT:
         self.clickLoc = [event.y, event.x]
         self._xlim    = self.ax.get_xlim()
         self._ylim    = self.ax.get_ylim()

      return

   def mouseReleaseImageEvent(self, event, *args, **kwargs):
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Method that activates each time one of the mouse buttons is released.
      '''

      if event.button is MouseButton.LEFT:
         self.clickLoc = None

      return

class WavelengthSlider(QWidget):
   r'''
   ..codeauthor:: Lina Issa & Wilfried Mercier

   Custom slider to change the wavelength.

   :param parent: parent object
   '''

   def __init__(self, parent: Any, *args, **kwargs) -> None:

      super().__init__(*args, **kwargs)

      ##################################################
      #           Slider object (horizontal)           #
      ##################################################

      self.slider = QSlider(Qt.Horizontal)

      # By default we set the values between 0 and 1 and we deactivate it
      self.slider.setMinimum(0)
      self.slider.setMaximum(1000)
#      self.slider.setEnabled(False)

      # Listen to the signal when the value is changed to update the text label
      self.slider.valueChanged.connect(self.updateLabel)

      ###################################################
      #           Text showing the wavelength           #
      ###################################################

      self.text   = QLabel()
      print(self.slider.value())
      self.text.setText(str(self.slider.value()))

      # Layout used to arrange the children widgets
      self.layout = QHBoxLayout()
      self.layout.addWidget(self.slider)
      self.layout.addWidget(self.text)

      self.setLayout(self.layout)

   def updateLabel(self, value: Any, *args, **kwargs) -> None:
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Update the label when the slider value changes.

      :param value: value of the slider
      '''

      self.text.setText(str(value))
      return

class App(QMainWindow):
   r'''
   ..codeauthor:: Lina Issa & Wilfried Mercier

   Main application.

   :param QApplication root: root object
   :param str iconsPath: (**Optional**) path where to find the icons
   '''

   def __init__(self, root: QApplication, iconsPath: str = 'icons', **kwargs) -> None:

      self.root           = root
      super().__init__(**kwargs)

      # Script current dir
      self.scriptDir      = opath.dirname(opath.realpath(__file__))

      appName             = 'Masking utility'
      self.setWindowTitle(appName)
#      root.setApplicationName(appName)
#      self.setWindowIcon(QIcon(opath.join(self.scriptDir, 'icon.png')))

      # By default no file is loaded (hence None)
      self.file           = None
      self.data           = None
      self.hdr            = None

      # Window
      self.win            = QWidget()
      self.win.setObjectName('Main')

      ########################################
      #        Child objects creation        #
      ########################################

      # Custom slider for the wavelength
      self.wvSlider       = WavelengthSlider(self)

      # Canvas for the matplotlib plot to show the spectrum
      self.specCanvas     = SpecImage(self)
      self.specCanvas.setFixedHeight(200)

      # Canvas for the matplotlib plot to show the image
      self.imCanvas       = FigImage(self)

      ############################################
      #           Common color palettes          #
      ############################################

      self.errorPalette   = QPalette()
      self.errorColorName = 'firebrick'
      red                 = QColor(self.errorColorName)
      self.errorPalette.setColor(QPalette.Text, red)

      ################################################
      #                 Setup layout                 #
      ################################################

      # Layout of the main window
      self.layoutWin      = QVBoxLayout()

      # Spectrum on the first line
      self.layoutWin.addWidget(self.specCanvas, 0)

      # Slider on the second line
      self.layoutWin.addWidget(self.wvSlider, 0)

      # Image on the second line
      self.layoutWin.addWidget(self.imCanvas, 2)

      # Set layout
      self.win.setLayout(self.layoutWin)

      ###############################################
      #               Setup shortcuts               #
      ###############################################

#      self.shortcuts           = {}
#      self.shortcuts['Ctrl+O'] = QShortcut(QKeySequence('Ctrl+O'), self.tabSettings)
#      self.shortcuts['Ctrl+O'].activated.connect(self.loadCorpus)

      ############################
      #           Menu           #
      ############################

      menubar           = self.menuBar()

      # Setup actions given the languages found
      filemenu          = menubar.addMenu('&File')

      action            = QAction(f'&Open', self)
      action.triggered.connect(lambda x=None: x)
      filemenu.addAction(action)

      # Setup actions for the theme
      stylemenu         = menubar.addMenu('&Style')
      action            = QAction(f'&Normal', self)
      action.triggered.connect(lambda x=None: x)
      stylemenu.addAction(action)

      ###########################################
      #               Apply theme               #
      ###########################################

#      self.setTheme(self.theme)

      # Temporary: load test data an insert in image
      self.load('/home/wilfried/Projects/Masks/cube.fits')
      self.imCanvas.setImage(self.data[0])


      ##################################
      #        Show application        #
      ##################################

      self.setCentralWidget(self.win)
      self.resize(800, 800)
      self.centre()
      self.show()

   ################################
   #          IO methods          #
   ################################

   def load(self, file: str, ext: int = 0, *args, **kwargs) -> None:
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      :param str file: load a file
      :param str ext: (**Optional**) extension to open
      '''

      # Bad programming: the code should not break because of this.
      # To be changed in the future
      if not isinstance(file, str):
         raise TypeError(f'file {file} has type {type(file)} but it must be str.')

      if not isinstance (ext, int):
         raise TypeError(f'extension for the file has type {type(ext)} but it must be an integer.')

      if not opath.isfile(file):
         raise OSError(f'file {file} is not a file.')

      tmp = opath.splitext(file)[-1]
      if not tmp.lower() in ['.fit', '.fits']:
         raise IOError(f'file {file} has extension {tmp} but only .fit and .fits are allowed.')

      self.file = file

      print(file, ext)
      with fits.open(file) as hdul:
         self.data = hdul[ext].data
         self.hdr  = hdul[ext].header

      return

   ##################################
   #          Miscellaneous         #
   ##################################

   def centre(self, *args, **kwargs) -> None:
      r'''
      ..codeauthor:: Lina Issa & Wilfried Mercier

      Centre the window.
      '''

      frameGm     = self.frameGeometry()
      screen      = self.root.desktop().screenNumber(self.root.desktop().cursor().pos())
      centerPoint = self.root.desktop().screenGeometry(screen).center()
      centerPoint.setY(centerPoint.y())
      centerPoint.setX(centerPoint.x())
      frameGm.moveCenter(centerPoint)
      self.move(frameGm.topLeft())

      return


if __name__ == '__main__':
   root   = QApplication(sys.argv)
   root.setApplicationName('Test')
   root.setApplicationDisplayName('Test2')
   app    = App(root)
   sys.exit(root.exec_())
