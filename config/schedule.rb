require 'yaml'

root = File.expand_path('.')
cfg = YAML.load_file(File.join(root, 'config/config.yml'))
interval = eval(cfg['interval'].to_s)

raise "时间设置不合法: #{cfg['interval']}" unless interval >= 60
raise "备份根目录无效: #{cfg['backup_root']}" unless File.exist?(cfg['backup_root']) && File.directory?(cfg['backup_root'])

set :output, File.join(root, 'log')
every interval do
	command "ruby #{File.join(root, 'main.rb')}"
end