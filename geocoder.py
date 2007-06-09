#!/usr/bin/env python
#
# Copyright (c) 2007 by Juan F. Codagnone <juan.zauber.com.ar>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; dweither version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

from sys import path
path.append('site-packages')
import elementtree.ElementTree as ET
from elementtree.ElementTree import XMLTreeBuilder, fromstring, tostring
import urllib
import htmlentitydefs



class Geocoder:
    """ Clase que resuelve el servicio geocoding de flof.com.ar.
        Este servicio es un servicio interno de flof.com.ar por lo
        que debe obtenerse permiso de flof antes de usarse.
            http://flof.com.ar/info/terms/ 
    """

    url_altura = 'http://flof.com.ar/bin/geocoder/'
    url_esquina = 'http://flof.com.ar/bin/geocoder/intersection/'

    altura_one = ['nombre', 'altura', 'longitud', 'latitud']
    altura_multi = ['nombre', 'altura', 'id']

    def __init__(self):
        self.entities = {};
        for i in htmlentitydefs.entitydefs:
            self.entities[i] = unicode(htmlentitydefs.entitydefs[i], 'latin-1')

    def altura(self, calle, altura, id=-1):
        int(altura)
        int(id)

        ret = []
        tree = self.__request_altura(calle, altura, id)
        a = tree.findall('./calle/')
        if len(a) == 1:
            vars = self.altura_one
        else:
            vars = self.altura_multi

        for i in a:
            ret1 = {}
            for j in i:
                if j.tag in vars:
                    ret1[j.tag] = j.text

            for i in vars:
                ret1[i]
            ret.append(ret1)

        return ret

    def esquina(self, calle1, calle2):
        ret = []
        tree = self.__request_esquina(calle1, calle2)
        a = tree.findall('./intersection/')
        for i in a:
            ret1 = {}
            vars = ['street1', 'street2', 'x', 'y']
            for j in i:
                if j.tag in ['street1', 'street2']:
                    ret1[j.tag] = j.text
                elif j.tag == 'point':
                    ret1['x'] = j.attrib['x'];
                    ret1['y'] = j.attrib['y'];
            for i in vars:
                ret1[i]
            ret.append(ret1)
        return ret

    def __request_xml(self, url):
        y = urllib.urlopen(url)
        ret = y.read()
        y.close()

        parser = XMLTreeBuilder(html=True)
        parser.entity = self.entities
        parser.feed(ret)

        return parser.close()

    def __request_altura(self, calle, altura, id):
        if id == -1:
            a = ''
        else: 
            a = '&id=%s' % id
        url = '%s?calle=%s&alturaCalle=%s%s' % (self.url_altura,
                 urllib.quote(calle), altura, a)
        return self.__request_xml(url)
    def __request_esquina(self, calle1, calle2):
        url = '%s?street1=%s&street2=%s' % (self.url_esquina, 
                 urllib.quote(calle1), urllib.quote(calle2))
        return self.__request_xml(url)



if __name__ == "__main__": 
    import unittest
    class TestSequenceFunctions(unittest.TestCase):
        g = Geocoder()
        def testAlturaSimple(self):
            expected = [{'latitud': '-34.5916558629142', 
                         'nombre': 'CALLAO AV.',
                         'longitud': '-58.3917938499444',
                         'altura': '1500'}]
            self.assertEquals(expected, self.g.altura('callao', 1500))
        def testAlturaMultiple(self):
            expected = [ {'nombre': 'FRAGATA Pres. SARMIENTO',
                          'id': '11348', 'altura': '1500'},
                         {'nombre': 'SARMIENTO', 'id': '10471', 
                         'altura': '1500'}]
            self.assertEquals(expected, self.g.altura('sarmiento', 1500))
        def testEsquinaSimple(self):
            expected = [{'y': '-34.6021131579496', 'street1': 'LAVALLE',
                         'street2': 'FLORIDA', 'x': '-58.3751696375015'}]
            self.assertEquals(expected, self.g.esquina('lavalle', 'florida'))
        def testAlturaSimpleId(self):
            expected = [{'latitud': '-34.6052548661967', 'nombre': 'SARMIENTO',
            'longitud': '-58.387794513211', 'altura': '1500'}]
            self.assertEquals(expected, self.g.altura('sarmiento', 1500, 10471))
        def testEsquinaCompuesto(self):
            expected = [{'y': '-34.6030465660967', 'street1': 'CALLAO AV.',
            'street2': 'LAVALLE', 'x': '-58.3922898323931'}]
            self.assertEquals(expected, self.g.esquina('CALLAO AV.', 
                'LAVALLE'))
    
    unittest.main()
