import functools  # 装饰器-传入的函数显示自己本身
from types import FunctionType  # 查看方法是不是函数类型
from django.conf.urls import url  # django中路由规则
from django.utils.safestring import mark_safe  # 将字符串 转义为 html
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse  # 反向解析
from django import forms  # 表单生成
from django.db.models import Q  # 复杂查询
from django.http import QueryDict  # GET或POST请求参数-是不能修改
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField  # 判断是不是一对一，多对多类型








class ModelConfigMapping(object):
    #
    def __init__(self, model, config, prev):
        '''
        :param model: ORM对象
        :param config: 实例化后StarkConfig对象
        :param prev: url上增加相关字符，组成新的url，细分权限
        '''
        self.model = model  # ORM对象
        self.config = config  # 配置文件
        self.prev = prev  #


def get_choice_text(field, head):
    """
    获取choice对应的中文内容
    用于每个app下的stark组件，在获取choice中文属性
    :param field:  字段名称
    :param head: 表头名称
    :return:
    """

    def inner(self, row=None, header=False): # row 是在 stark/templatetags/stark.py 中渲染 表格头
        if header:
            return head
        func_name = "get_%s_display" % field
        return getattr(row, func_name)()

    return inner


class Row(object):  # 处理组合按钮-代码渲染
    def __init__(self, data_list, option, query_dict):
        """
        元组
        :param data_list: 元组或queryset - Option 类中 ORM 查询出的数据
        :param option: Option类实例化对象本生 self
        :param query_dict: 用户提交GET数据
        """
        self.data_list = data_list
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):  # 实例化的对象 转换成迭代器
        yield '<div class="whole">'  # 生成器 一个next() 走一个 yield-然后就停住
        # 每次必走该代码
        tatal_query_dict = self.query_dict.copy()  # 深度拷贝query_dict-URL上的GET数据
        tatal_query_dict._mutable = True  # 允许修改URL上GET请求参数
        # origin_value_list 获取 URL 用户提交的参数， option.field 自定义 字段 在每个app应用下stark中 配置
        origin_value_list = self.query_dict.getlist(self.option.field)  # 用户提交的组合按钮选项- 用户提交的GET参数
        if origin_value_list:  # 为空，表示用户提交的get请求中的参数
            tatal_query_dict.pop(self.option.field)  # 做取消选中，组合按钮
            yield '<a href="?%s">全部</a>' % (tatal_query_dict.urlencode(),)  # 将URL中得参数转换成“k1=v1&k2=v2”  # 为选中状态
        else:
            yield '<a class="active" href="?%s">全部</a>' % (tatal_query_dict.urlencode(),)  # 选中状态

        yield '</div>'
        yield '<div class="others">'

        for item in self.data_list:  # item=(),queryset中的一个对象
            val = self.option.get_value(item)  # 获取到页面提交GET请求的 value值  一般是pk 主键
            text = self.option.get_text(item)  # 在页面上显示的文字

            query_dict = self.query_dict.copy()
            query_dict._mutable = True

            if not self.option.is_multi:  # 为空，表示不是多对多字段-单选
                if str(val) in origin_value_list:  # 自定义字段的value 是否 在 用户提交GET请求中
                    query_dict.pop(self.option.field)  # 做取消选中，组合按钮
                    # query_dict.urlencode() 转换成URL模式k=22&k=1  样式----text在页面上显示的文字
                    yield '<a class="active" href="?%s">%s</a>' % (query_dict.urlencode(), text)  # 选中状态
                else:
                    query_dict[self.option.field] = val
                    yield '<a href="?%s">%s</a>' % (query_dict.urlencode(), text)  # 未选中状态
            else:  # 多选
                multi_val_list = query_dict.getlist(self.option.field)  # 用户提交的GET参数、
                if str(val) in origin_value_list:
                    # 已经选，把自己去掉
                    multi_val_list.remove(str(val))
                    query_dict.setlist(self.option.field, multi_val_list)
                    yield '<a class="active" href="?%s">%s</a>' % (query_dict.urlencode(), text)
                else:
                    multi_val_list.append(val)
                    query_dict.setlist(self.option.field, multi_val_list)
                    yield '<a href="?%s">%s</a>' % (query_dict.urlencode(), text)

        yield '</div>'


class Option(object):  # 处理组合按钮-条件生成
    # 在每个app应用中实例化-处理组合按钮
    def __init__(self, field, condition=None, is_choice=False, text_func=None, value_func=None, is_multi=False,is_show=True):
        self.field = field  # ORM数据表字段-在app应用下 stark.py 自定义对哪个字段进行搜索
        self.is_choice = is_choice  # 判断是否是 choice 字段
        # app应用stark 自定义  DistinctNameOption('name',condition={'id__gt':9},value_func=lambda x:x[0],text_func=lambda x:x[0],),
        if not condition:  # 如果condition为空 # 该条件是app应用下 stark 自己定义条件，筛选显示几个组合按钮（二级按钮）
            condition = {}
        self.condition = condition  # ORM语句的过滤条件-用get请求方式传入
        self.text_func = text_func  # lambda匿名函数-- 显示按钮文本
        self.value_func = value_func  # lambda匿名函数-- 显示ID GET请求的参数把ID 传过去
        self.is_multi = is_multi  # 多对多ORM表操作
        self.is_show = is_show # 是否显示组合按钮

    def get_queryset(self, _field, model_class, query_dict):
        '''
        option.get_queryset(_field, self.config.model_class,self.config.request.GET)
        :param _field:  ORM表字段（ORM字段对象） ChangeList类下面生成的，
        :param model_class: # ORM类 - 用于数据查询
        :param query_dict: # 用户提交的GET请求数据  ChangeList类中处理得到的
        :return:
        '''
        # OneToOneField 继承 ForeignKey 所以这里不用判断OneToOneField 模式
        if isinstance(_field, ForeignKey) or isinstance(_field, ManyToManyField): # 如果一对一 或 多对多 字段
            # 根据自定义字段  通过rel（有外键关联时候用rel）查询该表数据  # self 对象本生
            row = Row(_field.rel.model.objects.filter(**self.condition), self, query_dict)
        else:
            if self.is_choice: # 如果自定义的ORM 字段 是 choice类型
                # _field.choices 是个元组数据，是ORM里的参数，定义着数字分别代表什么
                # self,query_dict用户提交的数据
                row = Row(_field.choices, self, query_dict)
            else:
                row = Row(model_class.objects.filter(**self.condition), self, query_dict)
        return row

    def get_text(self, item):  # 如果是item 是 ORM 查询出来的 对象数据
        '''
        获取2级按钮显示
        '''
        if self.text_func:  # text_func不为空--在app应用下的stark 自定义的匿名函数
            return self.text_func(item)  # text_func=lambda x:x.title（取title字段值），text_func=lambda x:x[1]（元组数据-取索引为1的）  这是参数x是Row类传入进来的
        return str(item)  # 如果没有的app应用下 stark.py 里自定义 那就输出  ORM 类中的 __str__ 并转换成字符串

    def get_value(self, item):
        '''
        :param item:   Row类里 查询出的数据对象
        :return: 每个按钮上的 value 值  ，用于用户提交GET请求时候带的
        '''
        if self.value_func:
            return self.value_func(item)  # 取ORM 数据对象
        if self.is_choice:  # 如果是choice
            return item[0]  # 显示元组索引0 # 是choice数字
        return item.pk  # 返回数据对象 主键ID 值


class ChangeList(object):
    """
    封装列表页面需要的所有功能
    """

    def __init__(self, config, queryset, q, search_list, page):
        self.q = q # 用户的查询条件- 组合按钮
        self.search_list = search_list # 可以模糊查询的字段，ORM
        self.page = page # 分页配置

        # func.__name__：函数名 func.text ， 给函数类添加的静态属性text
        # for func in config.get_action_list()  批量执行动作列表
        self.config = config # 对象配置文件--StarkConfig类的对象
        self.action_list = [{'name': func.__name__, 'text': func.text} for func in config.get_action_list()]
        # 添加按钮
        self.add_btn = config.get_add_btn()
        # model_class ORM 查询queryset数据类型，queryset列表中存放着查询出来的各个数据的对象
        self.queryset = queryset
        # 自定义显示哪些字段，组合成表格
        self.list_display = config.get_list_display()

        # 因为config是StarkConfig类的对象中寻找-每个app应用下自定的组合查询字段
        self.list_filter = config.get_list_filter()

    def gen_list_filter_rows(self):  # 数据渲染 组合搜索
        for option in self.list_filter: # 自定义组合查询字段列表 - list_filter在每个app下stark.py中编写的
            # .get_field(option.field) 获取字段的对象
            # .get_field(option.field).verbose_name 获取ORM参数中的verbose_name参数的值
            # 但是这里没有使用.verbose_name，所以他获取到的是该字段是什么类型（例如，一对一，多对多，一对多。。。ForeignKey）
            if not option.is_show:
                continue
            _field = self.config.model_class._meta.get_field(option.field)
            yield option.get_queryset(_field, self.config.model_class, self.config.request.GET)


class StarkConfig(object):
    '''
    stark的配置-如果需要有定制，需要重新写该类，或者继承该类
    '''

    def display_checkbox(self, row=None, header=False):
        if header:
            return "选择"
        return mark_safe("<input type='checkbox' name='pk' value='%s' />" % row.pk)

    def display_edit(self, row=None, header=False):
        if header:
            return "编辑"

        return mark_safe(
            '<a href="%s"><i class="fa fa-edit" aria-hidden="true"></i></a></a>' % self.reverse_edit_url(row))

    def display_del(self, row=None, header=False): # 类方法
        if header:
            return "删除"

        return mark_safe(
            '<a href="%s"><i class="fa fa-trash-o" aria-hidden="true"></i></a>' % self.reverse_del_url(row))

    def display_edit_del(self, row=None, header=False):
        if header:
            return "操作"
        tpl = """<a href="%s"><i class="fa fa-edit" aria-hidden="true"></i></a></a> |
        <a href="%s"><i class="fa fa-trash-o" aria-hidden="true"></i></a>
        """ % (self.reverse_edit_url(row), self.reverse_del_url(row),)
        return mark_safe(tpl)

    def multi_delete(self, request):
        """
        批量删除的action-动作
        :param request:
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete() # 删除数据
        # return HttpResponse('删除成功')

    multi_delete.text = "批量删除"  # 给函数对象添加text静态属性，用于在网页上中文显示
    order_by = []  # ORM排序-填写字段名
    list_display = []  # 自定义显示哪些字段，组合成表格
    # model_form_class 填写model_form类的字符串名称  在每个app中的stark插件中继承starkconfig类，编写一个model_form类。给model_form_class变量赋值，
    model_form_class = None
    action_list = []  # 批量操作的动作列表
    search_list = []  # 搜索查询字段，连表字段
    list_filter = []  # 多条件组合搜索条件 - 在每个app中的stark插件中继承starkconfig类，重写 list_filter

    # 2018年11月25日 00:08:12 添加执行增删改查url附带钩子脚本
    script_state_add = False
    script_state_delete = False
    script_state_change = False


    def __init__(self, model_class, site, prev):
        self.model_class = model_class  # ORM表的类名
        self.site = site  # 实例化后AdminSite的对象--
        self.prev = prev  # 拼接url-细分权限
        self.request = None  # request请求

        self.back_condition_key = "_filter"  # 历史的url记录


    def get_order_by(self):
        '''
        ORM查询出的数据进行排序
        该方法可以重新编写
        '''
        return self.order_by

    def get_list_display(self):
        '''
        从写该方法，用RBAC -- session中得权限，判断是否有该权限
        自定义显示哪些字段，组合成表格
        该方法可以重新编写 - 作为权限管理
        '''
        val = []
        val.append(StarkConfig.display_checkbox)
        val.extend(self.list_display)
        val.append(StarkConfig.display_edit)
        val.append(StarkConfig.display_del)
        return val

    def get_add_btn(self):
        '''
        添加-给数据库增加数据
        '''

        return mark_safe('<a href="%s" class="btn btn-success">添加</a>' % self.reverse_add_url())

    def get_model_form_class(self):
        """
        获取ModelForm类 - 渲染 html 表单页面 录入数据中
        :return:
        """
        if self.model_form_class: # 如果自定义了model_form 就用自己的
            return self.model_form_class

        class AddModelForm(forms.ModelForm): # 默认使用全局
            class Meta:
                model = self.model_class
                fields = "__all__" # 显示所有字段

        return AddModelForm

    def get_action_list(self):
        '''
        批量操作按钮 - 表格中的表头按钮
        '''
        val = [] # 获取数据的PK值，
        val.extend(self.action_list)  # 合并批量操作
        return val

    def get_action_dict(self):
        '''
        执行批量动作 数据选中后 - 批量删除....等
        '''
        val = {}
        for item in self.action_list:
            val[item.__name__] = item  # 执行批量动作
        return val

    def get_search_list(self):
        '''
        搜索条件 按照字段名 或者 能查询连表字段
        '''
        val = []
        val.extend(self.search_list)
        return val

    def get_search_condition(self, request):
        # 获取索条件
        search_list = self.get_search_list()  # ['name','tel']
        # 获取用户搜索条件 q 是key，如果没有value那就是空
        q = request.GET.get('q', "")  # ‘大’
        con = Q()  # con实例化Q类 Q是多个条件时候使用
        con.connector = "OR"  # 多个条件用 或
        if q:  # 如果 用户 提交搜索 条件
            for field in search_list:  # 可以查询的字段 循环
                # '%s__contains'：模糊 field 字段名 q：用户提交查询条件
                con.children.append(('%s__contains' % field, q))
        # 返回 search_list：查询字段列表，q：用户提交查询，con：对象 查询条件
        return search_list, q, con

    def get_list_filter(self):
        '''
        组合按钮搜索条件
        '''
        val = []
        val.extend(self.list_filter)  # self.list_filter 需要自己在每个app下重新编写
        return val

    def get_list_filter_condition(self):
        '''
        组合按钮搜索条件处理
        '''
        comb_condition = {}  # 条件字典
        for option in self.get_list_filter():  # 循环条件
            # option 是一个一个对象，Option类（封装数据，并对数据有相应处理方法与函数）
            # option.field 获取 ORM表的字段名
            element = self.request.GET.getlist(option.field)  # URL种有 field 名，获取值
            if element:  # 如果URL中有field值
                # 例如  comb_condition['company__in'] = '1'
                comb_condition['%s__in' % option.field] = element
        return comb_condition  # 返回条件字典

    def get_queryset(self):
        '''
        获取组合搜索筛选
        '''
        return self.model_class.objects

    def changelist_view(self, request):
        """
        视图的get请求-list
        所有URL的查看列表页面
        """
        # POST请求
        if request.method == 'POST':
            # action获取用户选择的批量动作
            action_name = request.POST.get('action')
            # 获取执行动作 key 函数名  value 函数本身
            action_dict = self.get_action_dict()
            # 判断用户提交请求是否在执行动作里面  因为后面要用反射执行方法，所有要判断，不然有黑客攻击，尝试提交各种方法动作
            if action_name not in action_dict:
                return HttpResponse('非法请求')
            # self 对象本生    action_name：函数名（该函数需要自己在每个app下stark组件编写）  传入参数 request请求体
            response = getattr(self, action_name)(request)  # 拿到处理结果-响应体  self starkconfig对象

            if response:  # 响应体内容存在
                return response  # 返回数据给用户

        # ##### 处理搜索 #####
        search_list, q, con = self.get_search_condition(request)

        # ##### 处理分页 #####
        from stark.utils.pagination import Pagination
        # filter 接收 查询条件 显示数据 count() 将查询出来的数据计算条数， 用于分页
        total_count = self.model_class.objects.filter(con).count()
        # 复制GET请求的数据
        query_params = request.GET.copy()  # 保修搜索条件
        # 可以修改用户提交的请求体数据
        query_params._mutable = True
        # 分页实例
        # request.GET.get('page')：用户选择的页码数 # total_count：数据总条数 # request.path_info：URL # query_params：用户提交的所有GET请求数据 # per_page：每页显示的数量
        page = Pagination(request.GET.get('page'), total_count, request.path_info, query_params, per_page=7)

        # list_filter = self.get_list_filter() # 试试用到没，先注释了

        # 获取组合搜索筛选
        origin_queryset = self.get_queryset()

        # queryset（queryset数据数据类型-当作列表使用） 根据查询条件进行显示数据    [page.start:page.end]：列表切片操作 显示多少数据
        # 在组合查询中添加distinct-为了数据去重
        # 而且该连表查询：inner join
        queryset = origin_queryset.filter(con).filter(**self.get_list_filter_condition()).order_by(
            *self.get_order_by()).distinct()[page.start:page.end]

        # cl实例化ChangeList列表页面所有功能
        # config = self 对象本身（实例化：StarkConfig） #q：用户提交查询 #search_list：查询字段列表 # page：分页对象
        cl = ChangeList(self, queryset, q, search_list, page)

        # 字典是要传给前端模板中做渲染用的
        context = {
            'cl': cl
        }
        return render(request, 'stark/changelist.html', context)

    def save(self, form, modify=False):
        """
        表单修改完毕，保存
        :param modify: True,表示要修改；False新增
        :return:
        """
        return form.save()

    def hookscript_add(self,*args,**kwargs):
        '''
        添加后执行的动作
        :param args:
        :param kwargs:
        :return:
        '''
        pass


    def add_view(self, request):
        """
        所有添加页面，都在此函数处理 - 增加
        使用ModelForm实现
        """

        AddModelForm = self.get_model_form_class()  # ModelForm类
        if request.method == "GET":
            form = AddModelForm()  # 实例化ModelForm
            return render(request, 'stark/change.html', {'form': form})

        form = AddModelForm(request.POST)
        if form.is_valid():
            self.save(form, modify=False)
            if self.script_state_add:
                self.hookscript_add()
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def hookscript_change(self,*args,**kwargs):
        '''
        修改后执行的动作
        :param args:
        :param kwargs:
        :return:
        '''
        pass

    def change_view(self, request, pk):
        """
        所有编辑页面
        """
        # model_class 是 ORM 类
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse('数据不存在')

        ModelFormClass = self.get_model_form_class()
        if request.method == 'GET':
            form = ModelFormClass(instance=obj)
            return render(request, 'stark/change.html', {'form': form})
        form = ModelFormClass(data=request.POST, instance=obj)
        if form.is_valid():
            self.save(form)
            if self.script_state_change:
                ret = self.hookscript_change(pk=pk)
                if ret:
                    return redirect('%s' %(ret))
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def hookscript_delete(self,*args,**kwargs):
        '''
        删除后执行的动作
        :param args: 
        :param kwargs: 
        :return: 
        '''
        pass

    def delete_view(self, request, pk):
        """
        所有删除页面
        """
        if request.method == "GET":
            # render返回页面，通过reverse_list_url()获取删除的url地址
            return render(request, 'stark/delete.html', {'cancel_url': self.reverse_list_url()})
        # model_class代表ORM对象
        self.model_class.objects.filter(pk=pk).delete()
        if self.script_state_delete:
            self.hookscript_delete(pk=pk)
        return redirect(self.reverse_list_url())

    def wrapper(self, func):
        # 装饰的是视图函数，每次请求来，到是视图函数都有request请求体，而视图函数被装饰器装饰，所以装饰器先拿到request
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request  # request 请求体 赋值给 self.request
            # 被装饰的函数前的操作动作
            ret = func(request, *args, **kwargs)
            # 被装饰的函数后的操作动作
            return ret

        return inner

    def get_urls(self):  # 添加路由关系
        # AdminSite中是生成的url(r'^stark/', include('rbac.urls', namespace='rbac'))
        #
        urlpatterns = [
            # wrapper 是装饰器，不用语法糖@
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^(?P<pk>\d+)/change/', self.wrapper(self.change_view), name=self.get_change_url_name),
            url(r'^(?P<pk>\d+)/del/', self.wrapper(self.delete_view), name=self.get_del_url_name),
        ]

        extra = self.extra_url()  # url合并-添加额外url
        if extra:  # 如果有值
            urlpatterns.extend(extra)  # 将额外url

        return urlpatterns

    def extra_url(self):  # 添加额外url - 钩子
        pass

    @property
    def get_list_url_name(self):
        '''
        get请求的url连接拼接- name别名  反向解析用到
        '''
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_changelist' % (app_label, model_name, self.prev)  # url细分权限
        else:
            name = '%s_%s_changelist' % (app_label, model_name) # namespace命名空间-反向解析
        return name

    @property
    def get_add_url_name(self):
        '''

        添加按钮
        '''
        app_label = self.model_class._meta.app_label  # 获取app名称
        model_name = self.model_class._meta.model_name  # 获取表名-小写
        if self.prev:
            name = '%s_%s_%s_add' % (app_label, model_name, self.prev)  # url细分权限 添加细节的url连接-比如（单独属于某个用户组 拥有权限）
        else:
            name = '%s_%s_add' % (app_label, model_name)
        return name

    @property
    def get_change_url_name(self):
        '''
        改url拼接
        :return:
        '''
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_change' % (app_label, model_name, self.prev)  # url细分权限
        else:
            name = '%s_%s_change' % (app_label, model_name)
        return name

    @property
    def get_del_url_name(self):  # get请求列表页面URL拼接
        '''
        删除url拼接
        '''
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_del' % (app_label, model_name, self.prev)  # url细分权限
        else:
            name = '%s_%s_del' % (app_label, model_name)
        return name

    def reverse_list_url(self):  # get请求列表页面URL拼接

        namespace = self.site.namespace
        name = '%s:%s' % (namespace, self.get_list_url_name)
        list_url = reverse(name)

        origin_condition = self.request.GET.get(self.back_condition_key) # 历史的url参数记录
        if not origin_condition:
            return list_url

        list_url = "%s?%s" % (list_url, origin_condition,)
        return list_url

    def reverse_add_url(self):  # post添加数据页面URL拼接
        namespace = self.site.namespace
        # 反向解析配置：字符串拼接
        name = '%s:%s' % (namespace, self.get_add_url_name)
        add_url = reverse(name)

        if not self.request.GET:
            return add_url

        # 获取当前URL搜索条件数据，GET请求中，而数据保存成 # q=嘉瑞&page=2 URL 上怎么显示的，这里就怎么赋值给param_str
        param_str = self.request.GET.urlencode()  # q=嘉瑞&page=2
        # 实例化QueryDict类，mutable=True可以修改用户提交过来的数据
        new_query_dict = QueryDict(mutable=True)
        # 在用户提交过来的数据QueryDict中，添加key与value  back_condition_key写死的key
        new_query_dict[self.back_condition_key] = param_str
        # 拼接出新的url，在有参数的URL--保留搜索删除
        add_url = "%s?%s" % (add_url, new_query_dict.urlencode(),)

        return add_url

    def reverse_edit_url(self, row):  # 编辑url
        namespace = self.site.namespace
        name = '%s:%s' % (namespace, self.get_change_url_name)  #
        edit_url = reverse(name, kwargs={'pk': row.pk})

        if not self.request.GET:
            return edit_url
        param_str = self.request.GET.urlencode()  # q=嘉瑞&page=2
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        edit_url = "%s?%s" % (edit_url, new_query_dict.urlencode(),)

        return edit_url

    def reverse_del_url(self, row):
        namespace = self.site.namespace
        name = '%s:%s' % (namespace, self.get_del_url_name)
        del_url = reverse(name, kwargs={'pk': row.pk})

        if not self.request.GET:
            return del_url
        param_str = self.request.GET.urlencode()  # q=嘉瑞&page=2
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        del_url = "%s?%s" % (del_url, new_query_dict.urlencode(),)

        return del_url

    @property  # 实例化对象  ： 当作静态属性
    def urls(self):  # 配置url
        return self.get_urls()  # 返回拼接好的url


class AdminSite(object):
    def __init__(self):
        '''
        _registry: 存放app应用调用stark组件存放的数据-实例化的对象
        app_name：app名称
        namespace：命名空间
        '''

        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, stark_config=None, prev=None):
        ''''
        model_class：ORM中的model类
        stark_config：每个app中stark自定义配置方法-先继承StarkConfig类，在这个基础上修改
        prev:前缀在url上面进行修改--是为了让操作同一张表-但是表中得某些字段不显示，只针对用户的权限显示
        '''
        # 判断每个app是否有自己的自定义方法，如果没有，用默认的配置方法
        if not stark_config:
            # StarkConfig 是 默认写死的配置方法- 选择编辑-删除等-如果需要添加自己的方法，需要重新编写StarkConfig， 在实例化Option类
            # stark_config是一个类
            stark_config = StarkConfig
        '''
        ModelConfigMapping 实例化
        model = model_class：ORM类
        config = stark_config：实例化 StarkConfig 类 - 传入 model_class：ORM类， self：对象自己本身 prev：url拼接用到
        prev = prev ： url拼接 - 权限细分
        将这些数据加入到_registry列表中
        '''
        self._registry.append(
            # 实例化Starkconfig类，self 是AdminSite的对象
           ModelConfigMapping(model=model_class, config=stark_config(model_class, self, prev), prev=prev))

    def get_urls(self):
        '''
        所有url汇总
        '''

        urlpatterns = []
        '''
        _registry：每个app调用stark组件 实例化 的数据
        app_label：获取APP的名称 
        model_name：获取ORM中的class的小写名称，表名
        '''
        for item in self._registry:
            '''
            item：代表一个实例化Starkconfig的对象
            '''
            app_label = item.model._meta.app_label
            model_name = item.model._meta.model_name
            if item.prev:
                '''
                r'^%s/%s/%s/' % (app_label, model_name, item.prev) app名称+表名构建路由正则+细分权限名称
                prev：url修改，一般用于一张表细分显示哪些字段。编辑哪些字段                       
                '''
                temp = url(r'^%s/%s/%s/' % (app_label, model_name, item.prev), (item.config.urls, None, None))
            else:
                # r'^%s/%s/' % (app_label, model_name,) app名称+表名构建路由正则
                # (item.config.urls, None, None) include 路由分发的返回值 - 三个元素 urlpatterns 列表（），app名称 路由命名空间
                # item.config.urls  - config代表StarkConfig实例化的对象   urls代表：StarkConfig实例化的对象的urls方法

                # 因为include方法返回的是元组，中间有三个参数
                # (
                # [url(r'^login/路径', views.login-视图函数,name="别名"),
                # None, # 参数2 - app名称
                # namespace="rbac") # url命名空间
                # (item.config.urls, None, None) # 就是include，下发到app中url地址
                temp = url(r'^%s/%s/' % (app_label, model_name,), (item.config.urls, None, None)) #生成
            urlpatterns.append(temp)
        return urlpatterns

    @property
    def urls(self): #根url配置汇总,生成
        # include-以元祖形式，返回的三个元素- urlpatterns列表，  app名称  路由命名空间
        return self.get_urls(), self.app_name, self.namespace


# 被其他app引入进去
# site-它是一个单例模式
# 调用site对象中的register方法 传入 ORM中class_model类
# site.register(models.Department（ORM中得类）, DepartmentConfig（自定义表头显示的内容）)
site = AdminSite()
