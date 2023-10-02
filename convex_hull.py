from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		sortedPoints = sorted(points, key=lambda k: [k[0], k[1]])
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def divide_and_conquer(points):
		n = len(points)
		if n <= 1:
			return points
		left = divide_and_conquer(points[:n//2])
		right = divide_and_conquer(points[n//2:])
		return merge(left, right)

	def merge(left, right):
		if not left or not right:
			return left or right
		if left[-1][0] <= right[0][0]:
			lower_tangent = merge_lower_tangent(left, right)
		else:
			lower_tangent = merge_lower_tangent(right, left)
		if left[0][0] >= right[-1][0]:
			upper_tangent = merge_upper_tangent(left, right)
		else:
			upper_tangent = merge_upper_tangent(right, left)
		return lower_tangent + upper_tangent[1:-1] + lower_tangent

	def merge_lower_tangent(left, right):
		while len(left) > 1 and len(right) > 1:
			if slope(left[-2], left[-1]) <= slope(right[0], right[1]):
				left.pop()
			else:
				right.pop(0)
		return left + right

	def merge_upper_tangent(left, right):
		while len(left) > 1 and len(right) > 1:
			if slope(left[0], left[1]) >= slope(right[-2], right[-1]):
				left.pop(0)
			else:
				right.pop()
		return left + right

	def slope(p, q):
		return (q[1] - p[1]) / (q[0] - p[0])
