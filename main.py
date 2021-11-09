import fnmatch
import os
import shutil
import sys
import time
from hashlib import md5
from shutil import copyfile

import yaml
from psutil import Process


def cpath(_path):
    """处理一下不同平台之间的路径问题"""
    return '/'.join(_path.split('\\')) if _path else ''


def join_path(base_path='', *_paths):
    """扩展路径"""
    tmp = cpath(base_path)
    for p in _paths:
        tmp += '/' + cpath(p)
    return '/'.join(tmp.split('//'))


def is_exclude(_str, ex_list):
    """判断是否在排除列表"""
    for ex in ex_list:
        if fnmatch.fnmatch(_str, ex):
            return True
    return False


def _md5(path):
    with open(path, 'rb') as f:
        md5obj = md5()
        md5obj.update(f.read())
    return str(md5obj.hexdigest())


def is_same(p1, p2):
    """判断有没有修改过"""
    return os.path.exists(p1) and os.path.exists(p2) and _md5(p1) == _md5(p2)


class Backuper:
    def __init__(self, opt):
        self.opt = opt
        # 路径保护
        if 'backup_root' in opt and opt['backup_root'] != '':
            self.opt['backup_root'] = cpath(str(self.opt['backup_root']))
        else:
            self.opt['backup_root'] = './backup_root'
        # 源去重复，排除备份路经
        if 'source_folders' in opt and isinstance(opt['source_folders'], list):
            for i in range(len(opt['source_folders'])):
                if self.opt['backup_root'] in cpath(opt['source_folders'][i]):
                    opt['source_folders'][i] = self.opt['backup_root']
            self.opt['source_folders'].append(self.opt['backup_root'])
            self.opt['source_folders'] = list(set(opt['source_folders']))
            self.opt['source_folders'].remove(self.opt['backup_root'])
        else:
            self.opt['source_folders'] = ()

    def start(self):
        back_root = self.opt['backup_root']
        change_time_dir = join_path(back_root,
                                    time.strftime("%Y%m%d-%H%M%S", time.localtime()))
        current_dir = join_path(back_root, 'current')
        # only copy into current at first backup
        self.is_first_back_up = os.path.exists(current_dir)
        tags = self.opt['source_folders']
        for sDir in tags:
            if os.path.isdir(sDir):
                self.change_time_sub_dir = join_path(
                    change_time_dir, os.path.basename(sDir))
                self.current_sub_dir = join_path(
                    current_dir, os.path.basename(sDir))
                self.new_file_list(sDir, sDir)

        # 1- remove unbackup dirs
        # 2- remove deleted folders from current_dir
        # 3- and backup them onec time
        # * current_dir has't files, so, need't deal with files
        for entity in os.listdir(current_dir):
            _path = join_path(current_dir, entity)
            if os.path.isdir(_path):
                ori = None
                for tag in tags:
                    if entity == os.path.basename(tag):
                        ori = tag
                        break
                # #判断源文件（夹）是否存在，不存在则把current_dir中对应的文件（夹）move到time_dir
                if ori and os.path.isdir(ori) and not is_exclude(ori, self.opt['excludes']):
                    self.remove_file_list(_path, ori, change_time_dir)
                else:
                    os.makedirs(change_time_dir, mode=0o777, exist_ok=True)
                    shutil.move(_path, change_time_dir)

    def new_file_list(self, dir, root):
        for entity in os.listdir(dir):
            _path = join_path(dir, entity)
            if os.path.isdir(_path):
                self.new_file_list(_path, root)
            elif os.path.isfile(_path):
                self.check_file(_path, root)

    def check_file(self, path, root):
        sub_path = path.replace(cpath(root), '')
        last_back_file = join_path(self.current_sub_dir, sub_path)
        change_back_file = join_path(self.change_time_sub_dir, sub_path)
        if not is_same(path, last_back_file) and not is_exclude(path, self.opt['excludes']):
            os.makedirs(os.path.dirname(last_back_file),
                        mode=0o777, exist_ok=True)
            copyfile(path, last_back_file)
            if self.is_first_back_up:
                os.makedirs(os.path.dirname(change_back_file),
                            mode=0o777, exist_ok=True)
                copyfile(path, change_back_file)

    def remove_file_list(self, dir, ori, change_time_dir):
        for entity in os.listdir(dir):
            ori_path = join_path(ori, entity)
            curr_sub_path = join_path(dir, entity)
            if os.path.exists(ori_path) and not is_exclude(ori_path, self.opt['excludes']):
                if os.path.isdir(ori_path):
                    self.remove_file_list(
                        curr_sub_path, ori_path, join_path(change_time_dir, entity))
            else:
                os.makedirs(change_time_dir, mode=0o777, exist_ok=True)
                shutil.move(curr_sub_path, change_time_dir)


if __name__ == '__main__':
    config_path = './config/config.yml'
    pid_path = './pid'
    os.chdir(sys.path[0])

    # 处理一下重复执行问题
    if os.path.exists(pid_path):
        with open(pid_path, 'r') as pid_file:
            try:
                pid = int(pid_file.read())
            except:
                pid = 0

        # 如果有正在行进的备份，尝试杀一下
        if pid > 0:
            try:
                proc = Process(pid)
                os.kill(proc.pid, 9)
            except:
                print('尝试停止重复线程失败！')

    try:
        # 标记一下pid
        with open(pid_path, 'w') as pid_file:
            pid_file.write(str(os.getpid()))
        # 读配置文件
        with open(config_path, encoding="UTF-8") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        # 调备份方法
        print('Incre-Backup Start!!')
        Backuper(config).start()
        print('Incre-Backup Done!!')
    except Exception as e:
        print(e)
    finally:
        # 清理标记
        if os.path.exists(pid_path):
            os.remove(pid_path)
