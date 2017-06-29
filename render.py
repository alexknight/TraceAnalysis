# coding:utf-8

import collections
import csv
import os
from util.log import logger

logger = logger()


class Template(object):
    def __init__(self,
                 base_dic, cmp_dic,
                 base_cost, cmp_cost,
                 base_call_times, cmp_call_times,
                 base_method_thread, cmp_method_thread,
                 base_theads_pid, cmp_theads_pid):
        self.base = base_dic  # base_sorted_dic, cmp_sorted_dic, base_cost, cmp_cost,base_call_times,cmp_call_times
        self.cmp = cmp_dic
        self.base_cost = base_cost
        self.cmp_cost = cmp_cost
        self.base_call_times = base_call_times
        self.cmp_call_times = cmp_call_times
        self.order_base_dic = collections.OrderedDict()
        self.order_cmp_dic = collections.OrderedDict()
        self.order_base_keys, self.order_base_values = self.initObjDatas(self.base, self.order_base_dic)
        self.order_cmp_keys, self.order_cmp_values = self.initObjDatas(self.cmp, self.order_cmp_dic)
        self.base_method_thread = base_method_thread
        self.cmp_method_thread = cmp_method_thread
        self.base_theads_pid = base_theads_pid
        self.cmp_theads_pid = cmp_theads_pid

    def initObjDatas(self, obj, init_obj):
        _keys = []
        _values = []
        for each in obj:
            init_obj[each[0]] = each[1]
        for _k, _v in init_obj.items():
            _keys.append(_k)
            _values.append(_v)
        return _keys, _values

    def generateTable(self, path, rows, data):
        if os.path.isfile(path):
            os.remove(path)
        csvfile = file(path, "wb")
        writer = csv.writer(csvfile)
        # writer.writerow(rows)
        writer.writerows(data)
        csvfile.close()

    def searchDictList(self, orderDict):
        keys = []
        values = []
        for k, v in orderDict.items():
            keys.append(k)
            values.append(v)
        return keys, values

    def generateTableData(self, path, rows):
        ''' ['调用方法','隶属线程', '线程PID', '基准分支排名', '对比分支排名', '基准分支方法耗时', '对比分支方法耗时',
             '耗时差(对比分支-基准分支)', '耗时上涨比例(%)', '基准分支方法调用次数','对比分支方法调用次数','方法耗时排名变化'] '''
        logger.debug("self.cmp_cost:\n" + str(self.cmp_cost))
        logger.debug("self.base_cost:\n" + str(self.base_cost))
        if self.base_cost != 0:
            ratio = format(float(self.cmp_cost - self.base_cost) / float(self.base_cost), '.2%')
        else:
            ratio = self.cmp_cost
        data = []
        add_rows = rows
        add_rows[0] = add_rows[0] + "- 系数: " + str(ratio)
        add_flag = 0
        for cmp_obj in self.order_cmp_keys:
            ''' 当cmp_obj有新增方法时 '''
            if cmp_obj not in self.order_base_keys:
                add_flag = 1
                method = cmp_obj
                base_index = "-"
                cmp_index = self.order_cmp_keys.index(cmp_obj)
                base_time = 0
                cmp_time = self.order_cmp_values[cmp_index]
                cmp_call_times = self.cmp_call_times[cmp_obj] if self.cmp_call_times.has_key(cmp_obj) else "-"
                if self.cmp_method_thread.has_key(cmp_obj):
                    cmp_thread = self.cmp_method_thread[cmp_obj]
                    self.cmp_method_thread.pop(cmp_obj)
                else:
                    cmp_thread = "-"
                base_call_times = 0
                diff = cmp_time
                rate = format(float(1), '.2%')
                rank_change = cmp_index
                content = (
                    method, str(cmp_thread), str(base_index), str(cmp_index), str(base_time), str(cmp_time), str(diff),
                    str(rate), str(base_call_times), str(cmp_call_times), str(rank_change))
                data.append(content)
        if add_flag == 1:
            data.insert(0, add_rows)
        rows[0] = rows[0] + "- 系数: " + str(ratio)
        data.append(rows)
        for base_obj in self.order_base_keys:
            method = base_obj
            base_index = self.order_base_keys.index(base_obj)  # 获取base_key的排名
            if base_obj in self.order_cmp_keys:
                cmp_index = self.order_cmp_keys.index(base_obj)  # 当base_obj方法还在cmp_obj方法中
                base_call_times = self.base_call_times[base_obj] if self.base_call_times.has_key(base_obj) else "-"
                cmp_call_times = self.cmp_call_times[base_obj] if self.cmp_call_times.has_key(base_obj) else "-"
            else:
                cmp_index = "-"  # 当base_obj方法在cmp_obj已经删减
                base_call_times = self.base_call_times[base_obj] if self.base_call_times.has_key(base_obj) else "-"
                cmp_call_times = 0
            if self.base_method_thread.has_key(base_obj):
                base_thread = self.base_method_thread[base_obj]
                self.base_method_thread.pop(base_obj)
            else:
                base_thread = "-"

            base_time = self.order_base_values[base_index]
            if cmp_index == "-":
                cmp_time = 0
                rank_change = base_index
            else:
                cmp_time = self.order_cmp_values[cmp_index]
                rank_change = base_index - cmp_index
            diff = cmp_time - base_time
            try:
                rate = format(float(diff) / float(base_time), '.2%')  # -100%:代表base_obj方法在cmp_obj已经删减的比率
            except Exception as e:
                rate = "error"
            content = (
                method, str(base_thread), str(base_index), str(cmp_index), str(base_time), str(cmp_time), str(diff),
                str(rate), str(base_call_times), str(cmp_call_times), str(rank_change))
            data.append(content)
        self.generateTable(path, rows, data)
        logger.debug("self.base_cost-self.cmp_cost:\n" + str(self.base_cost - self.cmp_cost))
        logger.debug("self.base_method_thread:\n" + str(self.base_method_thread))
        logger.debug("self.cmp_method_thread:\n" + str(self.cmp_method_thread))
