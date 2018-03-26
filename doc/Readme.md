python api.py 8031端口，负责提供图片文件浏览和标记，任务添加，数据库访问等api
python manage.py 8030端口，负责登陆界面，显示浏览界面
mysqlop.py 访问数据库相关
python worker.py 负责接收任务并开启训练
