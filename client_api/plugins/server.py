from repository import models
import datetime
import pytz
import logging
logger = logging.getLogger('django_default')
class Server(object):

    def __init__(self, server_obj, basic_dict, board_dict):
        self.server_obj = server_obj  # ORM 查出 主机 对象
        self.basic_dict = basic_dict  # 系统基本信息-字典
        self.board_dict = board_dict  # 主板基本信息- 字典

    def process(self,):
        # 更新server表
        tmp = {}
        tmp.update(self.basic_dict['data'])  # 获取系统基本数据
        tmp.update(self.board_dict['data'])  # 获取主板信息
        logger.debug("更新server表: %s" %(tmp))
        # 服务器数据更新
        tmp.pop('hostname') # 取出host主机名字段
        record_list = [] # 日志列表
        # 导入 事务 模块
        from django.db import transaction

        try:
            # 可回滚 -- 执行的是系统与主板信息收集--这些是不可插拔的东西
            with transaction.atomic():  # django 事务
                for k, new_val in tmp.items():  # 将字典拆分成(key,value) # 字典key就是Server表中字段
                    old_val = getattr(self.server_obj, k)  # 查询到老数据

                    if old_val != new_val: # 新老数据对比数据
                        # print("old_valiude", k, old_val)
                        # 日志记录
                        record = "[%s]的[%s]由[%s]变更为[%s]" % (self.server_obj.hostname, k, old_val, new_val)

                        record_list.append(record) # 日志记录列表
                        # 修改数据-将老数据替换成新数据
                        setattr(self.server_obj, k, new_val) # 类中添加静态属性或去修改属性， 相当于 self.key = value

                self.server_obj.latest_date = datetime.datetime.now(pytz.utc) # 修改时间
                logger.debug("更新server表事务日志: %s" % (self.server_obj.sn))
                self.server_obj.save() # 保存数据

            if record_list:
                # sever_obj 关联表  # ";" 代表的换行
                # print("recordrizhi ::因为要关联用户-现在不能写入数据库::", record_list)
                models.ServerRecord.objects.create(server_obj=self.server_obj, content=';'.join(record_list))
        except Exception as e:
            logger.info("更新server表报错%s" %(e))
