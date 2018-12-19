from django.conf import settings
from repository import models
import importlib
from .server import Server # 插件更新数据库


class PluginManger(object):

    def __init__(self):
        self.plugin_items = settings.PLUGIN_ITEMS
        self.basic_key = "basic"  # 系统基本信息
        self.board_key = "board"  # 主板信息

    def exec(self, server_dict):
        """

        :param server_dict:
        :return: 1,执行完全成功； 2, 局部失败；3，执行失败;4. 服务器不存在
        """
        ret = {'code': 1, 'msg': None}
        # 获取主机名
        hostname = server_dict[self.basic_key]['data']['hostname']
        # print("hostname_init:",hostname)
        server_obj = models.Server.objects.filter(hostname=hostname).first() # 根据主机名-查出对象

        # 没找到数据-代表服务器没有录入- 我们先要录入数据的主机名
        if not server_obj:
            ret['code'] = 4
            return ret
        # 不可插拔的插件-basic_key 系统基本信息  board_key 主板信息
        # 固定数据写入-数据库
        obj = Server(server_obj=server_obj, # ORM对象
                     basic_dict=server_dict[self.basic_key], # 系统基本信息
                     board_dict=server_dict[self.board_key]) # 主板信息
        obj.process()

        # 对比更新[硬盘，网卡，内存，可插拔的插件]
        for key, value in self.plugin_items.items(): #配置文件中得插件模块
            try:
                # 获取模板路径   方法名
                module_path, cls_name = value.rsplit('.', maxsplit=1)
                # print("module_path::",module_path,"----------cls_name:",cls_name)
                # 模块
                module_name = importlib.import_module(module_path)
                # 反射找到模块的下的方法-该方法是用类写的
                cls = getattr(module_name, cls_name)
                # 实例化 - server_obj查询ORM的对象- server_dict[key] post提交上的数据
                obj = cls(server_obj, server_dict[key])
                # 执行对象中得方法，有process-该方法是采集到数据。
                obj.process()
            except Exception as e:
                ret['code'] = 2

        return ret
