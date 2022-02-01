# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 16:10:19 2022

@author: bperr
"""

from distutils.core import setup, Extension

module_device = Extension('device',
                        sources = ['device.cpp'], 
                        library_dirs=['G:\Program Files\Microsoft SDKs\Windows\v6.1\Lib']
                      )

setup (name = 'WindowsDevices',
        version = '1.0',
        description = 'Get device list with DirectShow',
        ext_modules = [module_device])