#-*- coding:utf-8 - *-
__author__ = 'Marcos'

import fpgrowth as fp
import sys

import time
import resource

def load_data():
    return [['I1', 'I2', 'I5'], ['I2', 'I4'], ['I2', 'I3'], ['I1', 'I2', 'I4'], ['I1', 'I3'], ['I2', 'I3'], ['I1', 'I3'], ['I1', 'I2', 'I3', 'I5'], ['I1', 'I2', 'I3']]


def load_large_data():
    array = []


    file_iter = open('INTEGRATED-DATASET.csv', 'rU')
    for line in file_iter:
        line = line.strip().rstrip(',')                         # Remove trailing comma
        items = line.split(',')
        items = sorted(items)
        #print items
        array.append(items)
    return array

def main(argv):
    dataset = load_large_data()
    min_support = int(0.2 * len(dataset))

    timestart = time.clock()
    tree = fp.FPTree(dataset, min_support, None, None)
    patterns = tree.mine_patterns(min_support)
    time_elapsed = (time.clock() - timestart)
    print '频繁项集:'
    print patterns

    #生成关联规则
    print '关联规则：'
    min_confidence = 0.6
    rules = fp.generate_association_rules(patterns, min_confidence)
    for rule in rules.keys():
        print rule, '=>', rules[rule]

    print '耗时：', time_elapsed, 's'

    print '内存：', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'byte'

if __name__ == '__main__':
    main(sys.argv)