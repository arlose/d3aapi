## 数据库设计
by fengjie@codvision

### 定义


### 数据库名 ImageServer

* Users

    | tableitem      | type              | 描述
    | -------------- | ----------------- | ---------------------------------
	| id 		| int(4)		    | 用户id
	| name	| char(100)	    | 用户名称
	| email	| char(100)	    | 用户邮箱
	| passwd	| char(100)	    | 用户密码
	| active   | int(4)		    | 用户激活状态（0（默认），未激活，1，激活）
	| level		| int(4)		    | 用户级别（0（默认），普通用户，1，编辑用户，2，管理用户， 3， 超级用户）
	| groups	| char(100)	    | 用户组名（默认'common'）
	| regtime	| char(100)	    | 注册时间
	| regip   	| char(100)	    | 注册ip
	| lastlogintime	| char(100)	    | 上次登陆时间
	| lastloginip   	| char(100)	    | 上次登陆ip
	
	
* Groups

    | tableitem      | type              | 描述
    | -------------- | ----------------- | ---------------------------------
	| id 		| int(4)		    | 组id
	| name	| char(100)	    |  组名称
	

* Tasks

    | tableitem      | type              | 描述
    | -------------- | ----------------- | ---------------------------------
	| id 		| int(4)		    | 任务id
	| name	| char(100)	    | 任务名称
	| createtime	| char(100)	    | 创建时间
	| process	| double(16,2)	    | 进度
	| status		| int(4)		    | 任务状态（0标注中1待训练2训练中3训练完成4出错）
	| usrname	| char(100)	    | 创建任务的用户名
	| type		| int(4)		    | 任务类型（0图片检测1图片分类2视频分类）
	| workerpid 		| int(4)		    | worker的进程id
	| stop 		| int(4)		    | 终止任务标记
	| exclusworker | int(4)         | 是否独占某些worker
	
* Workers

    | tableitem      | type              | 描述
    | -------------- | ----------------- | ---------------------------------
	| id 		| int(4)		    | worker id
	| name	| char(100)	    | worker 名称
	| status		| int(4)		    | worker 状态（0空闲1忙碌2掉线）
	| GPUMemery	| char(100)	    | 显卡信息
	| taskname      | char(100)     | 正在服务的task名称
	| updatetime	| char(100)	    | 更新时间
	| Memusage	| int(4)	    | 显存剩余
	| usrname	| char(100)	    | 用户名字
