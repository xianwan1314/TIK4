>*Notice*
> Powered By MIO-KITCHEN-ENVS
####  **介绍** 


1.  【 **TI Kitchen 4.0** 】 是一个永久开源的ROM工具箱，支持安卓全版本


2.  已支持大多常见镜像的分解/打包，较完善支持erofs/V-AB分区等

3.  新增设置功能-调整交互习惯、打包行为

4.  已支持目前安卓14新机型，包括但不限于Xiaomi OPPO Pixel等

5.  Magisk Boot Kitchen & AndroidImagineKitchen双方案分解合成[boot|exaid|recovery/etc].img
    
6.  支持分解全版本super.img(V-AB)支持各种类型打包（半自动识别，高效稳定）

####  **支持** 

【 **识别分解 打包支持** 】

1. 【 *.zip, *.br, *.dat, ext4/2 *.img, bootimg 等】传统镜像识别-分解-打包
2. 【 Super.img <A-onloy/AB/V-AB>, bootimg<header3>, erofs *.img,  等】较新镜像识别-分解-打包
3. 【 dtbo，dtb , TWRP, ops, ofp, ozip, payload.bin, *.win000-004, *.dat.1~20等】特殊文件的解包/打包
4. 较完善适配最新 **安卓14** **Erofs** **动态分区** **V-AB分区**


【 **软件架构  同时支持** 】

1. 手机 Termux Proot Ubuntu 20.04及以上版本 Arm64[aarch64] 或者 <Linux Deploy> Chroot Ubuntu 20.04及以上版本 Arm64[aarch64] 【推荐chroot，效率更高】

2. 虚拟机或实体机 Ubuntu 20.04及以上版本 x86_64[x64] 

3. 不再支持Cygwin

4. 电脑 Win10/11上的Wsl/Wsl2 Ubuntu 20.04及以上版本 x86_64[x64]

Note: WSL 可能存在权限出错的问题 请自行判断测试！


####  **安装教程** 

    git clone https://gitee.com/yzdhz/TIK TIK3
    sudo chmod 777 ./TIK3/run.sh
    ./TIK3/run.sh

####  **【手机端】** 

1----运行Termux 获取存储权限 

    termux-setup-storage

2----一键配置proot并下载工具

    bash <(curl -s https://gitee.com/yeliqin666/proot-ubuntu/raw/master/onekey_install.sh)


####  **使用说明** 

1.  Termux内所有操作尽量【 **不要使用系统root功能** 】， PC端需要root权限(sudo) 且最好不要在【root用户登录状态下】运行此工具，以免打包后刷入手机出现权限问题 ！

2.   **关于手机解压zip** 
    - 请将zip文件放置在【 **内置存储 /sdcard/TIK3** 】，工具会自动查找（设置中可以修改)

3.  手机端termux proot ubuntu下工具目录： 【**/data/data/com.termux/files/home/ubuntu/root/TIK** 】

4.  **请勿删除【工程目录/TI_config文件夹】，打包时所需的文件信息都在此处，默认工具会自动帮您修改大小，适配动态分区！（可自行调整）

5.  由于手机性能、proot效率、工作模式( **如打包img前自动比对fs_config，不会立刻打包** )等原因，保持耐心，等待片刻即可；

6.  删除文件尽量在【Termux或proot ubuntu】执行 【rm -rf 文件、文件夹】 【 **不要使用系统root功能 ** 】

7.   **不要放在含有中文名文件夹下运行，可能支持选择带有空格的文件进行解包(如果有报错欢迎提issues)，工程文件夹不得有空格或其他特殊符号 ，文件名不要过长！！！** 

8.   **动态分区不允许单刷其中的任意分区，具体请参见安卓文档** 

10.  手机上使用工具时如果使用 **系统ROOT** 对工程目录下进行了操作(比如： **添加文件，修改文件**等。。。 )，请记得给操作过的文件或文件夹  **777**  满权！！！



####  **参与维护途径**

  请发起PR，我们将会第一时间查看并考虑是否通过，感谢所有为本项目提供支持的开发者/爱好者！ 


####  **交流反馈** 

  QQ群：[939212867](https://jq.qq.com/?_wv=1027&k=HOJVFqzP)( 点击群号即可加群 )



####  **免责声明** 

1.  本工具在Termux proot环境中运行，不需要root权限 【 **请在Termux中慎用系统root功能** 】 ！！！

2.  此工具不含任何【破坏系统、获取数据】等其他不法代码 ！！！

3.  **如果由于用户利用root权限对工具中的工程目录进行操作导致的数据丢失、损毁，不承担任何责任 ！！！** 


