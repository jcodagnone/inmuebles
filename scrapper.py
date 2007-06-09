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

# Scrapper de sitios inmobiliarios:
#   API e implementacion para obtener informacion raw de sitios inmobiliarios
#
# Todo scrapper tiene un metodo get(id).
# El id tiene diferentes formas (string, int, ...)..depende del scrapper
# Los scrappers retornan un diccionario de valores. La unica palabra del
# diccionario que todos los scrappers deben retornar es la propiedad the_geom
# con las coordenadas geograficas del inmueble

from sys import path
path.append('site-packages')
import re, sys, codecs, urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from geocoder import *
########### cosas comunes a los scrappers ################################## 

class AbstractHttpContentProvider:
    """ clase base para todos los content providers que vayan por http """

    def __init__(self):
        self.headers = { 
          'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
          'Accept-encoding': 'gzip',
          'Referer':          self.referer,
        }

    def _get(self, url):
        request = urllib2.Request(url)
        for key,value in self.headers.iteritems():
            request.add_header(key,value)
        return urllib2.urlopen(request)

class AbstractMockContentProvider:
    """ clase base para todos los content providers mock  """

    def dumpfile(self, filename):
        f = open(filename)
        s = ''
        for line in f:
            s = s + line
        f.close()
        return s

class AggregateBuscaInmuebleScrapper:
    """ combina multiples *BuscaInmuebleScrapper """

    def __init__(self, arrayBuscaInmuebleScrapper):
        self.arrayBuscaInmuebleScrapper = arrayBuscaInmuebleScrapper

    def get(self, id):
        ret = {}
        for scrapper in self.arrayBuscaInmuebleScrapper:
            ret.update(scrapper.get(id))
        return ret


class DefaultTextCleanerStrategy:
    """ hace legible el texto que queda de las paginas html. 
        remueve  tags html 
    """

    reMultipleSpaces = re.compile(' +');
    reFinalColon= re.compile(':$');

    def clean(self, text):
        s = text.expandtabs(1) \
                .replace('\n', ' ') \
                .replace('\r', ' ')
        return  self.reFinalColon.sub('', 
                  self.reMultipleSpaces.sub(' ', s))

def tabularScraper(table, textCleanerStrategy):
    """ extrae en forma de propiedad todas las filas e una tabla """

    ret = {}
    for i in table.findAll('tr'):
        row = []
        for j in i.findAll('td'):
            text = ''.join([e for e in j.recursiveChildGenerator()
                if isinstance(e, unicode)]).strip()
            row.append(textCleanerStrategy.clean(text))
        if len(row[0]) != 0:
            ret[row[0]] = row[1]
    return ret

########### CLARIN (BUSCA INMUBUEBLE) ################################## 
class MainBuscaInmuebleScrapper: 
    """ retorna un diccionario con datos principales de una propiedades. """

    def __init__(self, pageContentProvider, textCleanerStrategy): 
        self.pageContentProvider = pageContentProvider
        self.textCleanerStrategy = textCleanerStrategy

    def get(self, id):
        soup = BeautifulSoup(self.pageContentProvider.retriveMain(id), 
                             convertEntities="html", smartQuotesTo="html")
        l = soup.findAll('table', width="261")
        if len(l) == 1:
            return tabularScraper(l[0], textCleanerStrategy);
        else:
            raise AssertionError('no se encontro la tabla con datos de la propiedad')

class MapBuscaInmuebleScrapper:
    """ retorna un diccionario con las coordenadas del lugar """

    def __init__(self, pageContentProvider):
        self.pageContentProvider = pageContentProvider

    def get(self, id):
        soup = BeautifulSoup(self.pageContentProvider.retriveMap(id), 
                             convertEntities="html", smartQuotesTo="html")
        l = soup.findAll('iframe')
        if len(l) == 1:
            url = urlparse(l[0]['src'].replace('&amp;', '&'))
            map = dict([n for n in [i.split('=') for i in url[4].split('&')]])
            return {'the_geom': '%s %s' % (map['pos_x'], map['pos_y'])}
        else:
            raise AssertionError('no se encontro la tabla con datos de la propiedad')


class MockPageContentProvider(AbstractMockContentProvider):
    """ provee el contenido de las paginas web...version mock para testeo """

    mainBasePath = 'test/content/main_%d.html'
    mapBasePath  = 'test/content/mapa_%d.html'

    def retriveMain(self, id):
        return self.dumpfile(self.mainBasePath % int(id))
    def retriveMap(self, id):
        return self.dumpfile(self.mapBasePath % int(id))


class HttpPageContentProvider(AbstractHttpContentProvider):
    """ provee el contenido de las paginas web... """

    mainURL = 'http://www.inmuebles.clarin.com/inm/verAviso.do?idAviso=%d'
    mapURL  = 'http://www.inmuebles.clarin.com/inm/verMapa.do?idAviso=%d'
    referer = 'http://www.inmuebles.clarin.com/inm/resultadosBusqueda.do'

    def retriveMain(self, id):
        return self._get(self.mainURL % int(id))

    def retriveMap(self, id):
        return self._get(self.mapURL % int(id))

########### TODO PROPIEDADES ################################## 

class MainTodoPropiedadesScrapper: 
    """ obtiene datos de una propiedad de todopropiedades """

    geocoder = Geocoder()
    reAddress = re.compile('^(.*) (\d+)$')

    def __init__(self, pageContentProvider, textCleanerStrategy): 
        self.pageContentProvider = pageContentProvider
        self.textCleanerStrategy = textCleanerStrategy

    def get(self, id):
        soup = BeautifulSoup(self.pageContentProvider.retrive(id), 
                             convertEntities="html", smartQuotesTo="html")
        l = soup.findAll('table', bordercolor='#FF9D00')
        if len(l) == 1:
            return tabularScraper(l[0], textCleanerStrategy);
        else:
            raise AssertionError('no se encontro la tabla con datos de la propiedad')

class HttpTodoPropiedadesContentProvider(AbstractHttpContentProvider):
    referer = 'http://www.todopropiedades.com/respuesta_prop.phtml'
    URL = 'http://www.todopropiedades.com/respuesta_propmasinfo.phtml?codinmob=%d&codprop=%d&archivo=respuesta_propmasinfo12.shtml'

    def retrive(self, id):
        inmobiliaria, propiedad = id.split('-')
        return self._get(self.URL % (int(inmobiliaria), int(propiedad)))

class MockTodoPropiedadesContentProvider(AbstractMockContentProvider):
    """ provee el contenido de las paginas web...version mock para testeo """
    mainBasePath = 'test/content/todopropiedades_%s.html'

    def retrive(self, id):
        return self.dumpfile(self.mainBasePath % id)

############ Argenprop ################################## 
class MainArgenPropScrapper: 
    """ obtiene datos de una propiedad de http://www.argenprop.com.ar/"""

    def __init__(self, pageContentProvider, textCleanerStrategy): 
        self.pageContentProvider = pageContentProvider
        self.textCleanerStrategy = textCleanerStrategy

    def get(self, id):
        soup = BeautifulSoup(self.pageContentProvider.retrive(id), 
                             convertEntities="html", smartQuotesTo="html")
        l = soup.findAll('table', bgcolor='FFFFFF')
        if len(l) == 1:
            r = tabularScraper(l[0], textCleanerStrategy);
            
            # busco the_geom
            the_geom = None
            for link in soup.findAll('a'):
                s = "javascript:NvaVentana('/netmapas"
                if link['href'].startswith(s):
                    url = urlparse(link['href'][len(s):].replace('&amp;', '&'))
                    d = dict([n for n in [i.split('=') for i in url[4].split('&')]])
                    the_geom = '%s %s' % (d['Lon'], d['LAT'])
                    the_geom = the_geom.replace(',', '.')
            if the_geom == None:
                raise AssertionError('no se encontro las coordenadas')
            else:
                r['the_geom'] = the_geom 
            return r
        else:
            raise AssertionError('no se encontro la tabla con datos de la propiedad')

class HttpArgenPropContentProvider(AbstractHttpContentProvider):
    referer = 'http://www.argenprop.com.ar/index.asp'
    URL = 'http://websinmob.argenprop.com.ar/buscador/masdatos.asp?idpropiedad=%s&sqllook=I'

    def retrive(self, id):
        return self._get(self.URL % id)

class MockArgenPropContentProvider(AbstractMockContentProvider):
    """ provee el contenido de las paginas web...version mock para testeo """
    mainBasePath = 'test/content/argenprop_%s.html'

    def retrive(self, id):
        return self.dumpfile(self.mainBasePath % id)

############ FLOF  ################################## 

class MainFlofScrapper: 
    """ obtiene datos de flof.com.ar """

    def __init__(self, pageContentProvider): 
        self.pageContentProvider = pageContentProvider

    def get(self, id):
        soup = BeautifulSoup(self.pageContentProvider.retrive(id), 
                             convertEntities="xml", smartQuotesTo="xml")
        l = soup.findAll('point')
        if len(l) == 1:
            ret = {}
            ret['the_geom'] = '%s %s' % (l[0]['y'], l[0]['x'])
            ret['labels'] = reduce(lambda x,y: '%s %s' % (x,y), [i['name'] for i in l[0].findAll('label')])
            spot = l[0].findAll('spot')[0]
            for k,v in  spot._getAttrMap().iteritems():
                v = v.strip()
                if v != '':
                    ret[k] = v
            
            return ret
            r = tabularScraper(l[0], textCleanerStrategy);
        else:
            raise AssertionError('no se encontro la tabla con datos de la propiedad')


class HttpFlofContentProvider(AbstractHttpContentProvider):
    referer = 'http://flof.com.ar/'
    URL = 'http://flof.com.ar/bin/spot/lookup/?maxX=90&maxY=180&minY=-180&minX=-90&results=1&orderById=%d'

    def retrive(self, id):
        return self._get(self.URL % int(id))


############ INICIALIZIZACION  ################################## 
textCleanerStrategy = DefaultTextCleanerStrategy()

cpageContentProvider = HttpPageContentProvider()
#cpageContentProvider = MockPageContentProvider()

scrappers = { 'clarin': 
    AggregateBuscaInmuebleScrapper([
        MainBuscaInmuebleScrapper(cpageContentProvider, textCleanerStrategy),
        MapBuscaInmuebleScrapper(cpageContentProvider)
    ]),
    'todopropiedades': MainTodoPropiedadesScrapper(
        HttpTodoPropiedadesContentProvider(), textCleanerStrategy ),
    'argenprop': MainArgenPropScrapper(
        HttpArgenPropContentProvider(), textCleanerStrategy ),
    'flof': MainFlofScrapper(HttpFlofContentProvider()),
}

if __name__ == "__main__":
    sys.stdout = codecs.lookup('latin1')[-1](sys.stdout)
    if len(sys.argv) == 3:
        for key,value in scrappers[sys.argv[1]].get(sys.argv[2]).iteritems():
            print '%30s: %s' % (key, value)
    else:
        print 'Usage: %s proveedor id_de_la_propiedad' % sys.argv[0]
        print 
        print 'Example:  %s clarin 1325956' % sys.argv[0]
        print 'Example:  %s todopropiedades  135-15082' % sys.argv[0]
        print 'Example:  %s argenprop BW38037' % sys.argv[0]
        print 'Example:  %s flof 6479' % sys.argv[0]

