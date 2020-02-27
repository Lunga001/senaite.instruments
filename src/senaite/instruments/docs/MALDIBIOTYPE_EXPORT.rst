SENAITE INSTRUMENTS
===================

Import and export instrument adapters for SENAITE

Running this test from the buildout directory::

    bin/test test_doctests -t MALDIBIOTYPER_EXPORT


Test Setup
----------
Needed imports::

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from senaite.instruments.instruments.maldibiotyper.maldibiotyper import maldibiotyperexport
    >>> from bika.lims.exportimport.instruments import IInstrumentExportInterface
    >>> from DateTime import DateTime
    >>> from zope.component import getMultiAdapter
    >>> from zope.component import getAdapter

    >>> from senaite.instruments import instruments
    >>> from zope.publisher.browser import FileUpload, TestRequest


Functional helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)


Variables::

    >>> portal = self.portal
    >>> date_now = timestamp()
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_instruments = bika_setup.bika_instruments
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Instruments
===========

All instruments live in the `/bika_setup/bika_instruments` folder::

    >>> instruments = bika_setup.bika_instruments
    >>> instrument = api.create(instruments, "Instrument", title="Maldi")
    >>> instrument
    <Instrument at /plone/bika_setup/bika_instruments/instrument-1>
    >>> instrument.setDataInterface(['senaite.instruments.instruments.maldibiotyper.maldibiotyper.maldibiotyperexport'])
    >>> instrument.getDataInterface()
    ['senaite.instruments.instruments.maldibiotyper.maldibiotyper.maldibiotyperexport']


Required steps: Create and receive Analysis Request for import test
...................................................................

An `AnalysisRequest` can only be created inside a `Client`, and it also requires a `Contact` and
a `SampleType`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="NARALABS", ClientID="NLABS")
    >>> client
    <Client at /plone/clients/client-1>
    >>> contact = api.create(client, "Contact", Firstname="Juan", Surname="Gallostra")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>
    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="H2O", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

Create an `AnalysisCategory` (which categorizes different `AnalysisServices`), and add to it an `AnalysisService`.
This service matches the service specified in the file from which the import will be performed::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>
    >>> analysisservice1 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HIV06ml",
    ...                              ShortTitle="hiv06",
    ...                              Category=analysiscategory,
    ...                              Keyword="HIV06ml")
    >>> analysisservice1
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

    >>> service_uids = [
    ...     analysisservice1.UID(),
    ... ]

Create an `AnalysisRequest` with this `AnalysisService` and receive it::

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()
    ...          }
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/H2O-0001>
    >>> ar.getReceivedBy()
    ''
    >>> wf = api.get_tool('portal_workflow')
    >>> wf.doActionFor(ar, 'receive')
    >>> ar.getReceivedBy()
    'test_user_1_'
    >>> ar2 = create_analysisrequest(client, request, values, service_uids)
    >>> wf.doActionFor(ar2, 'receive')
    >>> ar3 = create_analysisrequest(client, request, values, service_uids)
    >>> wf.doActionFor(ar3, 'receive')

Create a Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

    >>> ar1_analyses = ar.getAnalyses(full_objects=True)
    >>> ar2_analyses = ar2.getAnalyses(full_objects=True)
    >>> ar3_analyses = ar3.getAnalyses(full_objects=True)
    >>> analyses = ar1_analyses + ar2_analyses + ar3_analyses
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)
    >>> maldibiotyperexport(self).Export(worksheet, request)

