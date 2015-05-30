#-*- coding:utf-8 - *-
__author__ = 'Marcos'

import sys
import itertools


class FPNode(object):
    """FP树的节点"""

    def __init__(self, value, count, parent):
        """树的构造函数"""
        self.value = value  #节点值
        self.count = count  #计数值
        self.parent = parent    #指向当前节点的父节点，从叶节点回溯时使用
        self.link = None    #用来链接相似的元素项
        self.children = []  # 存放节点的子节点

    def has_child(self, value):
        """检查节点是否有值为value的子节点"""
        for node in self.children:
            if node.value == value:
                return True

        return False

    def get_child(self, value):
        """获取值为value的子节点"""
        for node in self.children:
            if node.value == value:
                return node

        return None

    def add_child(self, value):
        """添加值为value的子节点"""
        child = FPNode(value, 1, self)
        self.children.append(child)
        return child


class FPTree(object):
    """一个FP树"""

    def __init__(self, transactions, threshold, root_value, root_count):
        """创建树"""
        self.frequent = self.find_frequent_items(transactions, threshold)
        self.headers = self.build_header_table(self.frequent)
        self.root = self.build_FPTree(
            transactions, root_value,
            root_count, self.frequent, self.headers)

    def find_frequent_items(self, transactions, threshold):
        """根据最小支持度计数找到所有项"""
        items = {}

        for transaction in transactions:
            for item in transaction:
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1

        for key in items.keys():
            if items[key] < threshold:
                del items[key]

        return items

    def build_header_table(self, frequent):
        """创建项头表"""
        headers = {}
        for key in frequent.keys():
            headers[key] = None

        return headers

    def build_FPTree(self, transactions, root_value,
                    root_count, frequent, headers):
        """建立FP树并返回根节点"""
        root = FPNode(root_value, root_count, None)

        for transaction in transactions:
            sorted_items = [x for x in transaction if x in frequent]
            sorted_items.sort(key=lambda x: frequent[x], reverse=True)
            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, root, headers)

        return root

    def insert_tree(self, items, node, headers):
        """递归的添加节点"""
        first = items[0]
        child = node.get_child(first)
        if child is not None:
            child.count += 1
        else:
            #添加子节点
            child = node.add_child(first)

            # 与头表相连
            if headers[first] is None:
                headers[first] = child
            else:
                current = headers[first]
                while current.link is not None:
                    current = current.link
                current.link = child

        #递归
        remaining_items = items[1:]
        if len(remaining_items) > 0:
            self.insert_tree(remaining_items, child, headers)

    def tree_has_single_path(self, node):
        """如果树内有单路径"""
        num_children = len(node.children)
        if num_children > 1:
            return False
        elif num_children == 0:
            return True
        else:
            return True and self.tree_has_single_path(node.children[0])

    def mine_patterns(self, threshold):
        """寻找frequent patterns"""
        if self.tree_has_single_path(self.root):
            return self.generate_pattern_list()
        else:
            return self.zip_patterns(self.mine_sub_trees(threshold))

    def zip_patterns(self, patterns):
        """根据条件FP树寻找条件模式基"""
        suffix = self.root.value

        if suffix is not None:
            new_patterns = {}
            for key in patterns.keys():
                new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

            return new_patterns

        return patterns

    def generate_pattern_list(self):
        """当此根节点对应只有一个条件模式基"""
        patterns = {}
        items = self.frequent.keys()

        #模式基为前缀
        if self.root.value is None:
            suffix_value = []
        else:
            suffix_value = [self.root.value]
            patterns[tuple(suffix_value)] = self.root.count

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items, i):
                pattern = tuple(sorted(list(subset) + suffix_value))
                patterns[pattern] = \
                    min([self.frequent[x] for x in subset])

        return patterns

    def mine_sub_trees(self, threshold):
        """生成条件FP树，并寻找条件模式基"""
        patterns = {}
        mining_order = sorted(self.frequent.keys(),
                              key=lambda x: self.frequent[x])

        # 反向回溯
        for item in mining_order:
            suffixes = []
            conditional_tree_input = []
            node = self.headers[item]

            #沿项头表寻找所有
            while node is not None:
                suffixes.append(node)
                node = node.link

            # 回溯路径
            for suffix in suffixes:
                frequency = suffix.count
                path = []
                parent = suffix.parent

                while parent.parent is not None:
                    path.append(parent.value)
                    parent = parent.parent

                for i in range(frequency):
                    conditional_tree_input.append(path)

            # 已建立条件数，寻找条件模式基
            subtree = FPTree(conditional_tree_input, threshold,
                             item, self.frequent[item])
            subtree_patterns = subtree.mine_patterns(threshold)

            # I将模式插入
            for pattern in subtree_patterns.keys():
                if pattern in patterns:
                    patterns[pattern] += subtree_patterns[pattern]
                else:
                    patterns[pattern] = subtree_patterns[pattern]

        return patterns


def generate_association_rules(patterns, confidence_threshold):
    """生成关联规则"""
    rules = {}
    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent = tuple(sorted(antecedent))
                consequent = tuple(sorted(set(itemset) - set(antecedent)))

                if antecedent in patterns:
                    lower_support = patterns[antecedent]
                    confidence = float(upper_support) / lower_support

                    if confidence >= confidence_threshold:
                        rules[antecedent] = (consequent, confidence)

    return rules
