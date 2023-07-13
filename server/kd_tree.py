import face_recognition
from rtree import index
from os.path import join
import sys, os
import math
import heapq 
import numpy as np

PATH = './static/'
EXT = '.jpg'

id_person = {}
face_encodings = {}

def clear_files():
    for base, dirs, files in os.walk('./'):
        if '128d.data' in files:
            os.remove('128d.data')
        if '128d.index' in files:
            os.remove('128d.index')

def euclidean_distance(query_encoding, known_encoding):
    sum = 0
    for i in range(len(query_encoding)): #D=128
        sum += math.pow((query_encoding[i] - known_encoding[i]), 2)
    return math.sqrt(sum)

def get_img_vector(img):
    picture = face_recognition.load_image_file(img)
    try:
        encoding = face_recognition.face_encodings(picture)[0] # feature vector
        return encoding
    except IndexError as e:
        print(e, "No face detected")

class KDTreeNode:
    def __init__(self, point):
        self.point = point
        self.left = None
        self.right = None

class KDTree:
    root = None
    def __init__(self):
        self.root = None
        self.extract_features()
        self.build_tree()

    def extract_features(self):
        i = -1
        for base, dirs, files in os.walk(PATH):
            i += 1
            encodings = []
            for file in files:
                img = join(base, file)
                if img.endswith(EXT):
                    picture = face_recognition.load_image_file(img)
                    if len(face_recognition.face_encodings(picture)) > 0:
                        encoding = face_recognition.face_encodings(picture)[0] # feature vector
                        encodings.append((img.replace('./data/',''), encoding))
            face_encodings[base.replace('./data/','')] = encodings
            if i >= 1:
                print(i, base)

    def build_tree(self):
        points = []
        for person, encodings in face_encodings.items():
            for _, encoding in encodings:
                points.append(encoding)
        self.root = self.construct_kdtree(points)

    def construct_kdtree(self, points, depth=0):
        if len(points) == 0:
            return None
        axis = depth % 128 #D
        points.sort(key=lambda point: point[axis])
        median = len(points) // 2
        node = KDTreeNode(points[median])
        node.left = self.construct_kdtree(points[:median], depth + 1)
        node.right = self.construct_kdtree(points[median + 1:], depth + 1)
        return node

    def euclidean_distancekd(self, query, point):
        sum = 0
        for i in range(len(query)): #D=128
            sum += math.pow((query[i] - point[i]), 2)
        return math.sqrt(sum)

    def priority_kd(self, query, k_results):
        heap = []
        self.search_kdtree(self.root, query, k_results, heap)
        heap = [(person, -dist, img_path) for dist, person, img_path in heap]
        heap.sort(key=lambda tup: tup[1]) # O(k_results x log(k_results))
        return heap

    def search_kdtree(self, node, query, k_results, heap, depth=0):
        if node is None:
            return
        axis = depth % 128 #D
        dist = self.euclidean_distancekd(query, node.point)
        if len(heap) < k_results:
            heapq.heappush(heap, (-dist, id_person[node.point], id_person[node.point][1]))
        else:
            r = heap[0] # front
            if dist <= -r[0]:
                heapq.heappush(heap, (-dist, id_person[node.point], id_person[node.point][1]))
                heapq.heappop(heap)
        if query[axis] < node.point[axis]:
            self.search_kdtree(node.left, query, k_results, heap, depth + 1)
        else:
            self.search_kdtree(node.right, query, k_results, heap, depth + 1)
            