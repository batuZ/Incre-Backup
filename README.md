# Incre-Backup

	本地目录定时增量备份

- 后台静默执行
- 极低性能消耗
- 定时增量备份，无冗余

### 安装
	
* 需要ruby2.5或更高版本
* 进入目录运行 `bundle install`


### 配置文件：.config/config.yml
	
* `interval` : 重复周期，最小60秒，[参考whenever文档](https://github.com/javan/whenever)
	- ex: 
		- `interval: 1.day`
		- `interval: 2.hours`
		- `interval: 3.minutes`
		- `interval: 60` eql `interval: 1.minute`
* `source_folders`: 设置源文件夹
	- ex:
```
			   source_folders: 
			     - /User/username/work
			     - /User/username/project
			     - /User/username/database
```
* `backup_root`: 备份根目录
	- ex: `/User/username/backup_root`

* `excludes`: 排除项
	- ex:
```
			   excludes: 
			     - logger.log
			     - *.tmp
			     - test/*
```


### 命令 [参考whenever文档](https://github.com/javan/whenever)
* 启动备份或更新配置 `whenever -i`
* 停止备份 `whenever -c`
* 查看任务 `cronbar -l`


### 注意!

- 仅在mac环境下完成测试，linux理论可行
- 启动时`whenever`gem会申请用户权限
- 在windows上可以手动创建计划任务，执行角本：`ruby x:\path\to\main.rb`，理论可行
- 排除项`excludes`为正则实现，不可套用其它规则
- 未进行网络备份测试


### 关于权限

		备份工作将递归查询文件和文件夹，后台运行程序需要拥有目标路径内所有对象的读取权限，否则不能完成工作。

		mac和linux系统的cron(计划任务)是由系统管理的,确保系统用户有足够的访问权限

		mac系统中需要为cron增加磁盘访问权：系统偏好设置 -> 安全与隐私 -> 隐私 -> 完全磁盘访问权限 增加`/usr/sbin/cron`

		linux系统使用root身份运行 whenever -u username , 使cron与目标文件夹有相同权限

