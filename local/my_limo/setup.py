from setuptools import find_packages
from setuptools import setup
from glob import glob

package_name = 'my_limo'

setup(
    name=package_name,
    version='3.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config/', glob('config/*', recursive=True)),
        ('share/' + package_name + '/launch/', glob('launch/*', recursive=True))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='James Heselden',
    maintainer_email='jheselden@lincoln.ac.uk',
    description='The my_limo package',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mqtt.py = my_limo.scripts.mqtt:main',
            'node_mapper.py = my_limo.scripts.node_mapper:main',
            'edge_mapper.py = my_limo.scripts.edge_mapper:main',
        ],
    },

)
