from repository import models


class Disk(object):
    def __init__(self, server_obj, disk_dict):
        self.server_obj = server_obj  # 传入ORM对象
        self.disk_dict = disk_dict  # 传入post请求提交上来的数据

    def process(self):
        # 硬盘、网卡和内存
        new_disk_info_dict = self.disk_dict['data']  # 获取数据
        """
        {
            '0': {'slot': '0', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'},
            '1': {'slot': '1', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH'},
            '2': {'slot': '2', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q'},
            '3': {'slot': '3', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAF912433K     Samsung SSD 840 PRO Series              DXM06B0Q'},
            '4': {'slot': '4', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAF303909M     Samsung SSD 840 PRO Series              DXM05B0Q'},
            '5': {'slot': '5', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series
        }"""
        new_disk_info_list = self.server_obj.disk.all()  # 获取数据库里数据-存放都是数据对象
        # print("new_disk_info_list::::::",new_disk_info_list)

        """
        [
            obj,
            obj,
            obj,
        ]
        """
        # new_disk_info_dict 插件提交的数据
        new_disk_slot_set = set(new_disk_info_dict.keys())  # 集合去重 - keys() 以列表返回一个字典所有的键
        # print("new_disk_slot_set::", new_disk_slot_set)

        # new_disk_info_list ORM数据列表- obj.slot 获取硬盘表的slot字段-插槽位
        old_disk_slot_set = {obj.slot for obj in new_disk_info_list}

        # add_slot_list = new_disk_slot_set - old_disk_slot_set
        # 需要添加的数据 - 存放着数据的new_disk_slot_set字典中得key
        add_slot_list = new_disk_slot_set.difference(old_disk_slot_set)  # 使用集合difference-差集--我有你没有的，显示出来
        # 需要删除的数据 - 根据插槽位
        del_slot_list = old_disk_slot_set.difference(new_disk_slot_set)  # 使用集合difference-差集--我有你没有的，显示出来
        # 需要更新的数据
        update_slot_list = old_disk_slot_set.intersection(new_disk_slot_set)  # intersection 交集

        add_record_list = []  # 添加操作记录
        # 增加 [2,5]
        for slot in add_slot_list:  # 循环集合筛选出的数据 #
            value = new_disk_info_dict[slot]  # slot 是 new_disk_info_dict字典的key
            tmp = "添加硬盘..."
            add_record_list.append(tmp)  # 添加操作记录
            # server_obj是外键-指是哪个主机，
            value['server_obj'] = self.server_obj  # 把ORM对象存入到new_disk_info_dict中，方便一会写入数据
            models.Disk.objects.create(**value)  # 数据写入
        # 删除 [4,6] -- 根据插槽位
        models.Disk.objects.filter(server_obj=self.server_obj, slot__in=del_slot_list).delete()

        # 更新 [7,8]
        for slot in update_slot_list:
            value = new_disk_info_dict[
                slot]  # {'slot': '0', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'}
            obj = models.Disk.objects.filter(server_obj=self.server_obj, slot=slot).first()
            for k, new_val in value.items():  # new_val post最新提交上来的数据
                old_val = getattr(obj, k)  # ORM对象中 查找 字段的值
                if old_val != new_val:  # 数据不相等，说明需要更新
                    setattr(obj, k, new_val) # 更新数据
            obj.save() # 保存数据

    def add_disk(self):
        '''
        手动添加
        :return:
        '''
        pass

    def del_disk(self):
        '''
        手动删除
        :return:
        '''
        pass

    def update_disk(self):
        '''
        手动更新
        :return:
        '''

        pass
