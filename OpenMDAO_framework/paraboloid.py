# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 09:26:01 2015

@author: frankpatterson
"""

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class Paraboloid(Component):
    """ Evaluates the equation f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3 """

    # set up interface to the framework
    x = Float(0.0, iotype='in', desc='The variable x')
    y = Float(0.0, iotype='in', desc='The variable y')

    f_xy = Float(0.0, iotype='out', desc='F(x,y)')


    def execute(self):
        """f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3
            Minimum: x = 6.6667; y = -7.3333
        """

        x = self.x
        y = self.y

        print 'X =', x, 'Y =', y, '    calculating...'
        self.f_xy = (x-3.0)**2 + x*y + (y+4.0)**2 - 3.0