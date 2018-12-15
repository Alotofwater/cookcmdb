from repository import models


class Nic(object):
    def __init__(self, server_obj, Nic_post):
        self.server_obj = server_obj  # 传入ORM对象
        self.Nic_post = Nic_post  # 传入post请求提交上来的数据

    def process(self):
        # 硬盘、网卡和内存
        new_nic_info_dict = self.Nic_post['data']  # 获取数据
        # print("new_nic_info_dict:Nic_post::",new_nic_info_dict)
        """
        'data': {
			'eth0': {
				'ipaddrs': '10.211.55.4',
				'up': True,
				'netmask': '255.255.255.0',
				'hwaddr': '00:1c:42:a5:57:7a'
			}
        """
        new_nic_info_list = self.server_obj.nic.all()  # 获取数据库里数据-存放都是数据对象
        # print("new_nic_info_list:::", new_nic_info_list)

        """
        [
            obj,
            obj,
            obj,
        ]
        """
        # new_nic_info_dict 插件提交的数据
        new_nic_name_set = set(new_nic_info_dict.keys())  # 集合去重 - keys() 以列表返回一个字典所有的键
        # print("new_nic_slot_set::", new_nic_name_set)

        # new_disk_info_list ORM数据列表- obj.name 获取网卡-网卡名
        old_nic_name_set = {obj.name for obj in new_nic_info_list}
        # print("old_nic_name_set", old_nic_name_set)
        # 需要添加的数据 - 存放着数据的new_nic_name_set字典中得key
        add_nic_name_list = new_nic_name_set.difference(old_nic_name_set)  # 使用集合difference-差集--我有你没有的，显示出来
        # print("add_nic_name_list:::",add_nic_name_list)

        # 需要删除的数据 -
        del_nic_name_list = old_nic_name_set.difference(new_nic_name_set)  # 使用集合difference-差集--我有你没有的，显示出来
        # 需要更新的数据
        update_nic_namet_list = old_nic_name_set.intersection(new_nic_name_set)  # intersection 交集
        # print("update_nic_namet_list", update_nic_namet_list)
        add_record_list = []  # 添加操作记录
        # 增加 [2,5]
        for nic_name in add_nic_name_list:  # 循环集合筛选出的数据 #
            value = new_nic_info_dict[nic_name]  # nic_name 是 new_nic_name_info_dict字典的key
            value["name"] = nic_name # 构造字典数据，里面是没有网卡名称，现在添加上网卡名称
            # print("添加value,写入数据：：：",value)
            tmp = "添加网卡..."
            add_record_list.append(tmp)  # 添加操作记录
            # server_obj是外键-指是哪个主机，
            value['server_obj'] = self.server_obj  # 把ORM对象存入到 new_nic_info_dict 中，方便一会写入数据
            models.NIC.objects.create(**value)  # 数据写入
        # 删除 [4,6] -- 根据网卡名
        models.NIC.objects.filter(server_obj=self.server_obj, name__in=del_nic_name_list).delete()

        # 更新 [7,8]
        for nic_name in update_nic_namet_list:
            value = new_nic_info_dict[nic_name]
            value["name"] = nic_name
            # print("更新value,写入数据：：：", value)
            obj = models.NIC.objects.filter(server_obj=self.server_obj, name=nic_name).first()
            for k, new_val in value.items():  # new_val post最新提交上来的数据
                old_val = getattr(obj, k)  # ORM对象中 查找 字段的值
                if old_val != new_val:  # 数据不相等，说明需要更新
                    setattr(obj, k, new_val)  # 更新数据
            obj.save()  # 保存数据

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
