## 图像标注API说明

by fengjie@codvision

### 定义

ip      api的ip地址

port    访问api的端口

xxx     实际中使用不同的字符串

info    错误信息字符串

### 文件相关API

* 文件夹浏览

    http://ip:port/api/getdir?usrname=xxx&taskname=xxx&start=xxx&num=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          start 图片开始index，从1开始计数
          
          num 图片浏览的个数 

    返回：
    
          成功： 服务器文件夹下相应文件列表（json格式）
          
          失败： ‘error：’ + info
          
* 按tag浏览(仅管理用户和超级用户)

    http://ip:port/api/getdir?usrname=xxx&taskname=xxx&start=xxx&num=xxx

    methods: post
    
    Content-Type: text/plain
    
    data内容： {"tag":xxx}
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          start 图片开始index，从1开始计数
          
          num 图片浏览的个数 

    返回：
    
          成功： 服务器文件夹下相应文件列表（json格式）
          
          失败： ‘error：’ + info

* 上传文件
    
    http://ip:port/api/uploadfile?usrname=xxx&taskname=xxx&filename=xxx

    methods: post
    
    data内容： ‘file’：文件数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 待上传文件名
          
    返回：
    
          成功： 上传文件地址
          
          失败： ‘error：’ + info

* 上传视频文件（用于视频分类任务）
    
    http://ip:port/api/uploadvideofile?usrname=xxx&taskname=xxx&filename=xxx

    methods: post
    
    data内容： ‘file’：文件数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 待上传文件名 （允许的视频后缀：mp4, avi, mpg, ts）
          
    返回：
    
          成功： 上传文件地址，服务器端对非mp4文件自动进行转码
          
          失败： ‘error：’ + info

* 上传视频文件并解码成图像（用于非视频分类任务）
    
    http://ip:port/api/uploadvideo2image?usrname=xxx&taskname=xxx&filename=xxx&interval=x

    methods: post
    
    data内容： ‘file’：文件数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 待上传文件名 （允许的视频后缀：mp4, avi, mpg, ts）

          interval 时间间隔，以秒为单位，代表从视频中间隔x秒取一张图片
          
    返回：
    
          成功： 上传文件地址，服务器端自动对视频进行解码并生成jpg图片
          
          失败： ‘error：’ + info


* 通过url上传文件
    
    http://ip:port/api/uploadurlfile?usrname=xxx&taskname=xxx

    methods: post
    
    data内容： json数据

	例如： {"url":"http://c.hiphotos.baidu.com/image/h%3D300/sign=93f9c659b91bb0519024b528067bda77/0df3d7ca7bcb0a46c89141426163f6246b60af1e.jpg"}
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          
    返回：
    
          成功： ‘OK’
          
          失败： ‘error：’ + info

* 通过搜索引擎爬取图片
    
    http://ip:port/api/scrapyimg?usrname=xxx&taskname=xxx

    methods: post
    
    data内容： 

	例如： {"engine":"baidu", "keyword":"狗", "start":1, "num": 50} 分别为搜索引擎（目前只支持baidu和sougou），关键字，起始序号，下载数量
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
    返回：
    
          成功： ‘OK’
          
          失败： ‘error：’ + info

* 自动删除相同文件

    http://ip:port/api/delsamefile?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          
    返回：
    
          成功： ‘OK’
          
          失败： ‘error：’ + info

* 删除文件

    http://ip:port/api/delfile?usrname=xxx&taskname=xxx&filename=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 待删除文件名
          
    返回：
    
          成功： 服务器文件夹目录（绝对路径）
          
          失败： ‘error：’ + info


* 文件个数查询

    http://ip:port/api/filecount?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名  

    返回：
    
          成功： 服务器文件夹下的图片个数
          
          失败： -1
    
    
* 已经标注的文件个数查询

    http://ip:port/api/labeledfilecount?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名  

    返回：
    
          成功： 服务器文件夹下已标注的图片个数
          
          失败： -1
    
    
### 标注相关API

* 保存标注结果

    http://ip:port/api/savelabel?usrname=xxx&taskname=xxx&filename=xxx

    methods: post
    
    Content-Type: text/plain
    
    data内容： 标注json数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 标注的文件名
          
    返回：
    
          成功：文件的标注数据（json格式）
          
          失败： ‘error：’ + info

* 载入标注结果

    http://ip:port/api/loadlabel?usrname=xxx&taskname=xxx&filename=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 标注的文件名
          
    返回：
    
          成功：文件的标注数据（json格式）
          
          失败： ‘error：’ + info

* 保存taglist

    http://ip:port/api/savetag?usrname=xxx&taskname=xxx

    methods: post
    
    Content-Type: text/plain
    
    data内容： taglist json数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          
    返回：
    
          成功：taglist json数据
          
          失败： ‘error：’ + info

* 载入taglist

    http://ip:port/api/loadtag?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
    返回：
    
          成功：taglist json数据
          
          失败： ‘error：’ + info
          
* 修改tag

    http://ip:port/api/changetag?usrname=xxx&taskname=xxx

    methods: post
    
    Content-Type: text/plain
    
    data内容： {"oldtag": xxx, "newtag":xxx}
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
    返回：
    
          成功：“OK”
          
          失败： ‘error：’ + info
          
          
* 获取标记统计信息

    http://ip:port/api/labelstatistics?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
    返回：
    
          成功：统计信息数据
          
          失败： ‘{}’

* 获取标记统计信息柱状图

    http://ip:port/api/labelstatisticsfig?usrname=xxx&taskname=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
    返回：
    
          成功：图片url
          
          失败： ‘’
          
          
### 任务相关API 

* 获取任务列表

    http://ip:port/api/gettasklist?usrname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
    返回：
    
          成功： 任务列表
          
                    例如：((u'task1', u'2017-07-28 09:42:55', 0.0, 0L, 0L， 1L), (u'task1', u'2017-07-28 09:43:12', 0.0, 0L, 0L，0L)) 分别为：任务名称，建立时间， 进度， 状态， 类型， 是否训练过
          
          失败： （）
    
    
* 添加任务
    
    http://ip:port/api/addtask?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info
          
* 查看可接收任务的用户名列表

    http://ip:port/api/distrableuserlist?usrname=xxx
    
    methods: get
    
    参数：
    
        usrname 分配任务的用户名
        
    返回：
    
          成功： 可接收任务的用户列表
          
                例如：[(u'aaaa', 0L), (u'test', 0L), (u'test1', 0L), (u'test3', 0L), (u'dly1', 0L), (u'arlose', 0L)] 分别为：用户名， 用户级别
          
          失败： []

* 查看已接收任务的用户名列表

    http://ip:port/api/distreduserlist?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 分配任务的用户名
        
        taskname 任务名
        
    返回：
    
          成功： 可接收任务的用户列表
          
          失败： （）
          
* 分配任务给其他用户

    http://ip:port/api/distributetask?usrname=xxx&taskname=xxx&distusrname=xxx&start=xxx&num=xxx
    
    methods: get
    
    参数：
    
        usrname 分配任务的用户名
        
        taskname 任务名
        
        distusrname 接收任务的用户名
        
        start 图片开始index，从1开始计数
          
        num 图片浏览的个数 
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info
          
* 取消分配任务

    http://ip:port/api/undistributetask?usrname=xxx&taskname=xxx&distusrname=xxx
    
    methods: get
    
    参数：
    
        usrname 分配任务的用户名
        
        taskname 任务名
        
        distusrname 接收任务的用户名
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info

* 移动或复制任务数据（超级用户,管理用户权限）

    http://ip:port/api/transfertaskdata
    
    methods: post

    参数：
        
        taskname 任务名

	start 图像起始序号

	num 图像数量（默认为所有数据）

	trasferusrname 移动或复制目标用户名（管理用户目标用户名仅为用户组内用户，超级用户目标用户名可为所有用户）

	trasfertaskname 移动或复制目标任务名

	isLabel 是否移动或复制标注数据（0代表不移动或复制标注数据，1代表移动或复制标注数据）

	isCopy 是否复制数据（0代表不保留原始数据，即移动，1代表保留原始数据，即复制）
        
    data内容： 超级用户或管理用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
    
        
    返回：
          成功： ‘OK’
          失败： ‘Fail’

          
* 删除任务

    http://ip:port/api/deltask?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info
          
* 开启训练

    http://ip:port/api/starttask?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info
          
* 终止训练

    http://ip:port/api/stoptask?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 任务列表
          
          失败： ‘error：’ + info

* 获取已有模型结构

    http://ip:port/api/taskinfostructure?usrname=xxx&taskname=xxx

    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
          成功： 已有模型结构列表，例如["yolo2", "SSD"]
          
          失败： ‘error：’ + info

* 查看任务训练状态

    http://ip:port/api/taskinfo?usrname=xxx&taskname=xxx&structure=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名

	structure 模型结构
        
    返回：
          成功： 图片url
          
          失败： ‘error：’ + info

* 查看任务训练log

    http://ip:port/api/tasklog?usrname=xxx&taskname=xxx&structure=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名

	structure 模型结构
        
    返回：
          成功： 'log info'
          
          失败： ‘error：’ + info


* 查看训练任务（超级用户权限）

    http://ip:port/api/gettrainingtaskinfo
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
    
        
    返回：
          成功： 任务列表，例如'[[(u'fj', u'task1', u'2017-07-28 14:42:19', 0L, 0L， 1L), (u'fj', u'task6', u'2017-08-01 11:22:10', 0L, 0L， 0L)]'分别为用户名，任务名，创建时间，任务类型，任务状态， 是否训练过
          
          失败： ‘{}’

* 获取默认训练参数

    http://ip:port/api/getdefaulttrainparams?usrname=xxx&taskname=xxx&structure=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名

	structure 模型结构
        
    返回：
    
          成功： 默认训练参数json数据，例如“{"structure":"yolo2", "epoch":5000, "optimizer":"SGD", "batchsize":64,"learningrate":0.0001,"momentum":0.9,"weightdecay":0.0005, "Retrain": 0, "pretrainmodel": "test1.param"}”
          
          失败： ‘{}’ 

* 获取训练参数

    http://ip:port/api/gettrainparams?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 训练参数json数据，例如“{"structure":"yolo2", "epoch":5000, "optimizer":"SGD", "batchsize":64,"learningrate":0.0001,"momentum":0.9,"weightdecay":0.0005, "Retrain": 1, "pretrainmodel": "test1.param"}”
          
          失败： ‘{}’


* 保存训练参数

    http://ip:port/api/savetrainparams?usrname=xxx&taskname=xxx
    
    methods: post
    
    data内容： 训练参数json数据
            
            例：“{"structure":"yolo2", "epoch":5000, "optimizer":"SGD", "batchsize":64,"learningrate":0.0001,"momentum":0.9,"weightdecay":0.0005,  "Retrain": 1, "pretrainmodel": "test1.param"}”
        
    参数：
    
        usrname 用户名
        
        taskname 任务名
        
    返回：
    
          成功： 训练参数json数据
          
          失败： ‘{}’
     
* 获取优化方法

    http://ip:port/api/getoptmethod
    
    methods: get
    
    参数：
        
    返回：
    
          成功： 优化方法列表，例如["SGD", "AdaGrad", "RMSProp", "Adam", "Adamax", "Nadam"]
          
          失败： ‘{}’     

* 获取已训练模型（只有在Retrain参数为1时使用，其余时不使用）

    http://ip:port/api/getpretrainmodel?usrname=xxx&taskname=xxx&structure=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名

	structure 模型结构
    
    methods: get
    
    参数：
        
    返回：
    
          成功： 已训练模型列表，例如["test1.param", "test2.param"]
          
          失败： ‘{}’

* 获取已训练模型（只有在自动标注时使用，其余时不使用）

    http://ip:port/api/getpretrainmodelall?usrname=xxx&taskname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
        taskname 任务名

    
    methods: get
    
    参数：
        
    返回：
    
          成功： 已训练模型列表，例如["test1.param", "test2.param"]
          
          失败： ‘{}’

* 获取检测训练模型

    http://ip:port/api/getdetstructure
    
    methods: get
    
    参数：
        
    返回：
    
          成功： 检测模型列表，例如["yolo2", "ssd"]
          
          失败： ‘{}’
       
* 获取分类训练模型

    http://ip:port/api/getclsstructure
    
    methods: get
    
    参数：
        
    返回：
    
          成功： 分类模型列表，例如["mobilenet", "googlenet", "resnet101"]
          
          失败： ‘{}’   
          
* 检测图片

    http://ip:port/api/detectimage?usrname=xxx&taskname=xxx&filename=xxx

    methods: post
    
    data内容： ‘file’：文件数据
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          filename 待上传文件名
          
    返回：
    
          成功： 检测结果（json格式）
          
          失败： ‘error：’ + info

* 自动标注图片

    http://ip:port/api/autolabelimage?usrname=xxx&taskname=xxx&start=xxx&num=xxx

    methods: get
    
    参数： 
    
          usrname 用户名
    
          taskname 任务名 
          
          start 图片开始index，从1开始计数
          
          num 图片浏览的个数 

    返回：
    
          成功： ‘OK’
          
          失败： ‘error：’ + info
          
* 打包标记数据输出

    http://ip:port/api/getlabelzip?usrname=xxx&taskname=xxx
    
    methods: post
        
    data内容： 管理用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 管理用户名称
          
          taskname 任务名称
        
    返回：
    
          成功： 打包标记数据url
          
          失败： "Fail"
          
* 打包训练模型输出

    http://ip:port/api/getmodel?usrname=xxx&taskname=xxx&structure=xxx
    
    methods: post
        
    data内容： 管理用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 管理用户名称
          
          taskname 任务名称

	  structure 模型结构
        
    返回：
    
          成功： 打包模型数据url（也需要等待一段时间才会返回）
          
          失败： "Fail"
          

* 查看operations

    http://ip:port/api/getoperations?usrname=xxx&start=xxx&num=xxx

    methods: get

    参数：

	usrname 用户名

	start 起始序号（从最新的开始算）

	num 条数

    返回：

	成功：操作列表

		例如：((u'codvision', u'192.168.0.118',u'2017-10-30 11:10:16',  u'login'， 'login'),(u'codvision', u'192.168.0.118', u'2017-10-30 11:10:16', u'listdir'，  'listdir')) 分别为：操作者名称，操作者ip， 操作时间, 操作类型， 操作详细描述

	失败： （）

* 查看operations个数

    http://ip:port/api/getoperationscount?usrname=xxx

    methods: get

    参数：

	usrname 用户名

    返回：

	成功：operations个数

	失败： 0
    
### worker相关API 
        
* 获取workers列表

    http://ip:port/api/getworkerlist?usrname=xxx
    
    methods: get
    
    参数：
    
        usrname 用户名
        
    返回：
    
          成功： worker列表
          
                    例如：((u'worker1', 0L, u'None'， u'2048/8192', 'all'),(u'worker2', 1L, u'task1', u'4096/8192', 'public')) 分别为：worker名称，状态， task名称, GPU内存使用情况， 拥有者
          
          失败： （）
          
* 修改worker拥有者

    http://ip:port/api/modifyworkerowner?workername=xxx&ownername=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          workername worker名称
          
          ownername 拥有者名称
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 获取管理用户列表

    http://ip:port/api/getmanagerusrlist
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：

        
    返回：
    
          成功： 管理用户列表，例如"['public', 'codvision']"
          
          失败： "[]"
          
          
### 用户相关API

* 用户注册

    http://ip:port/api/userreg

    methods: post
    
    data内容： 用户注册json数据
               
               例：'{"name": "fj", "email": "fj@qq.com", "passwd": "xxxxxx", "active": 0, "level": 0, "group": "common"}'
    
    参数： 
          
    返回：
    
          成功： 'OK'
          
          失败： 'error：' + info
          
* 用户登陆

    http://ip:port/api/userlogin

    methods: post
    
    data内容： 用户登陆json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
            
    参数： 
          
    返回：
    
          成功： {"status":"OK", "level": levelvalue}
          
          失败： {"status":"Fail", "level": 0}
           
* 获取用户级别

    http://ip:port/api/userlevel

    methods: get
                
    参数： 
    
          usrname 用户名
          
    返回：
    
          成功： 用户级别数字 0（普通用户） 1（编辑用户） 2（管理用户） 3（超级用户）
          
          失败： 0
          
* 查看用户列表

    http://ip:port/api/getuserlist
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
        
    返回：
    
          成功： user列表
          
                    例如：[(u'fj', u'fengjie@codvision.com', 1L, 3L， u'super')] 分别为：user名称，邮箱， 是否激活, 级别（0普通1编辑2管理3超级）， 所在组名称
          
          失败： （）
          
* 删除用户

    http://ip:port/api/delusr?usrname=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 用户名
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 修改用户级别

    http://ip:port/api/setusrlevel?usrname=xxx&level=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 用户名
          
          level 级别
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 修改用户组别

    http://ip:port/api/setusrgroup?usrname=xxx&group=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 用户名
          
          group 组名
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 修改用户邮箱

    http://ip:port/api/setusremail?usrname=xxx&email=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 用户名
          
          email 邮箱
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 修改用户密码

    http://ip:port/api/setusrpasswd?usrname=xxx&passwd=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          usrname 用户名
          
          passwd 密码
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 查看组列表

    http://ip:port/api/getgrouplist
    
    methods: get
        
    返回：
    
          成功： 组名列表
          
                    例如：[u'super',u'common']
          
          失败： （）
          
* 添加组

    http://ip:port/api/addgroup?groupname=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          groupname 组名
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
* 删除组

    http://ip:port/api/delgroup?groupname=xxx
    
    methods: post
        
    data内容： 超级用户json数据
            
            例：'{"name": "fj", "passwd": "xxxxxx"}'
           
    参数：
    
          groupname 组名
        
    返回：
    
          成功： 'OK'
          
          失败： （）
          
### json数据格式

* taglist json数据

例：'{"taglist": ["a", "b", "c", "e"]}'

多标签
{
    "listname":["list1", "list2"],
    "taglist": 
    {
         "list1":["行人","车牌","标牌","汽车","自行车","电瓶车"],
         "list2":["aa","bb"]
        
    }
}

* label json数据

例： {
            "length": 2,
            "objects": [
                {
                        "x_start": 0.091,
                        "y_start": 0.322,
                        "x_end": 0.267,
                        "y_end": 0.545,
                        "tag": "奶牛",
                        "info": "zhejiang"
                    },{
                        "x_start": 0.738,
                        "y_start": 0.370,
                        "x_end": 0.942,
                        "y_end": 0.520,
                        "tag": "公鸡",
                        "info": "aasdfasf"
                    }
            ]
        }
