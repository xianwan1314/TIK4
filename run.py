#!/usr/bin/env python
import os
import json
from api import cls
import time
import platform as plat

LOCALDIR = os.getcwd()
binner = LOCALDIR + os.sep + "bin"
setfile = LOCALDIR + os.sep + "bin" + os.sep + "settings.json"
tempdir = LOCALDIR + os.sep + 'TEMP'
tiklog = LOCALDIR + os.sep + f'TIK4_{time.strftime("%Y%m%d")}.log'
AIK = binner + os.sep + 'AIK'
MBK = binner + os.sep + 'AIK'
platform = plat.machine()
ostype = plat.system()


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
    def settings4(self):
        cls()
        print('''
        \033[33m  > 打包设置 \033[0m
           1>Brotli 压缩等级\n
           2>[EXT4] Size处理\n
           3>[EXT4] 打包工具\n
           4>[EXT4]打包RO/RW\n
           5>[Erofs]压缩方式\n
           6>[EXT4]UTC时间戳\n
           7>[EXT4]InodeSize\n
           8>[Img]创建sparse\n
           9>[~4]Img文件系统\n
           10> 补全fs_config\n
           11>默认BOOT打包Tool\n
           12>返回上一级菜单
           --------------------------
        ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "12":
            return 1
        try:
            getattr(self, 'packset%s' % op_pro)()
            self.settings5()
        except AttributeError:
            print("Input error!")
            self.settings4()

    def settings5(self):
        cls()
        print('''
        \033[33m  > 动态分区设置 \033[0m
           1> dynamic_partitions簇名\n
           2> [Metadata]元数据插槽数\n
           3> [Metadata]最大保留Size\n
           4> [分区] 默认扇区/块大小\n
           5> [Super] 指定/block大小\n
           6> [Super] 更改物理分区名\n
           7> [Super] 更改逻辑分区表\n
           8> [Super]强制烧写完整Img\n
           9> [Super] 标记分区槽后缀\n
           10>[Payload]靶定HeaderVer\n
           11>返回上一级菜单
           --------------------------
        ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "11":
            return 1
        elif op_pro == '10':
            input('维护中。。。')
        try:
            getattr(self, 'dyset%s' % op_pro)()
            self.settings5()
        except AttributeError:
            print("Input error!")
            self.settings5()

    def settings2(self):
        print(f"修改安卓端在内置存储识别ROM的路径。当前为/sdcard/{settings.mydir}")
        mydir = input('   请输入文件夹名称(英文):')
        if mydir:
            settings.change('mydir', mydir)

    def settings3(self):
        if os.name == "posix":
            for age in ['python3', 'simg2img', 'img2simg', 'cpio', 'sed', 'libnss3-tools', 'python3-pip', 'brotli',
                        'curl', 'bc', 'cpio', 'default-jre', 'android-sdk-libsparse-utils', 'openjdk-11-jre', 'aria2',
                        'p7zip-full']:
                print(f"\033[31m  修复安装{age}\033[0m")
                os.system(f"apt-get install {age} -y")
                print(f"\033[36m  {age}已安装\033[0m")
        else:
            print("非LINUX，无法修复")

    def settings6(self):
        print(f"  打包时ROM作者为：{settings.Romer}")
        Romer = input("  请输入（无特殊字符）: ")
        if Romer:
            settings.change('Romer', Romer)

    def settings7(self):
        print("  首页banner: [1]TIK3 [2]爷 [3]电摇嘲讽 [4]镰刀斧头 [5]镰刀斧头(大) [6]TIK2旧 ")
        banner = input("  请输入序号: ")
        if banner.isdigit():
            if 0 < int(banner) < 6:
                settings.change('banner', banner)

    def settings8(self):
        plugromlit = input("  设置区分ROM/Plug的Size界限[1]125829120 [2]自定义: ")
        if plugromlit == '2':
            plugromlit = input("  请输入：")
            if plugromlit.isdigit():
                settings.change('plugromlit', plugromlit)
        else:
            settings.change('plugromlit', '125829120')

    def packset1(self):
        print(f"  调整brotli压缩等级（整数1-9，级别越高，压缩率越大，耗时越长），当前为：{settings.brcom}级")
        brcom = input("  请输入（1-9）: ")
        if brcom.isdigit():
            if 0 < int(brcom) < 10:
                settings.change('brcom', brcom)

    def packset2(self):
        sizediy = input("  打包Ext镜像大小[1]动态最小 [2]手动改: ")
        if sizediy == '2':
            settings.change('diysize', '1')
        else:
            settings.change('diysize', '')

    def packset3(self):
        print("  ext4打包方案: [1]make_ext4fs [2]mke2fs+e2fsdroid ")
        pack_op = input("  请输入序号: ")
        if pack_op == '1':
            settings.change('pack_e2', '0')
        else:
            settings.change('pack_e2', '1')

    def packset4(self):
        extrw = input("  打包EXT是否可读[1]RW [2]RO: ")
        if extrw == '2':
            settings.change('ext4rw', '')
        else:
            settings.change('ext4rw', '-s')

    def packset5(self):
        erofslim = input("  选择erofs压缩方式[1]是 [2]否: ")
        if erofslim == '1':
            erofslim = input("  选择erofs压缩方式：lz4/lz4hc和压缩等级[1-9](数字越大耗时更长体积更小) 例如 lz4hc,8: ")
            if erofslim:
                settings.change("erofslim", erofslim)
        else:
            settings.change("erofslim", '')

    def packset6(self):
        utcstamp = input("  设置打包UTC时间戳[1]live [2]自定义: ")
        if utcstamp == "2":
            utcstamp = input("  请输入: ")
            if utcstamp.isdigit():
                settings.change('utcstamp', utcstamp)
        else:
            settings.change('utcstamp', '')

    def packset8(self):
        print("  Img是否打包为sparse(压缩体积)[1/0]")
        ifpsparse = input("  请输入序号: ")
        if ifpsparse == '1':
            settings.change('pack_sparse', '1')
        elif ifpsparse == '0':
            settings.change('pack_sparse', '0')

    def packset7(self):
        inodesize = input("  设置EXT分区inode-size: ")
        if inodesize:
            settings.change('inodesize', inodesize)

    def packset9(self):
        typediy = input("  打包镜像格式[1]同解包格式 [2]可选择: ")
        if typediy == '2':
            settings.change('diyimgtype', '1')
        else:
            settings.change('diyimgtype', '')

    def packset10(self):
        pack_op = input("  是否自动补全fs_config[谨慎!]: [1]是 [2]否\n请输入序号: ")
        if pack_op == '2':
            settings.change('auto_fsconfig', '0')
        else:
            settings.change('auto_fsconfig', '1')

    def packset11(self):
        chboottool = input("  默认Boot解、打包工具[1]AndroidImageKitchen [2]MagiskBootKitchen: ")
        if chboottool == '1':
            settings.change('default_boot_tool', 'AIK')
        else:
            settings.change('default_boot_tool', 'MBK')

    def dyset1(self):
        super_group = input(f"  当前动态分区簇名/GROUPNAME：{settings.super_group}\n  请输入（无特殊字符）: ")
        if super_group:
            settings.change('super_group', super_group)

    def dyset2(self):
        slotnumber = input("  强制Metadata插槽数：[2] [3]: ")
        if slotnumber == '3':
            settings.change('slotnumber', '3')
        else:
            settings.change('slotnumber', '2')

    def dyset3(self):
        metadatasize = input("  设置metadata最大保留size(默认为65536，至少512) ")
        if metadatasize:
            settings.change('metadatasize', metadatasize)

    def dyset4(self):
        BLOCKSIZE = input(f"  分区打包扇区/块大小：{settings.BLOCKSIZE}\n  请输入: ")
        if BLOCKSIZE:
            settings.change('BLOCKSIZE', BLOCKSIZE)

    def dyset5(self):
        SBLOCKSIZE = input(f"  分区打包扇区/块大小：{settings.SBLOCKSIZE}\n  请输入: ")
        if SBLOCKSIZE:
            settings.change('SBLOCKSIZE', SBLOCKSIZE)

    def dyset6(self):
        supername = input(f'  当前动态分区物理分区名(默认super)：{settings.supername}\n  请输入（无特殊字符）: ')
        if supername:
            settings.change('supername', supername)

    def dyset7(self):
        superpart_list = input(f'  当前动态分区内逻辑分区表：{settings.superpart_list}\n  请输入（无特殊字符）: ')
        if superpart_list:
            settings.change('superpart_list', superpart_list)

    def dyset8(self):
        iffullsuper = input("  是否创建强制刷入的Full镜像？[1/0]")
        if not iffullsuper == '1':
            settings.change('fullsuper', '')
        else:
            settings.change('fullsuper', '-F')

    def dyset9(self):
        autoslotsuffix = input("  是否标记需要Slot后缀的分区？[1/0]")
        if not autoslotsuffix == '1':
            settings.change('autoslotsuffixing', '')
        else:
            settings.change('autoslotsuffixing', '-x')

    def __init__(self):
        cls()
        print('''
    \033[33m  > 设置 \033[0m
       1> 待定
       2>[Droid]存储ROM目录
       3>[修复]工具部分依赖
       4>[打包]相关细则设置
       5>[动态分区]相关设置
       6>自定义 ROM作者信息
       7>自定义 首页Banner
       8>修改Plug/ROM限Size
       9>返回主页
       --------------------------
    ''')
        op_pro = input("   请输入编号: ")
        if op_pro == "9":
            return
        try:
            getattr(self, 'settings%s' % op_pro)()
            self.__init__()
        except AttributeError as e:
            print(f"Input error!{e}")
            self.__init__()
