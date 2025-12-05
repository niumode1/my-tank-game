# -*- mode: python ; coding: utf-8 -*-
import os

# 直接通过当前工作目录获取src路径（最稳妥）
src_dir = os.path.join(os.getcwd(), 'src')  # 等价于 D:\tank_war\src

# 所有自定义模块列表
CUSTOM_MODULES = ['tank', 'map', 'sound_manager', 'bullet', 'game_objects']

a = Analysis(
    ['src\\main.py'],
    pathex=[src_dir],  # 告诉PyInstaller src目录的位置
    binaries=[],
    datas=[('assets', 'assets')],  # 打包资源
    hiddenimports=CUSTOM_MODULES,  # 强制包含所有自定义模块
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tank_war',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 保留控制台看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tank_war',
)