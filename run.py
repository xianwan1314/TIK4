#!/usr/bin/env python
import json
import os
import platform as plat
import re
import shutil
import sys
import time
import zipfile
from argparse import Namespace
from configparser import ConfigParser
from io import BytesIO
if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitlew("TIK4")
else:
    sys.stdout.write("\x1b]2;TIK4\x07")
    sys.stdout.flush()
import extract_dtb
import requests
from rich.progress import track
from rich.console import Console
import contextpatch
import downloader
import fspatch
import imgextractor
import lpunpack
import mkdtboimg
import ofp_mtk_decrypt
import ofp_qc_decrypt
import ozipdecrypt
import utils
from api import cls, dir_has, cat, dirsize, re_folder, f_remove
from log import LOGS, LOGE
from utils import gettype, simg2img, call
import opscrypto
import zip2mpk

LOCALDIR = os.getcwd()
binner = LOCALDIR + os.sep + "bin"
setfile = LOCALDIR + os.sep + "bin" + os.sep + "settings.json"
platform = plat.machine()
ostype = plat.system()
ebinner = binner + os.sep + ostype + os.sep + platform + os.sep
temp = binner + os.sep + 'temp'


def yecho(info): print(f"\033[36m[{time.strftime('%H:%M:%S')}]{info}\033[0m")


def ywarn(info): print(f"\033[31m{info}\033[0m")


def ysuc(info): print(f"\033[32m[{time.strftime('%H:%M:%S')}]{info}\033[0m")


def rmdire(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except PermissionError:
            ywarn("无法删除文件夹，权限不足")


if os.name == 'posix':
    try:
        os.chmod(binner, 777)
    except:
        pass


def getprop(name, path):
    with open(path, 'r') as prop:
        for s in prop.readlines():
            if s[:1] == '#':
                continue
            if name in s:
                return s.strip().split('=')[1]


class set_utils:
    def __init__(self, path):
        self.path = path

    def load_set(self):
        with open(self.path, 'r') as ss:
            data = json.load(ss)
            for v in data:
                setattr(self, v, data[v])

    def change(self, name, value):
        with open(self.path, 'r') as ss:
            data = json.load(ss)
        with open(self.path, 'w', encoding='utf-8') as ss:
            data[name] = value
            json.dump(data, ss, ensure_ascii=False, indent=4)
        self.load_set()


settings = set_utils(setfile)
settings.load_set()


class setting:
    def settings2(self):
        cls()
        print('''
        \033[33m  > 打包设置 \033[0m
           1> Brotli 压缩等级\n
           ----[EXT4设置]------
           2> 大小处理
           3> 打包方式
           4> 读写状态\n
           ----[EROFS设置]-----
           5> 压缩方式\n
           ----[IMG设置]-------
           6> UTC时间戳
           7> 创建sparse
           8> 文件系统\n
           0>返回上一级菜单
           --------------------------
        ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "0":
            return 1
        try:
            getattr(self, 'packset%s' % op_pro)()
            self.settings2()
        except AttributeError:
            print("Input error!")
            self.settings2()

    def settings3(self):
        cls()
        print('''
        \033[33m  > 动态分区设置 \033[0m
           1> dynamic_partitions簇名\n
           ----[Metadata设置]--
           2> 元数据插槽数
           3> 最大保留Size\n
           ----[分区设置]------
           4> 默认扇区/块大小\n
           ----[Super设置]-----
           5> 指定block大小
           6> 更改物理分区名
           7> 更改逻辑分区表
           8> 强制烧写完整Img
           9> 标记分区槽后缀\n
           0>返回上一级菜单
           --------------------------
        ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "0":
            return 1
        try:
            getattr(self, 'dyset%s' % op_pro)()
            self.settings3()
        except AttributeError:
            print("Input error!")
            self.settings3()

    @staticmethod
    def settings1():
        print(f"修改安卓端在内置存储识别ROM的路径。当前为/sdcard/{settings.mydir}")
        mydir = input('   请输入文件夹名称(英文):')
        if mydir:
            settings.change('mydir', mydir)

    @staticmethod
    def settings4():
        print(f"  首页banner: [1]TIK4 [2]爷 [3]电摇嘲讽 [4]镰刀斧头 [5]镰刀斧头(大) [6]TIK2旧 \n  当前:[{settings.banner}]")
        banner = input("  请输入序号: ")
        if banner.isdigit():
            if 0 < int(banner) < 7:
                settings.change('banner', banner)

    @staticmethod
    def settings5():
        cls()
        with open(binner + os.sep + 'banners' + os.sep + '1', 'r') as banner:
            print(f'\033[31m {banner.read()} \033[0m')
        print('\033[96m 开源的安卓全版本ROM处理工具\033[0m')
        print('\033[31m---------------------------------\033[0m')
        print(f"\033[93m作者:\033[0m \033[92mColdWindScholar\033[0m")
        print(f"\033[93m开源地址:\033[0m \033[91mhttps://github.com/ColdWindScholar/TIK\033[0m")
        print(f"\033[93m软件版本:\033[0m \033[44mDelta Edition\033[0m")
        print(f"\033[93m开源协议:\033[0m \033[68mGNU General Public License v3.0 \033[0m")
        print('\033[31m---------------------------------\033[0m')
        print(f"\033[93m特别鸣谢:\033[0m")
        print('\033[94mAffggh')
        print("Yeliqin666")
        print('YukongA')
        print("\033[0m")
        print('\033[31m---------------------------------\033[0m')
        input('\033[97m Powered By MIO-KITCHEN-ENVS\033[0m')

    @staticmethod
    def packset1():
        print(f"  调整brotli压缩等级（整数1-9，级别越高，压缩率越大，耗时越长），当前为：{settings.brcom}级")
        brcom = input("  请输入（1-9）: ")
        if brcom.isdigit():
            if 0 < int(brcom) < 10:
                settings.change('brcom', brcom)
        else:
            return

    @staticmethod
    def packset2():
        sizediy = input(f"  打包Ext镜像大小[1]动态最小 [2]手动改: ")
        if sizediy == '2':
            settings.change('diysize', '1')
        else:
            settings.change('diysize', '')

    @staticmethod
    def packset3():
        print(f"  当前：[{settings.pack_e2}]\n  打包方案: [1]make_ext4fs [2]mke2fs+e2fsdroid:")
        pack_op = input("  请输入序号: ")
        if pack_op == '1':
            settings.change('pack_e2', '0')
        else:
            settings.change('pack_e2', '1')

    @staticmethod
    def packset4():
        extrw = input("  打包EXT是否可读[1]RW [2]RO: ")
        if extrw == '2':
            settings.change('ext4rw', '')
        else:
            settings.change('ext4rw', '-s')

    @staticmethod
    def packset5():
        erofslim = input("  选择erofs压缩方式[1]是 [2]否: ")
        if erofslim == '1':
            erofslim = input("  选择erofs压缩方式：lz4/lz4hc/lzma/和压缩等级[1-9](数字越大耗时更长体积更小) 例如 lz4hc,8: ")
            if erofslim:
                settings.change("erofslim", erofslim)
        else:
            settings.change("erofslim", '')

    @staticmethod
    def packset6():
        utcstamp = input("  设置打包UTC时间戳[1]自动 [2]自定义: ")
        if utcstamp == "2":
            utcstamp = input("  请输入: ")
            if utcstamp.isdigit():
                settings.change('utcstamp', utcstamp)
        else:
            settings.change('utcstamp', '')

    @staticmethod
    def packset7():
        print("  Img是否打包为sparse(压缩体积)[1/0]")
        ifpsparse = input("  请输入序号: ")
        if ifpsparse == '1':
            settings.change('pack_sparse', '1')
        elif ifpsparse == '0':
            settings.change('pack_sparse', '0')

    @staticmethod
    def packset8():
        typediy = input("  打包镜像格式[1]同解包格式 [2]可选择: ")
        if typediy == '2':
            settings.change('diyimgtype', '1')
        else:
            settings.change('diyimgtype', '')

    @staticmethod
    def dyset1():
        super_group = input(f"  当前动态分区簇名：{settings.super_group}\n  请输入（无特殊字符）: ")
        if super_group:
            settings.change('super_group', super_group)

    @staticmethod
    def dyset2():
        slotnumber = input("  强制Metadata插槽数：[2] [3]: ")
        if slotnumber == '3':
            settings.change('slotnumber', '3')
        else:
            settings.change('slotnumber', '2')

    @staticmethod
    def dyset3():
        metadatasize = input("  设置metadata最大保留size(默认为65536，至少512) ")
        if metadatasize:
            settings.change('metadatasize', metadatasize)

    @staticmethod
    def dyset4():
        BLOCKSIZE = input(f"  分区打包扇区/块大小：{settings.BLOCKSIZE}\n  请输入: ")
        if BLOCKSIZE:
            settings.change('BLOCKSIZE', BLOCKSIZE)

    @staticmethod
    def dyset5():
        SBLOCKSIZE = input(f"  分区打包扇区/块大小：{settings.SBLOCKSIZE}\n  请输入: ")
        if SBLOCKSIZE:
            settings.change('SBLOCKSIZE', SBLOCKSIZE)

    @staticmethod
    def dyset6():
        supername = input(f'  当前动态分区物理分区名(默认super)：{settings.supername}\n  请输入（无特殊字符）: ')
        if supername:
            settings.change('supername', supername)

    @staticmethod
    def dyset7():
        superpart_list = input(f'  当前动态分区内逻辑分区表：{settings.superpart_list}\n  请输入（无特殊字符）: ')
        if superpart_list:
            settings.change('superpart_list', superpart_list)

    @staticmethod
    def dyset8():
        iffullsuper = input("  是否创建强制刷入的Full镜像？[1/0]")
        if iffullsuper != '1':
            settings.change('fullsuper', '')
        else:
            settings.change('fullsuper', '-F')

    @staticmethod
    def dyset9():
        autoslotsuffix = input("  是否标记需要Slot后缀的分区？[1/0]")
        if autoslotsuffix != '1':
            settings.change('autoslotsuffixing', '')
        else:
            settings.change('autoslotsuffixing', '-x')

    def __init__(self):
        cls()
        print('''
    \033[33m  > 设置 \033[0m
       1>[Droid]存储ROM目录\n
       2>[打包]相关细则设置\n
       3>[动态分区]相关设置\n
       4>自定义首页Banner\n
       5>关于工具\n
       0>返回主页
       --------------------------
    ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "0":
            return
        try:
            getattr(self, 'settings%s' % op_pro)()
            self.__init__()
        except AttributeError as e:
            print(f"Input error!{e}")
            self.__init__()


def main_menu():
    gs = 1
    projects = {}
    cls()
    try:
        content = json.loads(requests.get('https://v1.jinrishici.com/all.json').content.decode())
        shiju = content['content']
        fr = content['origin']
        another = content['author']
    except:
        gs = 0
    with open(binner + os.sep + 'banners' + os.sep + settings.banner, 'r') as banner:
        print(f'\033[31m {banner.read()} \033[0m')
    print("\033[92;44m Delta Edition \033[0m")
    if gs == 1:
        print(f"\033[36m “{shiju}”")
        print(f"\033[36m---{another}《{fr}》\033[0m\n")
    print(" >\033[33m 项目列表 \033[0m\n")
    print("\033[31m   [00]  删除项目\033[0m\n")
    print("   [0]  新建项目\n")
    pro = 0
    if os.listdir(LOCALDIR + os.sep):
        for pros in os.listdir(LOCALDIR + os.sep):
            if pros.startswith('TI_') and os.path.isdir(LOCALDIR + os.sep + pros):
                pro += 1
                print(f"   [{pro}]  {pros}\n")
                projects['%s' % pro] = pros
    print("  --------------------------------------")
    print("\033[33m  [55] 解压  [66] 退出  [77] 设置  [88] 下载ROM\033[0m")
    print("")
    print(" \n")
    op_pro = input("  请输入序号：")
    if op_pro == '55':
        unpackrom()
    elif op_pro == '88':
        url = input("输入下载链接:")
        if url:
            try:
                downloader.download([url], LOCALDIR)
            except:
                pass
            unpackrom()
    elif op_pro == '00':
        op_pro = input("  请输入你要删除的项目序号：")
        if op_pro in projects.keys():
            delr = input(f"  确认删除{projects[op_pro]}？[1/0]")
            if delr == '1':
                rmdire(LOCALDIR + os.sep + projects[op_pro])
                ysuc("  删除成功！")
            else:
                print(" 取消删除")
    elif op_pro == '0':
        projec = input("请输入项目名称(非中文)：TI_")
        if not projec:
            ywarn("Input Error!")
            input("任意按钮继续")
        else:
            project = 'TI_%s' % projec
            if os.path.exists(LOCALDIR + os.sep + project):
                project = f'{project}_{time.strftime("%m%d%H%M%S")}'
                ywarn(f"项目已存在！自动命名为：{project}")
                time.sleep(1)
            os.makedirs(LOCALDIR + os.sep + project + os.sep + "config")
            menu(project)
    elif op_pro == '66':
        cls()
        sys.exit(0)
    elif op_pro == '77':
        setting()
    elif op_pro.isdigit():
        if op_pro in projects.keys():
            menu(projects[op_pro])
        else:
            ywarn("  Input error!")
    else:
        ywarn("  Input error!")
        input("任意按钮继续")
    main_menu()


def menu(project):
    PROJECT_DIR = LOCALDIR + os.sep + project
    cls()
    os.chdir(PROJECT_DIR)
    if not os.path.exists(os.path.abspath('config')):
        ywarn("项目已损坏！")
    if not os.path.exists(PROJECT_DIR + os.sep + 'TI_out'):
        os.makedirs(PROJECT_DIR + os.sep + 'TI_out')
    print('\n')
    print(" \033[31m>ROM菜单 \033[0m\n")
    print(f"  项目：{project}")
    print('')
    print('\033[33m    1> 回到主页     2> 解包菜单\033[0m\n')
    print('\033[36m    3> 打包菜单     4> 插件菜单\033[0m\n')
    print('\033[32m    5> 一键封装\033[0m\n')
    print()
    op_menu = input("    请输入编号: ")
    if op_menu == '1':
        os.chdir(LOCALDIR)
        return
    elif op_menu == '2':
        unpack_choo(PROJECT_DIR)
    elif op_menu == '3':
        packChoo(PROJECT_DIR)
    elif op_menu == '4':
        subbed(PROJECT_DIR)
    elif op_menu == '5':
        hczip(PROJECT_DIR)
        input("任意按钮继续")
    else:
        ywarn('   Input error!')
        input("任意按钮继续")
    menu(project)


def hczip(project):
    cls()
    print(" \033[31m>打包ROM \033[0m\n")
    print(f"  项目：{os.path.basename(project)}\n")
    print('\033[33m    1> 直接打包     2> 卡线一体 \n    3> 返回\033[0m\n')
    chose = input("    请输入编号: ")
    if chose == '1':
        print("正在准备打包...")
        for v in ['firmware-update', 'META-INF', 'exaid.img', 'dynamic_partitions_op_list']:
            if os.path.isdir(os.path.join(project, v)):
                if not os.path.isdir(os.path.join(project, 'TI_out' + os.sep + v)):
                    shutil.copytree(os.path.join(project, v), os.path.join(project, 'TI_out' + os.sep + v))
            elif os.path.isfile(os.path.join(project, v)):
                if not os.path.isfile(os.path.join(project, 'TI_out' + os.sep + v)):
                    shutil.copy(os.path.join(project, v), os.path.join(project, 'TI_out'))
        for root, dirs, files in os.walk(project):
            for f in files:
                if f.endswith('.br') or f.endswith('.dat') or f.endswith('.list'):
                    if not os.path.isfile(os.path.join(project, 'TI_out' + os.sep + f)) and os.access(
                            os.path.join(project, f), os.F_OK):
                        shutil.copy(os.path.join(project, f), os.path.join(project, 'TI_out'))
    elif chose == '2':
        code = input("打包卡线一体限制机型代号:")
        utils.dbkxyt(os.path.join(project, 'TI_out') + os.sep, code, binner + os.sep + 'extra_flash.zip')
    else:
        return
    zip_file(os.path.basename(project) + ".zip", project + os.sep + 'TI_out', project + os.sep, LOCALDIR + os.sep)


def get_all_file_paths(directory) -> Ellipsis:
    # 初始化文件路径列表
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            # 连接字符串形成完整的路径
            file_paths.append(os.path.join(root, filename))

    # 返回所有文件路径
    return file_paths


class zip_file(object):
    def __init__(self, file, dst_dir, local, path=None):
        if not path:
            path = LOCALDIR + os.sep
        os.chdir(dst_dir)
        relpath = str(path + file)
        if os.path.exists(relpath):
            ywarn(f"存在同名文件：{file}，已自动重命名为{(relpath := path + utils.v_code() + file)}")
        with zipfile.ZipFile(relpath, 'w', compression=zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zip_:
            # 遍历写入文件
            for file in get_all_file_paths('.'):
                print(f"正在写入:%s" % file)
                try:
                    zip_.write(file)
                except Exception as e:
                    print("写入{}时错误{}".format(file, e))
        if os.path.exists(relpath):
            print(f'打包完成:{relpath}')
        os.chdir(local)


def subbed(project):
    if not os.path.exists(binner + os.sep + "subs"):
        os.makedirs(binner + os.sep + "subs")
    cls()
    subn = 0
    mysubs = {}
    names = {}
    print(" >\033[31m插件列表 \033[0m\n")
    for sub in os.listdir(binner + os.sep + "subs"):
        if os.path.isfile(binner + os.sep + "subs" + os.sep + sub + os.sep + "info.json"):
            with open(binner + os.sep + "subs" + os.sep + sub + os.sep + "info.json") as l_info:
                name = json.load(l_info)['name']
            subn += 1
            print(f"   [{subn}]- {name}\n")
            mysubs[subn] = sub
            names[subn] = name
    print("----------------------------------------------\n")
    print("\033[33m> [66]-安装 [77]-删除 [0]-返回\033[0m")
    op_pro = input("请输入序号：")
    if op_pro == '66':
        path = input("请输入插件路径或[拖入]:")
        if os.path.exists(path) and not path.endswith('.zip2'):
            installmpk(path)
        elif path.endswith('.zip2'):
            installmpk(zip2mpk.main(path, os.getcwd()))
        else:
            ywarn(f"{path}不存在！")
        input("任意按钮继续")
    elif op_pro == '77':
        chose = input("输入插件序号:")
        if int(chose) in mysubs.keys():
            unmpk(mysubs[int(chose)], names[int(chose)], binner + os.sep + "subs")
        else:
            print("序号错误")
    elif op_pro == '0':
        return
    elif op_pro.isdigit():
        if int(op_pro) in mysubs.keys():
            if (os.path.exists(binner + os.sep + "subs" + os.sep + mysubs[int(op_pro)] + os.sep + "main.sh") and
                    not os.path.exists(binner + os.sep + "subs" + os.sep + mysubs[int(op_pro)] + os.sep + "main.json")):
                gen = gen_sh_engine(project)
                call(
                    f'busybox ash {gen} {(binner + os.sep + "subs" + os.sep + mysubs[int(op_pro)] + os.sep + "main.sh").replace(os.sep, "/")}')
                f_remove(gen)
            else:
                ywarn(f"{mysubs[int(op_pro)]}为环境插件，不可运行！")
            input("任意按钮返回")
    subbed(project)


def gen_sh_engine(project):
    if not os.path.exists(temp):
        os.makedirs(temp)
    engine = temp + os.sep + utils.v_code()
    with open(engine, 'w', encoding='utf-8', newline='\n') as en:
        en.write(f"export project={project.replace(os.sep, '/')}\n")
        en.write(f'export tool_bin={ebinner.replace(os.sep, "/")}\n')
        en.write(f'source $1\n')
    return engine.replace(os.sep, '/')


class installmpk:
    def __init__(self, mpk):
        super().__init__()
        self.mconf = ConfigParser()
        if not mpk:
            ywarn("插件不存在")
            return
        if not zipfile.is_zipfile(mpk):
            ywarn("非插件！")
            input("任意按钮返回")
        with zipfile.ZipFile(mpk, 'r') as myfile:
            with myfile.open('info') as info_file:
                self.mconf.read_string(info_file.read().decode('utf-8'))
            with myfile.open('%s' % (self.mconf.get('module', 'resource')), 'r') as inner_file:
                self.inner_zipdata = inner_file.read()
                self.inner_filenames = zipfile.ZipFile(BytesIO(self.inner_zipdata)).namelist()
        print('''
         \033[36m
        ----------------
           MIO-PACKAGE
        ----------------
        ''')
        print("插件名称：" + self.mconf.get('module', 'name'))
        print("版本:%s\n作者：%s" % (self.mconf.get('module', 'version'), (self.mconf.get('module', 'author'))))
        print("介绍:")
        print(self.mconf.get('module', 'describe'))
        print("\033[0m\n")
        install = input("要安装吗? [1/0]")
        if install == '1':
            self.install()
        else:
            yecho("取消安装")
            input("任意按钮返回")

    def install(self):
        try:
            supports = self.mconf.get('module', 'supports').split()
        except:
            supports = [sys.platform]
        if sys.platform not in supports:
            ywarn(f"[!]安装失败:不支持的系统{sys.platform}")
            input("任意按钮返回")
            return False
        for dep in self.mconf.get('module', 'depend').split():
            if not os.path.isdir(binner + os.sep + "subs" + os.sep + dep):
                ywarn(f"[!]安装失败:不满足依赖{dep}")
                input("任意按钮返回")
                return False
        if os.path.exists(binner + os.sep + "subs" + os.sep + self.mconf.get('module', 'identifier')):
            shutil.rmtree(binner + os.sep + "subs" + os.sep + self.mconf.get('module', 'identifier'))
        fz = zipfile.ZipFile(BytesIO(self.inner_zipdata), 'r')
        for file in track(self.inner_filenames, description="正在安装..."):
            try:
                file = str(file).encode('cp437').decode('gbk')
            except:
                file = str(file).encode('utf-8').decode('utf-8')
            fz.extract(file, binner + os.sep + "subs" + os.sep + self.mconf.get('module', 'identifier'))
        try:
            depends = self.mconf.get('module', 'depend')
        except:
            depends = ''
        minfo = {"name": "%s" % (self.mconf.get('module', 'name')),
                 "author": "%s" % (self.mconf.get('module', 'author')),
                 "version": "%s" % (self.mconf.get('module', 'version')),
                 "identifier": "%s" % (self.mconf.get('module', 'identifier')),
                 "describe": "%s" % (self.mconf.get('module', 'describe')),
                 "depend": "%s" % depends}
        with open(binner + os.sep + "subs" + os.sep + self.mconf.get('module', 'identifier') + os.sep + "info.json",
                  'w') as f:
            json.dump(minfo, f, indent=2)


class unmpk:
    def __init__(self, plug, name, moduledir):
        self.arr = []
        self.arr2 = []
        if plug:
            self.value = plug
            self.value2 = name
            self.moddir = moduledir
            self.lfdep()
            self.ask()
        else:
            ywarn("请选择插件！")
            input("任意按钮继续")

    def ask(self):
        cls()
        print(f"\033[31m >删除{self.value2} \033[0m\n")
        if self.arr2:
            print("\033[36m将会同时卸载以下插件")
            for i in self.arr2:
                print(i)
            print("\033[0m\n")
        if input("确定卸载吗 [1/0]") == '1':
            self.unloop()
        else:
            ysuc("取消")
            pass
        input("任意按钮继续")

    def lfdep(self, name=None):
        if not name:
            name = self.value
        for i in [i for i in os.listdir(self.moddir) if os.path.isdir(self.moddir + os.sep + i)]:
            with open(self.moddir + os.sep + i + os.sep + "info.json", 'r', encoding='UTF-8') as f:
                data = json.load(f)
                for n in data['depend'].split():
                    if name == n:
                        self.arr.append(i)
                        self.arr2.append(data['name'])
                        self.lfdep(i)
                        break
                self.arr = sorted(set(self.arr), key=self.arr.index)
                self.arr2 = sorted(set(self.arr2), key=self.arr2.index)

    def unloop(self):
        for i in self.arr:
            self.umpk(i)
        self.umpk(self.value)

    def umpk(self, name=None) -> None:
        if name:
            print(f"正在卸载:{name}")
            if os.path.exists(self.moddir + os.sep + name):
                shutil.rmtree(self.moddir + os.sep + name)
            if os.path.exists(self.moddir + os.sep + name):
                ywarn(f"卸载{name}失败！")
            else:
                yecho(f"卸载{name}成功！")


def unpack_choo(project):
    cls()
    os.chdir(project)
    print(" \033[31m >分解 \033[0m\n")
    filen = 0
    files = {}
    infos = {}
    ywarn(f"  请将文件放于{project}根目录下！")
    print()
    print(" [0]- 分解所有文件\n")
    if dir_has(project, '.br'):
        print("\033[33m [Br]文件\033[0m\n")
        for br0 in os.listdir(project):
            if br0.endswith('.br'):
                if os.path.isfile(os.path.abspath(br0)):
                    filen += 1
                    print(f"   [{filen}]- {br0}\n")
                    files[filen] = br0
                    infos[filen] = 'br'
    if dir_has(project, '.new.dat'):
        print("\033[33m [Dat]文件\033[0m\n")
        for dat0 in os.listdir(project):
            if dat0.endswith('.new.dat'):
                if os.path.isfile(os.path.abspath(dat0)):
                    filen += 1
                    print(f"   [{filen}]- {dat0}\n")
                    files[filen] = dat0
                    infos[filen] = 'dat'
    if dir_has(project, '.new.dat.1'):
        for dat10 in os.listdir(project):
            if dat10.endswith('.dat.1'):
                if os.path.isfile(os.path.abspath(dat10)):
                    filen += 1
                    print(f"   [{filen}]- {dat10} <分段DAT>\n")
                    files[filen] = dat10
                    infos[filen] = 'dat.1'
    if dir_has(project, '.img'):
        print("\033[33m [Img]文件\033[0m\n")
        for img0 in os.listdir(project):
            if img0.endswith('.img'):
                if os.path.isfile(os.path.abspath(img0)):
                    filen += 1
                    info = gettype(os.path.abspath(img0))
                    if info == "unknow":
                        ywarn(f"   [{filen}]- {img0} <UNKNOWN>\n")
                    else:
                        print(f'   [{filen}]- {img0} <{info.upper()}>\n')
                    files[filen] = img0
                    if info != 'sparse':
                        infos[filen] = 'img'
                    else:
                        infos[filen] = 'sparse'
    if dir_has(project, '.bin'):
        for bin0 in os.listdir(project):
            if bin0.endswith('.bin'):
                if os.path.isfile(os.path.abspath(bin0)) and gettype(os.path.abspath(bin0)) == 'payload':
                    filen += 1
                    print(f"   [{filen}]- {bin0} <BIN>\n")
                    files[filen] = bin0
                    infos[filen] = 'payload'
    if dir_has(project, '.ozip'):
        print("\033[33m [Ozip]文件\033[0m\n")
        for ozip0 in os.listdir(project):
            if ozip0.endswith('.ozip'):
                if os.path.isfile(os.path.abspath(ozip0)) and gettype(os.path.abspath(ozip0)) == 'ozip':
                    filen += 1
                    print(f"   [{filen}]- {ozip0}\n")
                    files[filen] = ozip0
                    infos[filen] = 'ozip'
    if dir_has(project, '.ofp'):
        print("\033[33m [Ofp]文件\033[0m\n")
        for ofp0 in os.listdir(project):
            if ofp0.endswith('.ofp'):
                if os.path.isfile(os.path.abspath(ofp0)):
                    filen += 1
                    print(f"   [{filen}]- {ofp0}\n")
                    files[filen] = ofp0
                    infos[filen] = 'ofp'
    if dir_has(project, '.ops'):
        print("\033[33m [Ops]文件\033[0m\n")
        for ops0 in os.listdir(project):
            if ops0.endswith('.ops'):
                if os.path.isfile(os.path.abspath(ops0)):
                    filen += 1
                    print(f'   [{filen}]- {ops0}\n')
                    files[filen] = ops0
                    infos[filen] = 'ops'
    if dir_has(project, '.win'):
        print("\033[33m [Win]文件\033[0m\n")
        for win0 in os.listdir(project):
            if win0.endswith('.win'):
                if os.path.isfile(os.path.abspath(win0)):
                    filen += 1
                    print(f"   [{filen}]- {win0} <WIN> \n")
                    files[filen] = win0
                    infos[filen] = 'win'
    if dir_has(project, '.win000'):
        for win0000 in os.listdir(project):
            if win0000.endswith('.win000'):
                if os.path.isfile(os.path.abspath(win0000)):
                    filen += 1
                    print(f"   [{filen}]- {win0000} <分段WIN> \n")
                    files[filen] = win0000
                    infos[filen] = 'win000'
    if dir_has(project, '.dtb'):
        print("\033[33m [Dtb]文件\033[0m\n")
        for dtb0 in os.listdir(project):
            if dtb0.endswith('.dtb'):
                if os.path.isfile(os.path.abspath(dtb0)) and gettype(os.path.abspath(dtb0)) == 'dtb':
                    filen += 1
                    print(f'   [{filen}]- {dtb0}\n')
                    files[filen] = dtb0
                    infos[filen] = 'dtb'
    print()
    print("\033[33m  [00] 返回  [11] 循环解包  \033[0m")
    print("  --------------------------------------")
    filed = input("  请输入对应序号：")
    if filed == '0':
        print()
        for v in files.keys():
            unpack(files[v], infos[v], project)
    elif filed == '11':
        print()
        imgcheck = 0
        upacall = input("  是否解包所有文件？ [1/0]")
        for v in files.keys():
            if upacall != '1':
                imgcheck = input(f"  是否解包{files[v]}?[1/0]")
            if upacall == "1" or imgcheck != "0":
                unpack(files[v], infos[v], project)
    elif filed == '00':
        return
    elif filed.isdigit():
        if int(filed) in files.keys():
            unpack(files[int(filed)], infos[int(filed)], project)
        else:
            ywarn("Input error!")
            input("任意按钮继续")
    else:
        ywarn("Input error!")
        input("任意按钮继续")
    unpack_choo(project)


def packChoo(project):
    cls()
    print(" \033[31m >打包 \033[0m\n")
    partn = 0
    parts = {}
    types = {}
    if not os.path.exists(project + os.sep + "config"):
        os.makedirs(project + os.sep + "config")
    if project:
        print("   [0]- 打包所有镜像\n")
        for packs in os.listdir(project):
            if os.path.isdir(project + os.sep + packs):
                if os.path.exists(project + os.sep + "config" + os.sep + packs + "_fs_config"):
                    partn += 1
                    parts[partn] = packs
                    if os.path.exists(project + os.sep + "config" + os.sep + packs + "_erofs"):
                        typeo = 'erofs'
                    else:
                        typeo = 'ext'
                    types[partn] = typeo
                    print(f"   [{partn}]- {packs} <{typeo}>\n")
                elif os.path.exists(project + os.sep + packs + os.sep + "comp"):
                    partn += 1
                    parts[partn] = packs
                    types[partn] = 'bootimg'
                    print(f"   [{partn}]- {packs} <bootimg>\n")
                elif os.path.exists(project + os.sep + "config" + os.sep + "dtbinfo_" + packs):
                    partn += 1
                    parts[partn] = packs
                    types[partn] = 'dtb'
                    print(f"   [{partn}]- {packs} <dtb>\n")
                elif os.path.exists(project + os.sep + "config" + os.sep + "dtboinfo_" + packs):
                    partn += 1
                    parts[partn] = packs
                    types[partn] = 'dtbo'
                    print(f"   [{partn}]- {packs} <dtbo>\n")
        print()
        print("\033[33m [55] 循环打包 [66] 打包Super [77] 打包Payload [88]返回\033[0m")
        print("  --------------------------------------")
        filed = input("  请输入对应序号：")
        if filed == '0':
            op_menu = input("  输出文件格式[1]br [2]dat [3]img:")
            if op_menu == '1':
                form = 'br'
            elif op_menu == '2':
                form = 'dat'
            else:
                form = 'img'
            if settings.diyimgtype == '1':
                syscheck = input("手动打包所有分区格式为：[1]ext4 [2]erofs")
                if syscheck == '2':
                    imgtype = "erofs"
                else:
                    imgtype = "ext"
            else:
                imgtype = 'ext'
            for f in parts.keys():
                yecho(f"打包{parts[f]}...")
                if types[f] == 'bootimg':
                    dboot(project + os.sep + parts[f], project + os.sep + parts[f] + ".img")
                elif types[f] == 'dtb':
                    makedtb(project + os.sep + parts[f], project)
                elif types[f] == 'dtbo':
                    makedtbo(parts[f], project)
                else:
                    inpacker(parts[f], project, form, imgtype)
        elif filed == '55':
            pacall = input("  是否打包所有镜像？ [1/0]	")
            op_menu = input("  输出所有文件格式[1]br [2]dat [3]img:")
            if op_menu == '1':
                form = 'br'
            elif op_menu == '2':
                form = 'dat'
            else:
                form = 'img'
            if settings.diyimgtype == '1':
                syscheck = input("手动打包所有分区格式为：[1]ext4 [2]erofs")
                if syscheck == '2':
                    imgtype = "erofs"
                else:
                    imgtype = "ext"
            else:
                imgtype = 'ext'
            for f in parts.keys():
                if pacall != '1':
                    imgcheck = input(f"  是否打包{parts[f]}?[1/0]	")
                else:
                    imgcheck = '1'
                if not imgcheck == '1':
                    continue
                yecho(f"打包{parts[f]}...")
                if types[f] == 'bootimg':
                    dboot(project + os.sep + parts[f], project + os.sep + parts[f] + ".img")
                elif types[f] == 'dtb':
                    makedtb(project + os.sep + parts[f], project)
                    pass
                elif types[f] == 'dtbo':
                    makedtbo(parts[f], project)
                else:
                    pass
                    inpacker(parts[f], project, form, imgtype)
        elif filed == '66':
            packsuper(project)
        elif filed == '77':
            packpayload(project)
        elif filed == '88':
            return
        elif filed.isdigit():
            if int(filed) in parts.keys():
                if settings.diyimgtype == '1' and types[int(filed)] not in ['bootimg', 'dtb', 'dtbo']:
                    syscheck = input("  手动打包所有分区格式为：[1]ext4 [2]erofs")
                    if syscheck == '2':
                        imgtype = "erofs"
                    else:
                        imgtype = "ext"
                else:
                    imgtype = 'ext'
                if settings.diyimgtype == '1' and types[int(filed)] not in ['bootimg', 'dtb', 'dtbo']:
                    op_menu = input("  输出所有文件格式[1]br [2]dat [3]img:")
                    if op_menu == '1':
                        form = 'br'
                    elif op_menu == '2':
                        form = "dat"
                    else:
                        form = 'img'
                else:
                    form = 'img'
                yecho(f"打包{parts[int(filed)]}")
                if types[int(filed)] == 'bootimg':
                    dboot(project + os.sep + parts[int(filed)], project + os.sep + parts[int(filed)] + ".img")
                elif types[int(filed)] == 'dtb':
                    makedtb(project + os.sep + parts[int(filed)], project)
                    pass
                elif types[int(filed)] == 'dtbo':
                    makedtbo(parts[int(filed)], project)
                else:
                    inpacker(parts[int(filed)], project, form, imgtype)
            else:
                ywarn("Input error!")
                input("任意按钮继续")
        else:
            ywarn("Input error!")
            input("任意按钮继续")
        input("任意按钮继续")
        packChoo(project)


def dboot(infile, orig):
    flag = ''
    if not os.path.exists(infile):
        print(f"Cannot Find {infile}...")
        return
    if os.path.isdir(infile + os.sep + "ramdisk"):
        try:
            os.chdir(infile + os.sep + "ramdisk")
        except Exception as e:
            print("Ramdisk Not Found.. %s" % e)
            return
        cpio = ebinner + os.sep + "cpio"
        os.system(ebinner + os.sep + "busybox find . | %s -H newc -R 0:0 -o -F ../ramdisk-new.cpio" % cpio)
        os.chdir(infile + os.sep)
        with open(infile + os.sep + "comp", "r", encoding='utf-8') as compf:
            comp = compf.read()
        print("Compressing:%s" % comp)
        if comp != "unknow":
            if call("magiskboot compress=%s ramdisk-new.cpio" % comp) != 0:
                print("Pack Ramdisk Fail...")
                os.remove("ramdisk-new.cpio")
                return
            else:
                print("Pack Ramdisk Successful..")
                try:
                    os.remove("ramdisk.cpio")
                except:
                    pass
                os.rename("ramdisk-new.cpio.%s" % comp.split('_')[0], "ramdisk.cpio")
        else:
            print("Pack Ramdisk Successful..")
            os.remove("ramdisk.cpio")
            os.rename("ramdisk-new.cpio", "ramdisk.cpio")
        if comp == "cpio":
            flag = "-n"
        ramdisk = True
    else:
        ramdisk = False
    if call("magiskboot repack %s %s" % (flag, orig)) != 0:
        print("Pack boot Fail...")
        return
    else:
        if ramdisk:
            os.remove(orig)
            os.rename(infile + os.sep + "new-boot.img", orig)
        os.chdir(LOCALDIR)
        try:
            rmdire(infile)
        except:
            print("删除错误...")
        print("Pack Successful...")


def unpackboot(file, project):
    name = os.path.basename(file).replace('.img', '')
    rmdire(project + os.sep + name)
    os.makedirs(project + os.sep + name)
    os.chdir(project + os.sep + name)
    if call("magiskboot unpack -h %s" % file) != 0:
        print("Unpack %s Fail..." % file)
        os.chdir(LOCALDIR)
        shutil.rmtree(project + os.sep + name)
        return
    if os.access(project + os.sep + name + os.sep + "ramdisk.cpio", os.F_OK):
        comp = gettype(project + os.sep + name + os.sep + "ramdisk.cpio")
        print("Ramdisk is %s" % comp)
        with open(project + os.sep + name + os.sep + "comp", "w") as f:
            f.write(comp)
        if comp != "unknow":
            os.rename(project + os.sep + name + os.sep + "ramdisk.cpio",
                      project + os.sep + name + os.sep + "ramdisk.cpio.comp")
            if call("magiskboot decompress %s %s" % (
                    project + os.sep + name + os.sep + "ramdisk.cpio.comp",
                    project + os.sep + name + os.sep + "ramdisk.cpio")) != 0:
                print("Decompress Ramdisk Fail...")
                return
        if not os.path.exists(project + os.sep + name + os.sep + "ramdisk"):
            os.mkdir(project + os.sep + name + os.sep + "ramdisk")
        os.chdir(project + os.sep + name + os.sep)
        print("Unpacking Ramdisk...")
        call("cpio -d --no-absolute-filenames -F %s -i -D %s" % ("ramdisk.cpio", "ramdisk"))
        os.chdir(LOCALDIR)
    else:
        print("Unpack Done!")
    os.chdir(LOCALDIR)


def undtb(project, infile):
    dtbdir = project + os.sep + os.path.basename(infile).split(".")[0] + "_dtbs"
    rmdire(dtbdir)
    if not os.path.exists(dtbdir):
        os.makedirs(dtbdir)
    extract_dtb.extract_dtb.split(Namespace(filename=infile, output_dir=dtbdir + os.sep + "dtb_files"))
    yecho("正在反编译dtb...")
    for i in os.listdir(dtbdir + os.sep + "dtb_files"):
        if i.endswith('.dtb'):
            name = i.split('.')[0]
            call(
                f'dtc -@ -I dtb -O dts {dtbdir + os.sep + "dtb_files" + os.sep + name + ".dtb"} -o {dtbdir + os.sep + "dtb_files" + os.sep + name + ".dts"}',
                out=1)
    open(project + os.sep + os.sep + "config" + os.sep + "dtbinfo_" + os.path.basename(infile).split(".")[0]).close()
    ysuc("反编译完成!")
    time.sleep(1)


def makedtb(sf, project):
    dtbdir = project + os.sep + sf + "_dtbs"
    rmdire(dtbdir + os.sep + "new_dtb_files")
    os.makedirs(dtbdir + os.sep + "new_dtb_files")
    for dts_files in os.listdir(dtbdir + os.sep + "dts_files"):
        new_dtb_files = dts_files.split('.')[0]
        yecho(f"正在回编译{dts_files}为{new_dtb_files}.dtb")
        if call(f'dtc -@ -I "dts" -O "dtb" "{dtbdir + os.sep + "dts_files" + os.sep + dts_files}" -o "$dtbdir/new_dtb_files/$new_dtb_files.dtb"',
                out=1) != 0:
            ywarn("回编译dtb失败")
    with open(project + os.sep + "TI_out" + os.sep + sf, 'wb') as sff:
        for dtb in os.listdir(dtbdir + os.sep + "new_dtb_files"):
            if dtb.endswith('.dtb'):
                with open(os.path.abspath(dtb), 'rb') as f:
                    sff.write(f.read())
    ysuc("回编译完成！")
    input("任意按钮继续")


def undtbo(project, infile):
    dtbodir = project + os.sep + os.path.basename(infile).split('.')[0]
    open(project + os.sep + "config" + os.sep + "dtboinfo_" + os.path.basename(infile).split('.')[0], 'w').close()
    rmdire(dtbodir)
    if not os.path.exists(dtbodir + os.sep + "dtbo_files"):
        os.makedirs(dtbodir + os.sep + "dtbo_files")
        try:
            os.makedirs(dtbodir + os.sep + "dts_files")
        except:
            pass
    yecho("正在解压dtbo.img")
    mkdtboimg.dump_dtbo(infile, dtbodir + os.sep + "dtbo_files" + os.sep + "dtbo")
    for dtbo_files in os.listdir(dtbodir + os.sep + "dtbo_files"):
        if dtbo_files.startswith('dtbo.'):
            dts_files = dtbo_files.replace("dtbo", 'dts')
            yecho(f"正在反编译{dtbo_files}为{dts_files}")
            if call(f'dtc -@ -I "dtb" -O "dts" {dtbodir + os.sep + "dtbo_files" + os.sep + dtbo_files} -o "{dtbodir + os.sep + "dts_files" + os.sep + dts_files}"') != 0:
                ywarn(f"反编译{dtbo_files}失败！")
    ysuc("完成！")
    time.sleep(1)


def makedtbo(sf, project):
    dtbodir = project + os.sep + os.path.basename(sf).split('.')[0]
    rmdire(dtbodir + os.sep + 'new_dtbo_files')
    if os.path.exists(project + os.sep + os.path.basename(sf).split('.')[0] + '.img'): os.remove(
        project + os.sep + os.path.basename(sf).split('.')[0] + '.img')
    os.makedirs(dtbodir + os.sep + 'new_dtbo_files')
    for dts_files in os.listdir(dtbodir + os.sep + 'dts_files'):
        new_dtbo_files = dts_files.replace('dts', 'dtbo')
        yecho(f"正在回编译{dts_files}为{new_dtbo_files}")
        call(
            f'dtc -@ -I "dts" -O "dtb" {dtbodir + os.sep + "dts_files" + os.sep + dts_files} -o {dtbodir + os.sep + "new_dtbo_files" + os.sep + new_dtbo_files}',
            out=1)
    yecho("正在生成dtbo.img...")
    list_ = []
    for b in os.listdir(dtbodir + os.sep + "new_dtbo_files"):
        if b.startswith('dtbo.'):
            list_.append(dtbodir + os.sep + "new_dtbo_files" + os.sep + b)
    list_ = sorted(list_, key=lambda x: int(float(x.rsplit('.', 1)[1])))
    try:
        mkdtboimg.create_dtbo(project + os.sep + os.path.basename(sf).split('.')[0] + '.img', list_, 4096)
    except:
        ywarn(f"{os.path.basename(sf).split('.')[0]}.img生成失败!")
    else:
        ysuc(f"{os.path.basename(sf).split('.')[0]}.img生成完毕!")
    input("任意按钮继续")


def inpacker(name, project, form, ftype):
    mount_path = f"/{name}"
    file_contexts = project + os.sep + "config" + os.sep + name + "_file_contexts"
    fs_config = project + os.sep + "config" + os.sep + name + "_fs_config"
    if not settings.utcstamp:
        utc = int(time.time())
    else:
        utc = settings.utcstamp
    out_img = project + os.sep + "TI_out" + os.sep + name + ".img"
    in_files = project + os.sep + name + os.sep
    if os.path.exists(project + os.sep + "config" + os.sep + name + "_size.txt"):
        img_size0 = int(cat(project + os.sep + "config" + os.sep + name + "_size.txt"))
    else:
        img_size0 = 0
    img_size1 = dirsize(in_files, 1, 1).rsize_v
    if settings.diysize == '' and img_size0 < img_size1:
        ywarn("您设置的size过小,将动态调整size!")
        img_size0 = dirsize(in_files, 1, 3, project + os.sep + "dynamic_partitions_op_list").rsize_v
    elif settings.diysize == '':
        img_size0 = dirsize(in_files, 1, 3, project + os.sep + "dynamic_partitions_op_list").rsize_v
    fspatch.main(in_files, fs_config)
    contextpatch.main(in_files, file_contexts)
    utils.qc(fs_config)
    utils.qc(file_contexts)
    size = img_size0 / int(settings.BLOCKSIZE)
    size = int(size)
    if ftype == 'erofs':
        call(
            f'mkfs.erofs -z{settings.erofslim}  -T {utc} --mount-point={mount_path} --fs-config-file={fs_config} --product-out={os.path.dirname(out_img)} --file-contexts={file_contexts} {out_img} {in_files}')
    else:
        if settings.pack_e2 == '0':
            call(
                f'make_ext4fs -J -T {utc} -S {file_contexts} -l {img_size0} -C {fs_config} -L {name} -a {name} {out_img} {in_files}')
        else:
            call(
                f'mke2fs -O ^has_journal -L {name} -I 256 -M {mount_path} -m 0 -t ext4 -b {settings.BLOCKSIZE} {out_img} {size}')
            call(
                f"e2fsdroid -e -T {utc} -S {file_contexts} -C {fs_config} {settings.extrw} -a /{name} -f {in_files} {out_img}")
    if settings.pack_sparse == '1' or form == 'dat' or form == 'br':
        call(f"img2simg {out_img} {out_img}.s")
        os.remove(out_img)
        os.rename(out_img + ".s", out_img)
    if form == 'br':
        try:
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".new.dat.br")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".patch.dat")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".transfer.list")
        except:
            pass
    elif form == 'dat':
        try:
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".new.dat")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".patch.dat")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".transfer.list")
        except:
            pass
    if form in ['dat', 'br']:
        yecho(f"打包[DAT]:{name}")
        try:
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".new.dat")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".new.dat.br")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".patch.dat")
            os.remove(project + os.sep + "TI_out" + os.sep + name + ".transfer.list")
        except:
            pass
        utils.img2sdat(out_img, project + os.sep + "TI_out", 4, name)
        try:
            os.remove(out_img)
        except:
            pass
    if form == 'br':
        yecho(f"打包[BR]:{name}")
        call(
            f'brotli -q {settings.brcom} -j -w 24 {project + os.sep + "TI_out" + os.sep + name + ".new.dat"} -o {project + os.sep + "TI_out" + os.sep + name + ".new.dat.br"}')


def packsuper(project):
    minssize = 0
    if os.path.exists(project + os.sep + "TI_out" + os.sep + "super.img"):
        os.remove(project + os.sep + "TI_out" + os.sep + "super.img")
    if not os.path.exists(project + os.sep + "super"):
        os.makedirs(project + os.sep + "super")
    cls()
    ywarn(f"请将需要打包的分区镜像放置于{project}/super中！")
    supertype = input("请输入Super类型：[1]A_only [2]AB [3]V-AB-->")
    if supertype == '3':
        supertype = 'VAB'
    elif supertype == '2':
        supertype = 'AB'
    else:
        supertype = 'A_only'
    ifsparse = input("是否打包为sparse镜像？[1/0]")
    checkssize = input("请设置Super.img大小:[1]9126805504 [2]10200547328 [3]16106127360 [4]压缩到最小 [5]自定义")
    if checkssize == '1':
        supersize = 9126805504
    elif checkssize == '2':
        supersize = 10200547328
    elif checkssize == '3':
        supersize = 16106127360
    elif checkssize == '4':
        minssize = 1
        supersize = 0
        ywarn("您已设置压缩镜像至最小,对齐不规范的镜像将造成打包失败；Size超出物理分区大小会造成刷入失败！")
    else:
        supersize = input("请输入super分区大小（字节数）:")
    yecho("打包到TI_out/super.img...")
    insuper(project + os.sep + 'super', project + os.sep + 'TI_out' + os.sep + "super.img", supersize, supertype,
            ifsparse, minssize)


def insuper(Imgdir, outputimg, ssize, stype, sparse, minsize):
    group_size_a = 0
    group_size_b = 0
    groupaab = None
    supermsize = 0
    for root, dirs, files in os.walk(Imgdir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                os.remove(file_path)
    superpa = f"--metadata-size {settings.metadatasize} --super-name {settings.supername} "
    if sparse == '1':
        superpa += "--sparse "
    if stype == 'VAB':
        superpa += "--virtual-ab "
    superpa += f"-block-size={settings.SBLOCKSIZE} "
    for imag in os.listdir(Imgdir):
        if imag.endswith('.img'):
            image = imag.split('.')[0].replace('_a', '').replace('_b', '')
            if f'partition {image}:readonly' not in superpa and f'partition {image}_a:readonly' not in superpa:
                print(f"待打包分区:{image}")
                if stype in ['VAB', 'AB']:
                    if os.path.isfile(Imgdir + os.sep + image + "_a.img") and os.path.isfile(
                            Imgdir + os.sep + image + "_b.img"):
                        groupaab = 1
                        img_sizea = os.path.getsize(Imgdir + os.sep + image + "_a.img")
                        img_sizeb = os.path.getsize(Imgdir + os.sep + image + "_b.img")
                        group_size_a += img_sizea
                        group_size_b += img_sizeb
                        superpa += f"--partition {image}_a:readonly:{img_sizea}:{settings.super_group}_a --image {image}_a={Imgdir}{os.sep}{image}_a.img --partition {image}_b:readonly:{img_sizeb}:{settings.super_group}_b --image {image}_b={Imgdir}{os.sep}{image}_b.img "
                    else:
                        img_size = os.path.getsize(Imgdir + os.sep + image + ".img")
                        group_size_a += img_size
                        group_size_b += img_size
                        superpa += f"--partition {image}_a:readonly:{img_size}:{settings.super_group}_a --image {image}_a={Imgdir}{os.sep}{image}.img --partition {image}_b:readonly:0:{settings.super_group}_b "
                else:
                    img_size = os.path.getsize(Imgdir + os.sep + image + ".img")
                    superpa += f"--partition {image}:readonly:{img_size}:{settings.super_group} --image {image}={Imgdir}{os.sep}{image}.img "
                    group_size_a += img_size
    if not groupaab:
        supermsize = group_size_a + int(settings.SBLOCKSIZE) * 1000
    elif groupaab == 1:
        supermsize = group_size_a + group_size_b + int(settings.SBLOCKSIZE) * 1000
    if minsize == 1:
        supersize = supermsize
        if supermsize < ssize:
            ywarn("设置SuperSize过小！已自动扩大！")
            supersize = supermsize + 4096000
    else:
        supersize = ssize
    if not supersize:
        supersize += group_size_a + 4096000
    superpa += f"--device super:{supersize} "
    if stype in ['VAB', 'AB']:
        superpa += "--metadata-slots 3 "
        superpa += f" --group {settings.super_group}_a:{supersize} "
        superpa += f" --group {settings.super_group}_b:{supersize} "
    else:
        superpa += "--metadata-slots 2 "
        superpa += f" --group {settings.super_group}:{supersize} "
    superpa += f"{settings.fullsuper} {settings.autoslotsuffixing} --output {outputimg}"
    if call(f'lpmake {superpa}') != 0:
        ywarn("创建super.img失败！")
    else:
        ysuc("成功创建super.img!")
    input("任意按钮继续")


def packpayload(project):
    if ostype != 'Linux':
        print(f"不支持当前系统:{ostype},目前只支持:Linux")
        input("任意按钮继续")
        return
    if os.path.exists(project + os.sep + 'payload'):
        if input('发现之前打包Payload残留，清空吗[1/0]') == '1':
            re_folder(project + os.sep + 'payload')
            re_folder(project + os.sep + 'TI_out' + os.sep + "payload")
            f_remove(project + os.sep + 'TI_out' + os.sep + "payload" + os.sep + 'dynamic_partitions_info.txt')
    ywarn(f"请将所有分区镜像放置于{project}/payload中（非super）！")
    yecho(
        "mi_ext分区也属于super，请及时到设置修改动态分区内逻辑分区表\n很耗时、很费CPU、很费内存，由于无官方签名故意义不大，请考虑后使用")
    checkssize = input("请设置构建Super.img大小:[1]9126805504 [2]10200547328 [3]16106127360 [5]自定义")
    if checkssize == '1':
        supersize = 9126805504
    elif checkssize == '2':
        supersize = 10200547328
    elif checkssize == '3':
        supersize = 16106127360
    else:
        supersize = input("请输入super分区大小（字节数）	")
    yecho(f"打包到{project}/TI_out/payload...")
    inpayload(supersize, project)


def inpayload(supersize, project):
    yecho("将打包至：TI_out/payload，payload.bin & payload_properties.txt")
    partname = ''
    pimages = ''
    for sf in os.listdir(project + os.sep + 'payload'):
        if sf.endswith('.img'):
            partname += sf.replace('.img', '') + ":"
            pimages += f"{pimages}{project}{os.sep}payload{os.sep}{sf.replace('.img', '')}.img:"
            yecho(f"预打包:{sf}")
    inparts = f"--partition_names={partname[:-1]} --new_partitions={pimages[:-1]}"
    yecho(f"当前Super逻辑分区表：{settings.superpart_list}，可在<设置>中调整.")
    with open(project + os.sep + "payload" + os.sep + "dynamic_partitions_info.txt", 'w', encoding='utf-8',
              newline='\n') as txt:
        txt.write(f"super_partition_groups={settings.super_group}\n")
        txt.write(f"qti_dynamic_partitions_size={supersize}\n")
        txt.write(f"qti_dynamic_partitions_partition_list={settings.superpart_list}")
    call(
        f"delta_generator --out_file={project + os.sep + 'TI_out' + os.sep + 'payload' + os.sep + 'payload.bin'} {inparts} --dynamic_partition_info_file={project + os.sep + 'payload' + os.sep + 'dynamic_partitions_info.txt'}")
    if call(f"delta_generator --in_file={project + os.sep + 'TI_out' + os.sep + 'payload' + os.sep + 'payload.bin'} --properties_file={project + os.sep + 'config' + os.sep}payload_properties.txt") == 0:
        LOGS("成功创建payload!")
    else:
        LOGE("创建payload失败！")
    input("任意按钮继续")


def unpack(file, info, project):
    if not os.path.exists(project + os.sep + 'config'):
        os.makedirs(project + os.sep + 'config')
    yecho(f"[{info}]解包{os.path.basename(file)}中...")
    if info == 'sparse':
        simg2img(file)
        unpack(file, gettype(file), project)
    elif info == 'dtbo':
        undtbo(project, os.path.abspath(file))
    elif info == 'br':
        call(f'brotli -dj {file}')
        partname = os.path.basename(file).replace('.new.dat.br', '')
        filepath = os.path.dirname(file)
        unpack(os.path.join(filepath, partname + ".new.dat"), 'dat', project)
    elif info == 'dtb':
        undtb(project, os.path.abspath(file))
    elif info == 'dat':
        partname = os.path.basename(file).replace('.new.dat', '')
        filepath = os.path.dirname(file)
        utils.sdat2img(os.path.join(filepath, partname + '.transfer.list'),
                       os.path.join(filepath, partname + ".new.dat"), os.path.join(filepath, partname + ".img"))
        try:
            os.remove(os.path.join(filepath, partname + ".new.dat"))
            os.remove(os.path.join(filepath, partname + '.transfer.list'))
            os.remove(os.path.join(filepath, partname + '.patch.dat'))
        except:
            pass
        unpack(os.path.join(filepath, partname + ".img"), gettype(os.path.join(filepath, partname + ".img")), project)
    elif info == 'img':
        unpack(file, gettype(file), project)
    elif info == 'ofp':
        ofpm = input(" ROM机型处理器为？[1]高通 [2]MTK	")
        if ofpm == '1':
            ofp_qc_decrypt.main(file, project)
        elif ofpm == '2':
            ofp_mtk_decrypt.main(file, project)
    elif info == 'ozip':
        ozipdecrypt.main(file)
        try:
            os.remove(file)
        except Exception as e:
            print(f"错误！{e}")
        zipfile.ZipFile(file.replace('.ozip', '.zip')).extractall(project)
    elif info == 'ops':
        args = {"decrypt": True,
                '<filename>': file,
                'outdir': os.path.join(project, os.path.dirname(file).split('.')[0])}
        opscrypto.main(args)
    elif info == 'payload':
        yecho(f"{os.path.basename(file)}所含分区列表：")
        os.system(f'{ebinner}payload-dumper-go -l {file}')
        extp = input("请输入需要解压的分区名(空格隔开)/all[全部]	")
        if extp == 'all':
            os.system(f"{ebinner}payload-dumper-go -o {project} {file}")
        else:
            for p in extp.split():
                os.system(f'{ebinner}payload-dumper-go -p {p} -o {project} {file}')
    elif info == 'win000':
        for fd in [f for f in os.listdir(project) if re.search(r'\.win\d+', f)]:
            with open(project + os.path.basename(fd).rsplit('.', 1)[0], 'ab') as ofd:
                for fd1 in sorted(
                        [f for f in os.listdir(project) if f.startswith(os.path.basename(fd).rsplit('.', 1)[0] + ".")],
                        key=lambda x: int(x.rsplit('.')[3])):
                    print("合并%s到%s" % (fd1, os.path.basename(fd).rsplit('.', 1)[0]))
                    with open(project + os.sep + fd1, 'rb') as nfd:
                        ofd.write(nfd.read())
                    os.remove(project + os.sep + fd1)
        filepath = os.path.dirname(file)
        unpack(os.path.join(filepath, file), gettype(os.path.join(filepath, file)), project)
    elif info == 'win':
        filepath = os.path.dirname(file)
        unpack(os.path.join(filepath, file), gettype(os.path.join(filepath, file)), project)
    elif info == 'ext':
        imgextractor.Extractor().main(file, project + os.sep + os.path.basename(file).split('.')[0], project)
        try:
            os.remove(file)
        except:
            pass
    elif info == 'dat.1':
        for fd in [f for f in os.listdir(project) if re.search(r'\.new\.dat\.\d+', f)]:
            with open(project + os.sep + os.path.basename(fd).rsplit('.', 1)[0], 'ab') as ofd:
                for fd1 in sorted(
                        [f for f in os.listdir(project) if f.startswith(os.path.basename(fd).rsplit('.', 1)[0] + ".")],
                        key=lambda x: int(x.rsplit('.')[3])):
                    print("合并%s到%s" % (fd1, os.path.basename(fd).rsplit('.', 1)[0]))
                    with open(project + os.sep + fd1, 'rb') as nfd:
                        ofd.write(nfd.read())
                    os.remove(project + os.sep + fd1)
        partname = os.path.basename(file).replace('.new.dat.1', '')
        filepath = os.path.dirname(file)
        utils.sdat2img(os.path.join(filepath, partname + '.transfer.list'),
                       os.path.join(filepath, partname + ".new.dat"), os.path.join(filepath, partname + ".img"))
        unpack(os.path.join(filepath, partname + ".img"), gettype(os.path.join(filepath, partname + ".img")), project)
    elif info == 'erofs':
        call(f'extract.erofs -i {os.path.abspath(file)} -o {project} -x ')
        open(project + os.sep + 'config' + os.sep + os.path.basename(file).split('.')[0] + "_erofs", 'w').close()
    elif info == 'super':
        lpunpack.unpack(os.path.abspath(file), project)
        for v in os.listdir(project):
            if os.path.isfile(project + os.sep + v):
                if os.path.getsize(project + os.sep + v) == 0:
                    os.remove(project + os.sep + v)
                else:
                    if v.endswith('_a.img'):
                        shutil.move(project + os.sep + v, project + os.sep + v.replace('_a', ''))
                    elif v.endswith('_b.img'):
                        shutil.move(project + os.sep + v, project + os.sep + v.replace('_b', ''))
    elif info in ['boot', 'vendor_boot']:
        unpackboot(os.path.abspath(file), project)
    else:
        ywarn("未知格式！")


def unpackrom():
    os.chdir(LOCALDIR)
    cls()
    zipn = 0
    zips = {}
    print(" \033[31m >ROM列表 \033[0m\n")
    ywarn(f"   请将ROM置于{LOCALDIR}下！")
    if dir_has(LOCALDIR, '.zip'):
        for zip0 in os.listdir(LOCALDIR):
            if zip0.endswith('.zip'):
                if os.path.isfile(os.path.abspath(zip0)):
                    if os.path.getsize(os.path.abspath(zip0)):
                        zipn += 1
                        print(f"   [{zipn}]- {zip0}\n")
                        zips[zipn] = zip0
    else:
        ywarn("	没有ROM文件！")
    print("--------------------------------------------------\n")
    print()
    zipd = input("请输入对应序列号：")
    if zipd.isdigit():
        if int(zipd) in zips.keys():
            projec = input("请输入项目名称(可留空)：")
            if projec:
                project = "TI_%s" % projec
            else:
                project = "TI_%s" % os.path.basename(zips[int(zipd)]).replace('.zip', '')
            if os.path.exists(LOCALDIR + os.sep + project):
                project = project + time.strftime("%m%d%H%M%S")
                ywarn(f"项目已存在！自动命名为：{project}")
            os.makedirs(LOCALDIR + os.sep + project)
            print(f"创建{project}成功！")
            with Console().status("[yellow]解压刷机包中...[/]"):
                zipfile.ZipFile(os.path.abspath(zips[int(zipd)])).extractall(LOCALDIR + os.sep + project)
            yecho("分解ROM中...")
            autounpack(LOCALDIR + os.sep + project)
            menu(project)
        else:
            ywarn("Input Error")
            time.sleep(0.3)
    else:
        ywarn("Input error!")
        time.sleep(0.3)


def autounpack(project):
    yecho("自动解包开始！")
    os.chdir(project)
    if os.path.exists(project + os.sep + "payload.bin"):
        yecho('解包 payload.bin...')
        unpack(project + os.sep + 'payload.bin', 'payload', project)
        yecho("payload.bin解包完成！")
        wastes = ['care_map.pb', 'apex_info.pb']
        if input("你要删除payload吗[1/0]") == '1':
            wastes.append('payload.bin')
        for waste in wastes:
            if os.path.exists(project + os.sep + waste):
                try:
                    os.remove(project + os.sep + waste)
                except:
                    pass
        if not os.path.isdir(project + os.sep + "config"):
            os.makedirs(project + os.sep + "config")
        shutil.move(project + os.sep + "payload_properties.txt", project + os.sep + "config")
        shutil.move(project + os.sep + "META-INF" + os.sep + "com" + os.sep + "android" + os.sep + "metadata",
                    project + os.sep + "config")
    if True:
        ask_ = input("解包所有文件？[1/0]")
        for infile in os.listdir(project):
            os.chdir(project)
            if os.path.isdir(os.path.abspath(infile)):
                continue
            elif not os.path.exists(os.path.abspath(infile)):
                continue
            elif os.path.getsize(os.path.abspath(infile)) == 0:
                continue
            elif os.path.abspath(infile).endswith('.list') or os.path.abspath(infile).endswith('.patch.dat'):
                continue
            if ask_ != '1':
                ask = input(f"要分解{infile}吗 [1/0]")
                if not ask == '1':
                    continue
            if infile.endswith('.new.dat.br'):
                unpack(os.path.abspath(infile), 'br', project)
            elif infile.endswith('.dat.1'):
                unpack(os.path.abspath(infile), 'dat.1', project)
            elif infile.endswith('.new.dat'):
                unpack(os.path.abspath(infile), 'dat', project)
            elif infile.endswith('.img'):
                unpack(os.path.abspath(infile), 'img', project)


if __name__ == '__main__':
    main_menu()
