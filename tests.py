from main import cfg, MainScreen
from os import listdir, path

with open('test_report.txt','w') as f:
    for file in listdir('CFGs'):
        if file[-4:].lower() == '.cfg':
            f.write('Testing %s.' % file)
            e4_cfg = cfg(path.join('CFGs', file))
            e4_cfg.open()
            if e4_cfg.has_errors:
                f.write('  This file has errors.\n')
                for error in e4_cfg.errors:
                    if error[:5] == 'Error':
                        f.write('   ' + error + '\n')
                f.write('\n')
            else:
                test_screen = MainScreen()
                f.write(' No errors.\n\n')
