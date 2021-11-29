# Реализация алгоритма Дейкстры для матрицы смежности
# по мотивам https://python-scripts.com/dijkstras-algorithm

import math

class Node:
    def __init__(self, data, indexloc=None):
        self.data = data
        self.index = indexloc

    def __repr__(self):
        return f"<Node {self.data}>"


class Graph:
    @classmethod
    def create_from_nodes(self, nodes):
        return Graph(len(nodes), len(nodes), nodes)

    def __init__(self, rows, cols, nodes=None):
        # установка матрицы смежности размером rows x cols
        self.adj_mat = [[0] * cols for _ in range(rows)]     ## san ##
        ## san ##self.adj_mat = [[float("inf")] * cols for _ in range(rows)]     ## san ##
        self.nodes = nodes
        for i in range(len(self.nodes)):
            self.nodes[i].index = i

    # Связывает node1 с node2
    # Обратите внимание, что ряд - источник, а столбец - назначение
    # Обновлен для поддержки взвешенных ребер (поддержка алгоритма Дейкстры)
    def connect_dir(self, node1, node2, weight=1):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        self.adj_mat[node1][node2] = weight
        ## san ##self.adj_mat[node1][node1] = 0  ## san ##
        ## san ##self.adj_mat[node2][node2] = 0  ## san ##

    # Опциональный весовой аргумент для поддержки алгоритма Дейкстры
    def connect(self, node1, node2, weight=1):
        self.connect_dir(node1, node2, weight)
        self.connect_dir(node2, node1, 1/weight)

    # Получает ряд узла, отметить ненулевые объекты с их узлами в массиве self.nodes
    # Выбирает любые ненулевые элементы, оставляя массив узлов
    # которые являются connections_to (для ориентированного графа)
    # Возвращает значение: массив кортежей (узел, вес)
    def connections_from(self, node):
        node = self.get_index_from_node(node)
        return [(self.nodes[col_num], self.adj_mat[node][col_num]) for col_num in range(len(self.adj_mat[node])) if
                self.adj_mat[node][col_num] != 0]

    # Проводит матрицу к столбцу узлов
    # Проводит любые ненулевые элементы узлу данного индекса ряда
    # Выбирает только ненулевые элементы
    # Обратите внимание, что для неориентированного графа
    # используется connections_to ИЛИ connections_from
    # Возвращает значение: массив кортежей (узел, вес)
    def connections_to(self, node):
        node = self.get_index_from_node(node)
        column = [row[node] for row in self.adj_mat]
        return [(self.nodes[row_num], column[row_num]) for row_num in range(len(column)) if column[row_num] != 0]

    def print_adj_mat(self):
        for row in self.adj_mat:
            print(row)

    def node(self, index):
        return self.nodes[index]

    def remove_conn(self, node1, node2):
        self.remove_conn_dir(node1, node2)
        self.remove_conn_dir(node2, node1)

    # Убирает связь в направленной манере (nod1 к node2)
    # Может принять номер индекса ИЛИ объект узла
    def remove_conn_dir(self, node1, node2):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        self.adj_mat[node1][node2] = 0

    # Может пройти от node1 к node2
    def can_traverse_dir(self, node1, node2):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        return self.adj_mat[node1][node2] != 0

    def has_conn(self, node1, node2):
        return self.can_traverse_dir(node1, node2) or self.can_traverse_dir(node2, node1)

    def add_node(self, node):
        self.nodes.append(node)
        node.index = len(self.nodes) - 1
        for row in self.adj_mat:
            row.append(0)
        self.adj_mat.append([0] * (len(self.adj_mat) + 1))

    # Получает вес, представленный перемещением от n1
    # к n2. Принимает номера индексов ИЛИ объекты узлов
    def get_weight(self, n1, n2):
        node1, node2 = self.get_index_from_node(n1), self.get_index_from_node(n2)
        return self.adj_mat[node1][node2]

    # Разрешает проводить узлы ИЛИ индексы узлов
    def get_index_from_node(self, node):
        if not isinstance(node, Node) and not isinstance(node, int):
            raise ValueError("node must be an integer or a Node object")
        if isinstance(node, int):
            return node
        else:
            return node.index

    def dijkstra(self, node):
        # Получает индекс узла (или поддерживает передачу int)
        nodenum = self.get_index_from_node(node)
        # Заставляет массив отслеживать расстояние от одного до любого узла
        # в self.nodes. Инициализирует до бесконечности для всех узлов, кроме
        # начального узла, сохраняет "путь", связанный с расстоянием.

        # Индекс 0 = расстояние, индекс 1 = перескоки узла
        DISTANCE = 0
        HOPS = 1

        dist = [None] * len(self.nodes)
        for i in range(len(dist)):
            dist[i] = [float("inf")]
            dist[i].append([self.nodes[nodenum]])

        dist[nodenum][DISTANCE] = 0     ## san ##
        ## san ##dist[nodenum][DISTANCE] = 1 ## san ##

        # Добавляет в очередь все узлы графа
        # Отмечает целые числа в очереди, соответствующие индексам узла
        # локаций в массиве self.nodes
        queue = [i for i in range(len(self.nodes))]
        # Набор просмотренных на данный момент номеров
        seen = set()
        while len(queue) > 0:
            # Получает узел в очереди, который еще не был рассмотрен
            # и который находится на кратчайшем расстоянии от источника
            min_dist = float("inf")
            min_node = None
            for n in queue:
                if dist[n][DISTANCE] < min_dist and n not in seen:
                    min_dist = dist[n][DISTANCE]
                    min_node = n

            # Добавляет мин. расстояние до просмотренного узла, убирает из очереди
            queue.remove(min_node)
            seen.add(min_node)

            # Получает все следующие перескоки
            connections = self.connections_from(min_node)
            # Для каждой связи обновляет путь и полное расстояние от
            # исходного узла, если полное расстояние меньше
            # чем текущее расстояние в массиве dist
            for (node, weight) in connections:
                tot_dist = weight + min_dist        ## san ##
                ## san ##if min_dist:                        ## san ##
                ## san ##    tot_dist = weight * min_dist    ## san ##
                ## san ##else:                               ## san ##
                ## san ##    tot_dist = weight               ## san ##

                if tot_dist < dist[node.index][DISTANCE]:
                    dist[node.index][DISTANCE] = tot_dist
                    dist[node.index][HOPS] = list(dist[min_node][HOPS])
                    dist[node.index][HOPS].append(node)
        return dist


if __name__ == "__main__":
    EUR = Node("EUR")
    USD = Node("USD")
    CHF = Node("CHF")
    CAD = Node("CAD")
    GBP = Node("GBP")
    JPY = Node("JPY")
    AUD = Node("AUD")
    NZD = Node("NZD")

    nodes = [EUR, USD, CHF, CAD, GBP, JPY, AUD, NZD]
    w_graph = Graph.create_from_nodes(nodes)

    USE_UNIQUE_RATES = True

    if USE_UNIQUE_RATES:
        w_graph.connect(EUR, USD, 1.1165)
        w_graph.connect(USD, CHF, 0.9725)
        w_graph.connect(USD, CAD, 1.2985)
        w_graph.connect(EUR, GBP, 0.85)
        w_graph.connect(EUR, JPY, 121.18)
        w_graph.connect(EUR, CHF, 1.0857)
        w_graph.connect(AUD, USD, 0.698)
        w_graph.connect(GBP, JPY, 142.53)
        w_graph.connect(CHF, JPY, 111.59)
        w_graph.connect(GBP, CHF, 1.277)
        w_graph.connect(NZD, USD, 0.6691)
    else:
        w_graph.connect(EUR,USD)
        w_graph.connect(USD,CHF)
        w_graph.connect(USD,CAD)
        w_graph.connect(EUR,GBP)
        w_graph.connect(EUR,JPY)
        w_graph.connect(EUR,CHF)
        w_graph.connect(AUD,USD)
        w_graph.connect(GBP,JPY)
        w_graph.connect(CHF,JPY)
        w_graph.connect(GBP,CHF)
        w_graph.connect(NZD,USD)

    w_graph.print_adj_mat()

    for src_node in [NZD]:
        for dest_node in [AUD]:
            if dest_node == src_node:
                continue
            print(f"{src_node} --> {dest_node}")
            for weight, node in w_graph.dijkstra(src_node):
                path = [n.data for n in node]
                if len(path) == 1:
                    continue
                print(f"{'>' if dest_node and path[-1] == dest_node.data else ''}\t{weight:10.4f}\t{path}")
