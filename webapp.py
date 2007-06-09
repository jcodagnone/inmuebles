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

#
# Esta es una peque~na aplicacion web que ayuda a ordenar
# lugares para alquiler. soporta estados y comentarios de usuarios
#

from sys import path
path.append('site-packages')
import web, re

urls = (
    '/',                                    'RootController',
    '/home/',                               'HomeController',
    '/history/',                            'HistoryController',
    '/places/',                             'PlacesController',
    '/map/',                                'MapController',
    '/map/(\w+)/([A-Z0-9-]+)/',             'MapController',
    '/map/data/',                           'DataMapController',
    '/map/data/(\w+)/([A-Z0-9-]+)/js/'  ,   'DataMapController',
    '/map/data/(\w+)/([A-Z0-9-]+)/info/',   'IdDataMapController',
    '/places/(\d+)/',                       'LocalPlacesController',
    '/places/(\w+)/([A-Z0-9-]+)/',          'ProviderPlaceController',
    '/places/(\w+)/([A-Z0-9-]+)/comment/',  'CommentProviderPlaceController',
    '/places/(\w+)/([A-Z0-9-]+)/state/([A-Z ]+)/', 'StateProviderPlaceController',

)

class RootController:
    def GET(self):
        web.seeother('home/')

class HomeController:
    def GET(self):
        print render.header()
        print render.home()
        print render.footer()

class HistoryController:
    def GET(self):
        print render.header()
        print render.history(web.select('action_log',
                             order='date desc', limit=100))
        print render.footer()
    def POST(self):
        self.GET()

class PlacesController:
    def GET(self):
        print render.header()
        print render.places(web.select('places', order='id desc'))
        print render.footer()

class MapController:
    def GET(self, providerName=None, providerId=None):
        print render.header(True)
        print render.map(providerName, providerId)
        print render.footer()

class DataMapController:
    SQL_BBOX ='select  AsText(box2d(Collect(the_geom))) AS the_geom from places'
    SQL_PLACES = 'select id, provider, providerid, AsText(the_geom), state from places'
    rePoint = re.compile('^POINT[(](.*) (.*)[)]$')
    rePolygon  = re.compile('^POLYGON[(][(](.*)[)][)]$')

    def GET(self, provider=None, id=None):
        ret = []
        for i in web.query(self.SQL_PLACES):
            m = self.rePoint.match(i.astext)
            ret.append([int(i.id), i.provider, i.providerid, float(m.group(1)),
                        float(m.group(2)), i.state])
        if provider == None:
            a = web.query(self.SQL_BBOX)[0].the_geom
        else:
            a = web.query("%s WHERE provider = %s and providerid=%s" %
                  (self.SQL_BBOX, web.db.sqlquote(provider),
                   web.db.sqlquote(id)))[0].the_geom
        bound = self.rePolygon.match(a).group(1).split(',')
        print render.map_data(ret, bound[0].split(' '), bound[2].split(' '))


class AbstractDataController:
    def GET(self, providerName, id):
        try:
            model = scrappers[providerName].get(id)
            found = True
        except Exception, e:
            found = False
            web.ctx.status = '404 Not Found'
            print render.header()
            print render.someplace_error(e)
            print render.footer()

        if found:
            self.view(found, model, providerName, id);
   
class IdDataMapController(AbstractDataController):
    def view(self, found, model, providerName, id):
     	print render.map_data_id(model, id, providerName)

class LocalPlacesController:
    """ dado un id, redirije a provider/providerid """
    def GET(self, id):
        r = web.select('places', what='provider, providerid',
                         where='id=%d' % int(id))[0]
        web.seeother('/places/%s/%s/' % (r.provider, r.providerid))

class ProviderPlaceController(AbstractDataController):
    """ GET: muestra informacion de un lugar..
        POST: borra el lugar
    """
    def view(self, found, model, providerName, id):
        lid = scrappers[providerName].local(id)
        comments = web.select('places_forum', where='idplace=%d' % lid, 
                             order='date asc')
        print render.header()
        print render.someplace(model, comments, providerName, id)
        print render.footer()

    def POST(self, providerName, id):
        print id, providerName
        propiedadesDAO.delete(id, providerName)   
        web.seeother('/history/')

class CommentProviderPlaceController:
    """ agrega un comentario a un lugar """
    SQL_INSERT = 'INSERT INTO places_forum VALUES(id, owner, description) VALUES (%d,%s,%s);'
    SQL_ACTION = "INSERT INTO action_log(owner,description) VALUES (%s, %s)"

    def POST(self, providerName, id):
        lid = scrappers[providerName].local(id)
        i = web.input()
        username = usernameProvider.get()

        web.transact() 
        n = web.insert('places_forum', idPlace=lid, owner=username, 
                       description=i.description)
        web.query(self.SQL_ACTION % (web.db.sqlquote(username),
          web.db.sqlquote('agrego un comentario a %s-%s' % (providerName,id))));
        web.commit()
        web.seeother('../')

class StateProviderPlaceController:
    """ agrega un comentario a un lugar """
    SQL_UPDATE = "UPDATE places SET state=%s WHERE id=%d"
    SQL_ACTION = "INSERT INTO action_log(owner,description) VALUES (%s, %s)"

    def POST(self, providerName, id, state):
        lid = scrappers[providerName].local(id)
        web.transact() 
        web.query(self.SQL_UPDATE % (web.db.sqlquote(state), lid))
        web.query(self.SQL_ACTION % (web.db.sqlquote(usernameProvider.get()),
          web.db.sqlquote('cambio al estado %s la prop  %s-%s' % 
             (state,providerName,id))));

        web.commit()
        web.seeother('../../')

#####################
class DbBuscaInmuebleScrapper:
    """ Implementacion de DbBuscaInmuebleScrapper que cachea las propiedades
        en la base de datos
    """
    def __init__(self, propiedadesDAO, buscaInmuebleScrapper, providerName):
        self.d = propiedadesDAO
        self.buscaInmuebleScrapper = buscaInmuebleScrapper
        self.providerName = providerName

    def get(self, id):
        if self.d.has(id, self.providerName) == False:
            ret = self.buscaInmuebleScrapper.get(id)
            self.d.store(id, ret, self.providerName)
        
        ret = self.d.get(id, self.providerName)
        return ret
    def local(self, id):
        return self.d._getLocalId(id, self.providerName)[0].id

class UsernameProvider:
    def get(self):
	ret = 'alguien'
	if 'HTTP_AUTHORIZATION' in  web.ctx.env:
		s = web.ctx.env['HTTP_AUTHORIZATION']
		ret = b64decode(s[6:].strip()).split(':')[0]
        return ret

class PropiedadesDAO:
    SQL_DESCR = "INSERT INTO places_description (id, name, value) VALUES (%d, %s,%s)"
    SQL_PLACE = "INSERT INTO places (the_geom, provider, providerid) VALUES (GeomFromText('POINT(%s)',4326), '%s', '%s')"
    SQL_ACTION = "INSERT INTO action_log(owner,description) VALUES (%s, %s)"

    def __init__(self, usernameProvider):
        self.usernameProvider = usernameProvider;

    def _getLocalId(self, id, provider):
        return web.select('places', what='id',
                   where="providerid=%s and provider=%s" % \
                   (web.db.sqlquote(id), web.db.sqlquote(provider)))

    def has(self, id, provider):
        return len(self._getLocalId(id, provider)) == 1

    def store(self, id, model, providerName,username=None):
        username = self.usernameProvider.get()
        thegeom = model['the_geom']
        del  model['the_geom']
        model['providerName'] = providerName
        model['originalId'] = str(id)
        web.transact() 
        ret = web.query(self.SQL_PLACE  %
                       (thegeom.encode('latin1'), providerName, id))
        appid = web.select("currval('places_id_seq')")[0].currval

        for k,v in model.iteritems():
            sql = self.SQL_DESCR % (appid, web.db.sqlquote(k.encode('latin1')),
                                    web.db.sqlquote(v.encode('latin1')))
            sql = sql.replace('$','S')
            web.query(sql)
        web.query(self.SQL_ACTION % (web.db.sqlquote(username),
            web.db.sqlquote('importo la propiedad %s-%s' % (providerName,id))));
        web.commit()

    def getlocal(self, id):
        ret = {}
        for i in web.select('places_description', where='id=%d' % id):
            ret[i.name] = i.value
        return ret

       
    def get(self, id, providerName):
        ret = {}
        id = self._getLocalId(id, providerName)[0].id
        for i in web.select('places_description', where='id=%s' % id):
            ret[i.name] = i.value

        ret['ESTADO_ZAUBER']  = web.select('places', what='state', where='id=%s' % id)[0].state
        return ret

    def delete(self, id, providerName):
        username = self.usernameProvider.get()
        web.transact() 
        web.delete('places',  where="providerid=%s and provider=%s" % \
            (web.db.sqlquote(id), web.db.sqlquote(providerName)))
        web.query(self.SQL_ACTION % (web.db.sqlquote(username),
                         web.db.sqlquote('elimino propiedad %s-%s' %
                         (providerName, id))));
        web.commit()

#########################################################################
def cgidebugerror():
    """ necesario para engancharlo al apache """
    sys.stdout = web._oldstdout
    cgitb.handler()

    sys.stdout = _wrappedstdout

from base64 import b64decode
from scrapper import *
import os
render = web.template.render('templates/', cache='DEV' not in os.environ)
if 'DEV' in os.environ:
    middleware = [web.reloader]
else:
    middleware = []

if __name__ == "__main__":
    web.config.db_parameters = dict(dbn='postgres', 
                                    user='alquiler', pw='', db='alquiler')
    web.load()
    usernameProvider = UsernameProvider()
    pageContentProvider = HttpPageContentProvider()
    #pageContentProvider = MockPageContentProvider()
    propiedadesDAO = PropiedadesDAO(usernameProvider)
    scrappers = { 
        'clarin':
            DbBuscaInmuebleScrapper(propiedadesDAO,
            AggregateBuscaInmuebleScrapper([
                  MainBuscaInmuebleScrapper(pageContentProvider,
                                           DefaultTextCleanerStrategy()),
                  MapBuscaInmuebleScrapper(pageContentProvider)
               ]), 'clarin'),
         'todopropiedades': 
             DbBuscaInmuebleScrapper(
                propiedadesDAO,
                MainTodoPropiedadesScrapper(
                    HttpTodoPropiedadesContentProvider(),textCleanerStrategy),
               'todopropiedades'),
         'argenprop':
             DbBuscaInmuebleScrapper(propiedadesDAO,
                MainArgenPropScrapper(
                    HttpArgenPropContentProvider(), textCleanerStrategy),
               'argenprop'),
         'flof': DbBuscaInmuebleScrapper(propiedadesDAO, 
                    MainFlofScrapper(HttpFlofContentProvider()), 
                    'flof'),
    }
    
    web.run(urls, globals(), *middleware)
