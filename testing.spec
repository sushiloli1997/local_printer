from PyInstaller.utils.hooks import collect_data_files
from PyInstaller import __main__

# Collect asset files (images, fonts, etc.)
datas = collect_data_files('asset')  # This will include files from 'asset' folder

# Include specific directories and files
additional_datas = [
    ('generated_cards', 'generated_cards'),  # Include 'generated_cards' directory
    ('frontbackdesign.py', '.')  # Include the 'frontbackdesign.py' file in the root
]

# Combine the collected datas and the additional ones
datas += additional_datas

a = Analysis(
    ['testing.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,  # This will include the necessary asset, generated_cards, and frontbackdesign.py files
    hiddenimports=['qrcode'],  # Include hidden imports if needed
    hookspath=[],
    runtime_hooks=[],
    excludes=[]
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='testing',
    debug=True,   # Enable debugging output
    console=True,  # Show the console window
    icon=None     # You can specify an icon for your executable
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,  
    strip=False,
    upx=True,
    name='testing'
)
