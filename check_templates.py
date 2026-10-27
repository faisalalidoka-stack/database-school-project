import glob
import os
from django.template.loader import get_template

for path in sorted(glob.glob('core/templates/core/**/*.html', recursive=True)):
    name = os.path.relpath(path, 'core/templates').replace(os.sep, '/')
    try:
        get_template(name)
        print('OK     ', name)
    except Exception as e:
        print('ERROR  ', name, '->', e)