Never code another line of SOQL again, instead use SalesForceAlchemy to interact with SalesForce using Python objects.

For instance, you would say the following: (Login)

```
sf = SalesForceAlchemy().username(__sf_account__['username']).password(__sf_account__['password']).endPoint('www.salesforce.com').login()
print 'isLoggedIn=%s' % (sf.isLoggedIn)
if (not sf.isLoggedIn):
    print 'lastError=%s' % (sf.lastError)
```

And then: (Generate some SOQL)

```
results = sf.case.fields('*').filter(Id='put-an-Id-here').order_by('Id').all(debug=1)
```

And then: (Count some records)

```
results = sf.case.fields('*').filter(Id='put-an-Id-here').order_by('Id').count()
```

And then: (Fetch some data)

```
results = sf.case.fields('*').filter(Id='put-an-Id-here').order_by('Id').all()
```

SalesForceAlchemy requires the latest VyperLogixLib-1.0-py2.5.egg that can be downloaded from http://python2.wordpress.com under a separate License.

SalesForceAlchemy requires the latest [pyax](https://launchpad.net/pyax/+download) distro which is under a separate license.