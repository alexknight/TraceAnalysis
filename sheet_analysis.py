# coding:utf-8
import os

from config import config
from handler.trace import TraceHandler
from render import Template
from util import log

logger = log.logger()

csv_name = "result.csv"
csv_path = os.path.join(os.getcwd(), csv_name)

table_rows = ['调用方法', '隶属线程', '基准分支排名', '对比分支排名', '基准分支方法耗时', '对比分支方法耗时',
              '耗时差(对比分支-基准分支)', '耗时上涨比例(%)', '基准分支方法调用次数', '对比分支方法调用次数', '方法耗时排名变化']


def run():
    # 获取基准traceview的解析结果
    logger.info(u"开始解析: " + config.BASE_TRACES)
    base_results = TraceHandler(
        config.BASE_TRACES,
        convert_jar=config.ANTI_CONFUSE_TOOL,
        mapping_path=config.MAPPING_FILE).anti_mapping().analysis()

    # 获取当前traceview的解析结果
    logger.info(u"开始解析: " + config.BASE_TRACES)
    compare_results = TraceHandler(
        config.COMPARE_TRACES,
        convert_jar=config.ANTI_CONFUSE_TOOL,
        mapping_path=config.MAPPING_FILE).anti_mapping().analysis()

    # 生成csv结果
    template = Template(
        base_results["sorted_dic"], compare_results["sorted_dic"],
        base_results["costs"], compare_results["costs"],
        base_results["call_times"], compare_results["call_times"],
        base_results["method_thread"], compare_results["method_thread"],
        base_results["theads_pid"], compare_results["theads_pid"]
    )

    table_rows[0] += csv_name
    template.generateTableData(csv_path, table_rows)
    logger.info(u"结果已生成: " + csv_name)


if __name__ == '__main__':
    run()
