# SalesForce Alchemy - provides an ORM-type interface for SalesForce via pyax and pyax_utils.

from vyperlogix.classes.MagicObject import MagicObject2

from vyperlogix.sf.sf import SalesForceQuery
from vyperlogix.sf.abstract import SalesForceAbstract
from vyperlogix.wx.pyax.SalesForceLoginModel import SalesForceLoginModel

from vyperlogix.misc import _utils
from vyperlogix.hash import lists

from vyperlogix.classes.SmartObject import SmartFuzzyObject

__copyright__ = """\
(c). Copyright 1990-2008, Vyper Logix Corp., All Rights Reserved.

Published under Creative Commons License 
(http://creativecommons.org/licenses/by-nc/3.0/) 
restricted to non-commercial educational use only., 

See also: http://www.VyperLogix.com and http://www.pypi.info for details.

THE AUTHOR VYPER LOGIX CORP DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

USE AT YOUR OWN RISK.
"""

class SalesForceObjectException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
        
class SalesForceFieldException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
        
class SalesForceParmException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
        
class SalesForceOrderByException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
        
class SalesForceAlchemy(MagicObject2,SalesForceAbstract):
    def __init__(self,username=None,password=None,token=None):
        self.__sfQuery__ = None
	self.__lastError__ = ''
	self.__factory = None
	self.__save_result = []
	self.__save_result_isValid = False
	self.__description__ = None
	self.__descriptions__ = SmartFuzzyObject({})
	self.__names__ = None
	self.object_name = None

        self.__username__ = username
        self.__password__ = password
        self.__token__ = token
        self.__endPoint__ = None
        self.__sfLoginModel__ = None
        self.__api_version__ = 14
        self.__types__ = lists.HashedFuzzyLists2()
        self.__objectStack__ = []
        self.__fieldsStack__ = []
        self.__filterStack__ = []
        self.__orderByStack__ = []
        self.__quoted__ = lambda val:"'" if (not str(val).isdigit()) else ''
	
        self.__reset_magic__()
        
    def __tokenize_password__(self):
        if (isinstance(self.__token__,str)):
            self.__password__ = str(self.__password__) + self.__token__
            self.__token__ = None

    def api_version():
        doc = "api_version - default is 14.0 however any valid value works so long as SalesForce supports it."
        def fget(self):
            return self.__api_version__
        def fset(self, api_version):
            self.__api_version__ = _utils.only_float_digits(str(api_version))
        return locals()
    api_version = property(**api_version())

    def lastError():
        doc = "lastError property"
        def fget(self):
            return self.__sfLoginModel__.lastError
        return locals()
    lastError = property(**lastError())

    def isLoggedIn():
        doc = "isLoggedIn property"
        def fget(self):
            return self.__sfLoginModel__.isLoggedIn
        return locals()
    isLoggedIn = property(**isLoggedIn())
    
    def __make_soql__(self):
        where_clause = []
        while (len(self.__filterStack__) > 0):
            aFilter = self.__filterStack__.pop()[0]
            where_clause.append(' and '.join(['%s.%s=%s%s%s' % (self.object_prefix,k,self.__quoted__(v),v,self.__quoted__(v)) for k,v in aFilter.iteritems()]))
        where_clause = ['(%s)' % (where) for where in where_clause]
        order_by_clause = []
        while (len(self.__orderByStack__) > 0):
            item = self.__orderByStack__.pop()[0]
            if (item in self.description.fieldnames):
                order_by_clause.append('%s.%s' % (self.object_prefix,item))
                break
            else:
                raise SalesForceOrderByException('Cannot use the field named "%s" in an ORDER BY clause for SalesForce Object named "%s".' % (item,self.object_name))
	if (len(order_by_clause) == 1):
	    order_by_clause.insert(0,'')
        from_clause = ' FROM %s %s%s' % (self.object_name,self.object_prefix,' WHERE %s' % (' and '.join(where_clause)) if (len(where_clause) > 0) else '')
        soql = 'SELECT %s%s%s' % (', '.join(self.names),from_clause,' ORDER BY '.join(order_by_clause) if (len(order_by_clause) > 0) else '')
        soql_count = 'SELECT COUNT()%s' % (from_clause)
        return soql,soql_count
    
    def __getattr__(self,name):
        t = self.__types__[name]
        if (t is not None):
            self.__objectStack__.append(t)
            return self
        return super(SalesForceAlchemy, self).__getattr__(name)
    
    def __call__(self,*args,**kwargs):
        super(SalesForceAlchemy, self).__call__(*args,**kwargs)
        n = self.n.pop()
        a = list(args)
        a.append(kwargs)
        if (n == 'endPoint'):
            self.__endPoint__ = a
        elif (n == 'login'):
            self.__tokenize_password__()
            self.__sfLoginModel__ = SalesForceLoginModel(username=self.__username__,password=self.__password__)
            if (isinstance(self.__endPoint__,list)):
                self.__sfLoginModel__.api_version = self.__api_version__
                self.__endPoint__ = self.__endPoint__[0] if (len(self.__endPoint__) > 0) else 'www.salesforce.com'
            if (self.__endPoint__.find('://') == -1):
                self.__endPoint__ = self.__sfLoginModel__.get_endpoint(end_point=self.__endPoint__)
            self.__sfLoginModel__.perform_login(end_point=self.__endPoint__)
            if (self.isLoggedIn):
                for t in self.__sfLoginModel__.sfdc.describe_global_response['types']:
                    self.__types__[t] = t
		self.__sfQuery__ = SalesForceQuery(self.__sfLoginModel__)
        elif (n == 'username'):
            self.__username__ = a[0] if (len(a) > 0) else ''
        elif (n == 'password'):
            self.__password__ = a[0] if (len(a) > 0) else ''
        elif (n == 'token'):
            self.__token__ = a[0] if (len(a) > 0) else ''
        elif (n == 'fields'):
            self.__fieldsStack__.append(a)
        elif (n == 'filter'):
            self.__filterStack__.append(a)
        elif (n == 'order_by'):
            self.__orderByStack__.append(a)
        elif (n == 'all') or (n == 'count'):
            try:
                object_name = self.__objectStack__.pop()
            except IndexError:
                raise SalesForceObjectException("Required Object Name was not present.  Object Name must appear like this (sf.case.fields('*').filter(Id='value-of-Id').order_by('Name').all()) with each Object Name being present in the target SalesForce Org.")
            self.object_name = object_name
            fields = []
            names = self.description.fieldnames
            try:
                while (len(self.__fieldsStack__) > 0):
                    field = self.__fieldsStack__.pop()[0]
                    if (field == '*'):
                        fields = names
                        break
                    elif (field in names):
                        fields.append(field)
                    else:
                        raise SalesForceFieldException('Field with name of "%s" is not present in the SalesForce object named "%s".' % (field,self.object_name))
            except Exception, _details:
		info_string = _utils.formattedException(details=_details)
                raise SalesForceParmException('Cannot process the field specifications for object named "%s".\n%s' % (self.object_name,info_string))
            self.namesCanonicalized(fields)
            soql,soql_count = self.__make_soql__()
            results_count = self.sf_query(soql_count)
	    if (n == 'count'):
		if (kwargs.has_key('debug')) and (kwargs['debug']):
		    return soql,soql_count,results_count[0]
		else:
		    return results_count[0]
	    else:
		if (int(results_count[0]['size'][0]) > 1):
		    pass
		elif (kwargs.has_key('debug')) and (kwargs['debug']):
		    return soql,soql_count,results_count[0]
		else:
		    return self.sf_query(soql)
        self.__reset_magic__()
        return self

if (__name__ == '__main__'):
    import sys
    print >>sys.stdout, __copyright__
    print >>sys.stderr, __copyright__
    
    from maglib.salesforce.auth import credentials
    from maglib.salesforce.auth import magma_molten_passphrase
    
    _use_staging = False
    __sf_account__ = credentials(magma_molten_passphrase,0 if (not _use_staging) else 1)
    
    #sf = SalesForceAlchemy(username=__sf_account__['username'],password=__sf_account__['password']).endPoint('www.salesforce.com').login()
    #print 'isLoggedIn=%s' % (sf.isLoggedIn)
    #if (not sf.isLoggedIn):
        #print 'lastError=%s' % (sf.lastError)
    
    sf = SalesForceAlchemy().username(__sf_account__['username']).password(__sf_account__['password']).endPoint('www.salesforce.com').login()
    print 'isLoggedIn=%s' % (sf.isLoggedIn)
    if (not sf.isLoggedIn):
        print 'lastError=%s' % (sf.lastError)

    results = sf.case.fields('*').filter(Id='500300000035KA4AAM').order_by('Id').all(debug=1)
    print results
    
    results = sf.case.fields('*').filter(Id='500300000035KA4AAM').order_by('Id').count()
    print results
    
    results = sf.case.fields('*').filter(Id='500300000035KA4AAM').order_by('Id').count(debug=1)
    print results
    
    results = sf.case.fields('*').filter(Id='500300000035KA4AAM').order_by('Id').all()
    print results

    results = sf.case.fields('*').filter().order_by('Id').all()
    print results
 