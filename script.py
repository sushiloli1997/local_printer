from py2exe.freeze import freeze

freeze(
    console=[{'script': "testing.py"}],  # Main script
    includes=['frontbackdesign'],  # Include dependent modules
    excludes=[],  # Exclude unnecessary modules
    zipfile=None,  # Bundle libraries into the .exe
    options={
        'bundle_files': 1,  # Bundle all files into a single .exe
    },
    dist_dir='dist',  # Output folder for .exe
)
