from setuptools import setup

setup(
    name='qtile-widget-tvheadend',
    packages=['tvhwidget'],
    version='0.1.0',
    description=('A qtile widget to show TVHeadend status '
                 'and upcoming recordings.'),
    author='elParaguayo',
    url='https://github.com/elparaguayo/qtile-widget-tvheadend',
    license='MIT',
    install_requires=['qtile>0.14.2', 'requests']
)
