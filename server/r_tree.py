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

# KNN-Secuencial: Implementación de los algoritmos de búsqueda sin indexación
def sequential_knn(query, k_results):
    result = []
    for person, encodings in face_encodings.items(): # O(N x D)
        for img, encoding in encodings:
            dist = euclidean_distance(query, encoding)
            result.append((person, dist, img))
    result.sort(key=lambda tup: tup[1]) # O(N x logN)
    return result[:k_results]

def get_img_vector(img):
    picture = face_recognition.load_image_file(img)
    try:
        encoding = face_recognition.face_encodings(picture)[0] # feature vector
        return encoding
    except IndexError as e:
        print(e, "No face detected")


class RTree:
  idx = None
  def __init__(self):
    p = index.Property()
    p.dimension = 128 #D
    p.buffering_capacity = 10 #M
    p.dat_extension = 'data'
    p.idx_extension = 'index'
    self.idx = index.Index('128d', properties=p)
    self.extract_features()
    self.insert_all()
  
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
  
  def insert_all(self):   
    id = 0
    for person, encodings in face_encodings.items():
      for img, encoding in encodings:
        point = tuple(encoding)
        point += point
        id_person[id] = (person, img, encoding)
        self.idx.insert(id, point)
        id += 1

  def mindist(self, query, region):
    sum = 0
    for i in range(len(query)): #D=128
      r = None
      if query[i] < region[i]:
        r = region[i]
      elif query[i] > region[i + 128]:
        r = region[i + 128]
      else:
        r = query[i]
      sum += math.pow((query[i] - r), 2)
    return math.sqrt(sum)

  def priority_knn(self, query, k_results):
    heap = []
    min_distance = sys.float_info.max
    leaf_region = None
    for leaf in self.idx.leaves():
      if self.mindist(query, leaf[2]) < min_distance: # leaf[2] -> region bounds
        min_distance = self.mindist(query, leaf[2])
        leaf_region = leaf
    for point in leaf_region[1]: # leaf_region[1] -> points
      person = id_person[point][0]
      img_path = id_person[point][1]
      encoding = id_person[point][2]
      distance = euclidean_distance(query, encoding)
      if len(heap) < k_results:
        heapq.heappush(heap, (-distance, person, img_path))
      else:
        r = heap[0] # front
        if distance <= -r[0]:
          heapq.heappush(heap, (-distance, person, img_path))
          heapq.heappop(heap)
    heap = [(person, -dist, img_path) for dist, person, img_path in heap]
    heap.sort(key=lambda tup:tup[1]) # O(k_results x log(k_results))
    return heap

  def by_range(self, query, radius):
    result = []
    for person, encodings in face_encodings.items(): # O(N x D)
      for img, encoding in encodings:
        dist = euclidean_distance(query, encoding)
        if dist <= radius:
          result.append((person, dist, img))
    result.sort(key=lambda tup:tup[1]) # O(N x logN)
    return result