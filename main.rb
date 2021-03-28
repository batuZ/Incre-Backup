require 'yaml'
require 'digest'
require 'fileutils'

class Backuper
	# ex:
	# 	Backuper.new(opt).start
	#
	# opt: 
	# 	source_folders 需要备份的目录，绝对路径
	# 	ex:
	# 		source_folders: ['/User/username/tag_dir1', '/User/username/tag_dir2', ...]
	#
	# 	backup_root 本地备份目标，如果不指定此参数将使用当前目录作为备份根目录
	#   ex: 
	# 		backup_root: '/User/username/backup'
	#
	# 	excludes 排除的内容,正则前匹配，并不完善
	# 	ex:
	# 		excludes: ['.DS_Store', '*.jpg', 'tmp/']
	def initialize(opt={})
		@opt = opt
    end

    def start
		@backup_root = File.expand_path(@opt['backup_root']||'.')
    	@change_time_dir = File.expand_path(File.join(@backup_root , Time.now.strftime("%Y%m%d-%H%M%S")))
    	@current_dir = File.expand_path(File.join(@backup_root , 'current'))
    	@tags = @opt['source_folders']||[]
    	@tags.each do |dir| 
    		if File.directory?(dir)
    			@change_time_sub_dir = File.join(@change_time_dir, File.basename(dir))
				@current_sub_dir = File.join(@current_dir, File.basename(dir))
				FileUtils.mkdir_p(@current_sub_dir, :mode => 0777)
	    		new_file_list dir, dir
    		end
    	end

    	Dir.entries(@current_dir).each do |entity|
    		path = File.expand_path(entity, @current_dir)
    		if entity.eql?('.') || entity.eql?('..')
    			# do nothing ..
    		elsif File.directory?(path)
    			ori = @tags.select{|f| File.basename(f).eql?entity}.first
    			if ori && File.exist?(ori)
    				@change_time_sub_dir = File.join(@change_time_dir, entity)
    				remove_file_list path, ori, path
    			else
    				remove_dir = File.join(@change_time_dir, entity)
    				FileUtils.mkdir_p(File.dirname(remove_dir), :mode => 0777)
    				FileUtils.mv path, remove_dir
    			end
    		else
    			# do nothing ..
    		end
    	end
    end

	def new_file_list dir, root
		Dir.entries(dir).each do |entity|
			path = File.expand_path(entity, dir)
			if entity.eql?('.') || entity.eql?('..')
				# do nothing ..
			elsif File.directory?(path)
				new_file_list(path, root)
			elsif File.file?(path)
				check_file(path, root)
			else
				# do nothing ..
			end
		end
	end
   	
   	def remove_file_list dir, ori, ori_root
   		Dir.entries(dir).each do |entity|
   			path = File.expand_path(entity, dir)
   			sub_path = path.gsub(ori_root,'')
			ori_path = File.join(ori, sub_path)
			remove_dir = File.join(@change_time_sub_dir, sub_path)
   			if entity.eql?('.') || entity.eql?('..')
   				# do nothing ..
   			elsif File.directory?(path)
   				if File.exist?(ori_path)
   					remove_file_list path, ori, ori_root
   				else
   					FileUtils.mkdir_p(File.dirname(remove_dir), :mode => 0777)
   					FileUtils.mv path, remove_dir
   				end
   			elsif File.file?(path) && !File.exist?(ori_path)
				FileUtils.mkdir_p(File.dirname(remove_dir), :mode => 0777)
				FileUtils.mv path, remove_dir
   			else
   				# do nothing ..
   			end
   		end
   	end

	def check_file path, root
		sub_path = path.gsub(root,'')
		last_back_file = File.join(@current_sub_dir, sub_path)
		change_back_file = File.join(@change_time_sub_dir, sub_path)
		if !is_same?(path, last_back_file) #&& !is_exclude?(sub_path)
			FileUtils.mkdir_p(File.dirname(last_back_file), :mode => 0777)
			FileUtils.cp(path, last_back_file)
			FileUtils.mkdir_p(File.dirname(change_back_file), :mode => 0777)
			FileUtils.cp(path, change_back_file)
		end
	end

	def is_exclude? str
		(@opt['excludes']||[]).any?{|exc| !!(str =~ %r`^#{exc}`)}
	end

	def md5 path
		Digest::MD5.hexdigest(File.open(path, 'r'){|f| f.read}) rescue nil
	end

	def is_same? p1, p2
		md5(p1).eql?md5(p2)
	end
end

pid_path = File.join(File.expand_path(__dir__), 'pid')
system "kill -9 #{File.read(pid_path)}" rescue puts "#{Time.now.to_s}: 尝试停止重复线程失败！" if File.exist?(pid_path)
File.open(pid_path, 'w'){|f| f.puts Process.pid}

begin 
   	puts "#{Time.now.to_s}: Incre-Backup Start!!"
	Backuper.new(YAML.load_file(File.join(File.expand_path(__dir__), 'config/config.yml'))).start
   	puts "#{Time.now.to_s}: Incre-Backup Done!!"
rescue 
   	puts "#{Time.now.to_s}: 备份失败！"
ensure 
   	File.delete pid_path
end




