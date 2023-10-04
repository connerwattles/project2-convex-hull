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
		sortedPoints = sorted(points, key=lambda k: k.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		#polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		node = divide_and_conquer(sortedPoints)
		polygon = convert_to_qlinef_list(node)
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

def divide_and_conquer(points):
	n = len(points)
	if n <= 1:
		hull = create_doubly_linked_list(points)
		return hull
	left = divide_and_conquer(points[:n//2])
	right = divide_and_conquer(points[n//2:])
	
	lpu, rpu, lpl, rpl = find_tangents(left, right)

	lpu.next = rpu
	rpu.prev = lpu
	rpl.next = lpl
	lpl.prev = rpl

	return lpu

def find_tangents(left, right):

	leftHullRightMost = find_rightmost_node(left)
	rightHullLeftMost = find_leftmost_node(right)

	leftTangentUpperPoint = leftHullRightMost
	rightTangentUpperPoint = rightHullLeftMost
	done = True
	while done:
		done = False
		previousSlope = slope(leftTangentUpperPoint.point, rightTangentUpperPoint.point)

		while slope(leftTangentUpperPoint.prev.point, rightTangentUpperPoint.point) < previousSlope:
			leftTangentUpperPoint = leftTangentUpperPoint.prev
			previousSlope = slope(leftTangentUpperPoint.point, rightTangentUpperPoint.point)
			done = True

		while slope(leftTangentUpperPoint.point, rightTangentUpperPoint.next.point) > previousSlope:
			rightTangentUpperPoint = rightTangentUpperPoint.next
			previousSlope = slope(leftTangentUpperPoint.point, rightTangentUpperPoint.point)
			done = True

	leftTangentLowerPoint = leftHullRightMost
	rightTangentLowerPoint = rightHullLeftMost
	done = True
	while done:
		done = False
		previousSlope = slope(leftTangentLowerPoint.point, rightTangentLowerPoint.point)

		while slope(leftTangentLowerPoint.next.point, rightTangentLowerPoint.point) > previousSlope:
			leftTangentLowerPoint = leftTangentLowerPoint.next
			previousSlope = slope(leftTangentLowerPoint.point, rightTangentLowerPoint.point)
			done = True

		while slope(leftTangentLowerPoint.point, rightTangentLowerPoint.prev.point) < previousSlope:
			rightTangentLowerPoint = rightTangentLowerPoint.prev
			previousSlope = slope(leftTangentLowerPoint.point, rightTangentLowerPoint.point)
			done = True

	return leftTangentUpperPoint, rightTangentUpperPoint, leftTangentLowerPoint, rightTangentLowerPoint


def slope(p1, p2):
	return (p2.y() - p1.y()) / (p2.x() - p1.x())


class Node:
	def __init__(self, point):
		self.point = point
		self.prev = None
		self.next = None

def create_doubly_linked_list(points):
	# Create a doubly linked list from a list of points
	head = Node(points[0])
	tail = head
	for point in points[1:]:
		node = Node(point)
		node.prev = tail
		tail.next = node
		tail = node
	head.prev = tail
	tail.next = head
	return head

def convert_to_qlinef_list(head):
	# Convert a doubly linked list of QPointF objects to a list of QLineF objects
	qlinef_list = []
	node = head
	while True:
		qlinef_list.append(QLineF(node.point, node.next.point))
		node = node.next
		if node == head:
			break
	return qlinef_list

def find_rightmost_node(head):
	# Find the rightmost node in a circular doubly linked list
	node = head
	rightmost_node = node
	while node.next != head:
		node = node.next
		if node.point.x() > rightmost_node.point.x():
			rightmost_node = node
	return rightmost_node

def find_leftmost_node(head):
	# Find the leftmost node in a circular doubly linked list
	node = head
	leftmost_node = node
	while node.next != head:
		node = node.next
		if node.point.x() < leftmost_node.point.x():
			leftmost_node = node
	return leftmost_node