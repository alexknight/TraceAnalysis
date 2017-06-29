# -*- coding: utf-8 -*-

import os
import re
import sys

from config import config
from log import logger

sys.path.append("../")

logger = logger()

MAX_RECORD = int(config.MAX_SAVE_RECORDS)

WATCHER = config.WATCH_MODULES or ""


class TraceDump(object):
    def __init__(self):
        self.traceFileName = ""
        self.traceThreadName = ""

    def getTraceFileName(self):
        return self.traceFileName

    def setTraceFileName(self, fileName):
        self.traceFileName = fileName

    def analysisExclusiveTime(self, fileName):
        try:
            flag = False
            excl_record = []
            f = open(fileName, 'r')
            for line_content in f:
                if flag:
                    if "Inclusive elapsed times for each method" in line_content:
                        break
                    excl_record.append(line_content)
                else:
                    if "Exclusive elapsed times for each method" in line_content:
                        flag = True
        except IOError:
            logger.error("The file don't exist, Please double check!")

        regex = '(\d+?)\s+?([\d\.]+?)\s+?([\d\.]+?)\s+?\[(\d+?)\]\s+?(.+?)$'
        p = re.compile(regex)
        method_dict = {}
        excl_data = {}
        for each_excl in excl_record:
            result = p.findall(each_excl)
            if len(result) != 0:
                result = result[0]
                method_dict[result[3]] = result[4]
                tmp_method = self.trimPreStr(result[4].replace(" ", "").replace("/", "."), '.')
                if re.search(WATCHER, tmp_method) is not None:
                    excl_data[tmp_method] = int(result[0])
        return method_dict, excl_data

    def analysisInclusiveTime(self, fileName):
        try:
            flag = False
            incl_record = []
            each_method = []
            f = open(fileName, 'r')
            for line_content in f:
                if flag:
                    if "Exclusive elapsed time for each class" in line_content:
                        break
                    if "---------------------------------------------------" in line_content:
                        incl_record.append(each_method)
                        each_method = []
                    else:
                        each_method.append(line_content)
                else:
                    if "Inclusive elapsed times for each method" in line_content:
                        flag = True
        except IOError:
            logger.error("The file don't exist, Please double check!")

        regex_self = '\[(\d+?)\]\s+?([\d\.]+?)%\s+?([\d\+]+?)\s+?(\d+?)\s+?(.+?)$'
        regex_other = '([\d\.]+?)%\s+?\[(\d+?)\]\s+?([\d\/]+?)\s+?(\d+?)\s+?(.+?)$'
        p_self = re.compile(regex_self)
        p_other = re.compile(regex_other)

        parent_children = {}
        incl_data = {}
        for each_incl_record in incl_record:
            flag = 0
            index = 0
            method_dict = {0: [], 1: []}
            for each_incl in each_incl_record:
                result = p_other.findall(each_incl)
                if len(result) != 0:
                    result = result[0]
                    tmp_method = self.trimPreStr(result[4].replace(" ", "").replace("/", "."), '.')
                    method_dict[flag].append(tmp_method)
                    if re.search(WATCHER, tmp_method) is not None:
                        if tmp_method not in incl_data.keys():
                            incl_data[tmp_method] = int(result[3])
                        else:
                            if incl_data[tmp_method] < int(result[3]):
                                incl_data[tmp_method] = int(result[3])
                else:
                    result = p_self.findall(each_incl)
                    if len(result) != 0:
                        result = result[0]
                        tmp_method = self.trimPreStr(result[4].replace(" ", "").replace("/", "."), '.')
                        #                         print tmp_method
                        #                         if re.search(WATCHER, tmp_method) is not None:
                        #                             incl_data[tmp_method] = int(result[3])
                        flag = 1
                        index = tmp_method
            parent_children[index] = method_dict
        return parent_children, incl_data

    def analysisCallTimes(self, fileName):
        try:
            flag = False
            call_record = []
            f = open(fileName, 'r')
            for line_content in f:
                if flag:
                    call_record.append(line_content)
                else:
                    if "Exclusive elapsed time for each method" in line_content:
                        flag = True
        except IOError:
            logger.error("The file don't exist, Please double check!")

        regex = '(\d+?)\s+?([\d\.]+?)\s+?([\d\.]+?)\s+?([\d\.]+?)\s+?(\d+?)\+(\d+?)\s+?\[(\d+?)\]\s+?(.+?)$'
        p = re.compile(regex)
        call_data = {}
        for each_excl in call_record:
            result = p.findall(each_excl)
            if len(result) != 0:
                result = result[0]
                tmp_method = self.trimPreStr(result[7].replace(" ", "").replace("/", "."), '.')
                if re.search(WATCHER, tmp_method) is not None:
                    call_data[tmp_method] = int(result[4]) + int(result[5])
        return call_data

    def analysisTheadTime(self, traceThreadName):
        try:
            flag = True
            regex_thread = '(\d+?)\s+?(.+?)$'
            regex_action = '(\d+?)\s+?([a-z]+?)\s+?(\d+?)[\s-]+?(.+?)$'
            p_thread = re.compile(regex_thread)
            p_action = re.compile(regex_action)

            threads = {}
            thread_time = {}
            method_thread = {}
            tmp = {}
            f = open(traceThreadName, 'r')
            for line_content in f:
                if flag:
                    if "Trace (threadID action usecs class.method signature):" in line_content:
                        flag = False
                    else:
                        result = p_thread.findall(line_content)
                        if len(result) != 0:
                            result = result[0]
                            threads[result[0]] = result[1]
                else:
                    result = p_action.findall(line_content)
                    if len(result) != 0:
                        result = result[0]
                        # 将方法中多余多空格去掉，将 / 转成 . ，
                        # 并且把前面用于表现层级关系的 . 去掉
                        tmp_method = self.trimPreStr(result[3].replace(" ", "").replace("/", "."), '.')

                        if result[0] not in threads.keys():
                            continue
                        if not (threads[result[0]] in thread_time.keys()):
                            thread_time[threads[result[0]]] = 0
                        thread_time[threads[result[0]]] = int(result[2])
                        if re.search(WATCHER, tmp_method) is not None:
                            if not (tmp_method in method_thread.keys()):
                                method_thread[tmp_method] = threads[result[0]]
                        if result[0] in tmp.keys():
                            if len(tmp[result[0]]) != 0:
                                last_action = tmp[result[0]][-1]
                                if result[1] == "xit" and result[3] == last_action[2]:
                                    thread_time[threads[result[0]]] += int(result[2]) - int(last_action[1])
                                    tmp[result[0]].pop()
                            else:
                                if result[1] == "ent":
                                    tmp[result[0]].append((result[1], result[2], result[3]))
                        else:
                            if result[1] == "ent":
                                tmp[result[0]] = [(result[1], result[2], result[3])]

            return {value: key for key, value in threads.items()}, thread_time, method_thread
        except IOError:
            logger.error("The file don't exist, Please double check!")

    # 去掉前置的 .
    def trimPreStr(self, s, opt):
        length = len(s)
        i = 0
        while i < length:
            if s[i] == opt:
                i += 1
            else:
                break
        return s[i:length]

    def analysisTraceFile(self, fileName, mode):
        txt_file_name_g = fileName[:fileName.rfind('.')] + "_g.txt"
        if not os.path.exists(txt_file_name_g):
            os.system('dmtracedump -g a.png ' + fileName.replace("(", "\(").replace(")", "\)") + ' > '
                      + txt_file_name_g.replace("(", "\(").replace(")", "\)"))
        # 求exclusive time
        method_dict, exclusive_time_result = self.analysisExclusiveTime(txt_file_name_g)

        exclusive_time_items = sorted(exclusive_time_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        exclusive_time_result = {}
        max_record = min(len(exclusive_time_items), MAX_RECORD)
        for i in range(0, max_record):
            exclusive_time_result[exclusive_time_items[i][0]] = exclusive_time_items[i][1]

        # 求inclusive time
        parent_children, inclusive_time_result = self.analysisInclusiveTime(txt_file_name_g)
        inclusive_time_items = sorted(inclusive_time_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

        stack_hash_record = {}
        max_record = min(len(inclusive_time_items), 3)
        for i in range(0, max_record):
            stack_hash_record[i] = inclusive_time_items[i][0]

        max_record = min(len(inclusive_time_items), MAX_RECORD)
        inclusive_time_result = {}
        for i in range(0, max_record):
            inclusive_time_result[inclusive_time_items[i][0]] = inclusive_time_items[i][1]

        # 求调用次数和递归调用次数总和
        call_times_result = self.analysisCallTimes(txt_file_name_g)
        call_times_items = sorted(call_times_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        call_times_result = {}
        max_record = min(len(call_times_items), MAX_RECORD)
        for i in range(0, max_record):
            call_times_result[call_times_items[i][0]] = call_times_items[i][1]

        # 分析线程
        txt_file_thread_o = fileName[:fileName.rfind('.')] + "_o.txt"
        if not os.path.exists(txt_file_thread_o):
            os.system('dmtracedump -o ' + fileName.replace("(", "\(").replace(")", "\)") + ' > '
                      + txt_file_thread_o.replace("(", "\(").replace(")", "\)"))
        # method_stack,threads = self.analysiscCycleFunction(txt_file_thread_o)
        theads_pid, thead_time_result, method_thread = self.analysisTheadTime(txt_file_thread_o)
        thead_time_items = sorted(thead_time_result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        len_theads = len(thead_time_items)
        len_theads = min(len_theads, MAX_RECORD)
        thead_time_result = {}
        for i in range(0, len_theads):
            thead_time_result[thead_time_items[i][0]] = thead_time_items[i][1]

        final_inclusive_time_result, inclusive_costs = self.render_data(inclusive_time_result, parent_children,
                                                                        method_dict)
        final_exclusive_time_result, exclusive_costs = self.render_data(exclusive_time_result, parent_children,
                                                                        method_dict)

        final_thead_time_result = []

        for key, value in thead_time_result.items():
            if key in theads_pid.keys():
                final_thead_time_result.append({"name": theads_pid[key], "time": value})

        if mode == "inclusive":
            costs = inclusive_costs
        else:
            costs = exclusive_costs

        final_result = {
            "inclusive": final_inclusive_time_result,
            "exclusive": final_exclusive_time_result,
            "method_thread": method_thread,
            "theads_pid": theads_pid,
            "call_times": call_times_result,
            "costs": costs
        }

        return final_result

    def render_data(self, data, parent_children, methods):
        result = []
        cost_time = 0
        for key, value in data.items():

            if "aerie" in key:
                continue
            one_record = {}
            one_record['name'] = key
            one_record['time'] = value
            cost_time = cost_time + value
            parents = []
            children = []
            if key in parent_children.keys():
                for p_c in parent_children[key][0]:
                    parents.append(p_c)
                for p_c in parent_children[key][1]:
                    children.append(p_c)
                one_record['parents'] = parents
                one_record['children'] = children
            result.append(one_record)
        return result, cost_time


def sortInclThreadCost(result_dic, mode, sort):
    before_sort = {}
    sorted_tmp_dic = {}
    sorted_dic = {}
    for each_result in result_dic[mode]:
        before_sort[each_result["name"]] = each_result["time"]
    sorted_tmp_dic = sorted(before_sort.iteritems(), key=lambda d: d[1], reverse=True)
    # for key,value in sorted_tmp_dic:
    #     sorted_dic[key] = value
    if sort == False:
        return before_sort
    return sorted_tmp_dic
