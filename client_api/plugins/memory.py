from repository import models


class Memory(object):
    def __init__(self, server_obj, post_dict):
        self.server_obj = server_obj  # 传入ORM对象
        self.post_dict = post_dict  # 传入post请求提交上来的数据

    def process(self):
        # 硬盘、网卡和内存
        new_post_info_dict = self.post_dict['data']  # 获取数据
        print("内存:post_dict::",new_post_info_dict)

        # 获取数据库里数据-存放都是数据对象-memory是 Memory 类中 ORM别名
        orm_obj_list = self.server_obj.memory.all()
        print("orm_obj_list:::", orm_obj_list)

        # new_post_info_dict 插件提交的数据
        new_psot_key_set = set(new_post_info_dict.keys())  # 集合去重-key代表可插拔的数据 - keys() 以列表返回一个字典所有的键
        print("new_psot_key_set::", new_psot_key_set)

        # orm_obj_list  ORM数据列表- obj.slot 获取网卡-网卡名  生成集合
        old_post_name_set = {obj.slot for obj in orm_obj_list}
        print("old_post_name_set", old_post_name_set)

        # 需要添加的数据 - 存放着数据的 new_psot_key_set 字典中得key
        add_post_name_list = new_psot_key_set.difference(old_post_name_set)  # 使用集合difference-差集--我有你没有的，显示出来
        print("add_post_name_list:::",add_post_name_list)

        # 需要删除的数据 -
        del_post_name_list = old_post_name_set.difference(new_psot_key_set)  # 使用集合difference-差集--我有你没有的，显示出来
        # 需要更新的数据
        update_post_namet_list = old_post_name_set.intersection(new_psot_key_set)  # intersection 交集
        print("update_post_namet_list", update_post_namet_list)
        add_record_list = []  # 添加操作记录
        # 增加 [2,5]
        for nic_name in add_post_name_list:  # 循环集合筛选出的数据 #
            value = new_post_info_dict[nic_name]  # nic_name 是 new_nic_name_info_dict字典的key

            print("内存添加value,写入数据：：：",value)
            tmp = "添加网卡..."
            add_record_list.append(tmp)  # 添加操作记录
            # server_obj是外键-指是哪个主机，
            value['server_obj'] = self.server_obj  # 把ORM对象存入到 new_post_info_dict 中，方便一会写入数据
            models.Memory.objects.create(**value)  # 数据写入
        # 删除 [4,6] -- 根据网卡名 -- slot__in 参数修改修改
        models.Memory.objects.filter(server_obj=self.server_obj, slot__in=del_post_name_list).delete()

        # 更新 [7,8]
        for nic_name in update_post_namet_list:
            value = new_post_info_dict[nic_name]

            print("内存更新value,写入数据：：：", value)
            obj = models.Memory.objects.filter(server_obj=self.server_obj, slot=nic_name).first()
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
