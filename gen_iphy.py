# -*- coding: utf-8 -*-
from xml.dom import minidom
import re
import sys
import os

class c_gen_iphy_xml(object):

    def __init__(self, scf_xml, target_xml):
        self.scf_xml = scf_xml
        self.target_xml = target_xml

    def gen_iphy_xml(self, iphy_xnl):
        # three parameters namespaceURI, qualifiedName, doctype
        doc = minidom.getDOMImplementation().createDocument(None, None, None)
        rootElement = doc.createElement('IPHY-Config')
        obsaiElement = doc.createElement('OBSAI-Config')
        obsaisettingElement = doc.createElement('OBSAI-setting')
        rrulistElement = doc.createElement('RRH_List')
        for i in range(len(self.rrulist)):
            rruElement = doc.createElement('RRH')
            rruElement = self.gen_rru_info(doc, rruElement, self.rrulist[i])
            rrulistElement.appendChild(rruElement)
        obsaiElement.appendChild(rrulistElement)
        obsaiElement.appendChild(obsaisettingElement)
        rootElement.appendChild(obsaiElement)
        doc.appendChild(rootElement)

        f = open(iphy_xml, 'w')
        doc.writexml(f, addindent='  ', newl='\n', encoding='utf-8')
        f.close()

    def gen_idE(self, doc, rruname, resourceSWVersion, procode):
        idE = doc.createElement('identity')

        serialnoE = doc.createElement('serialno')
        serialnoE.appendChild(doc.createTextNode("L6144201723"))
        productcodeE = doc.createElement('productcode')
        productcodeE.appendChild(doc.createTextNode(procode))
        productnameE = doc.createElement('productname')
        productnameE.appendChild(doc.createTextNode(rruname))
        hwversionE = doc.createElement('hwversion')
        hwversionE.appendChild(doc.createTextNode("101"))
        buildnameE = doc.createElement('buildname')
        buildnameE.appendChild(doc.createTextNode(resourceSWVersion))
        buildversionE = doc.createElement('buildversion')
        buildversionE.appendChild(doc.createTextNode(resourceSWVersion))

        idE.appendChild(serialnoE)
        idE.appendChild(productcodeE)
        idE.appendChild(productnameE)
        idE.appendChild(hwversionE)
        idE.appendChild(buildnameE)
        idE.appendChild(buildversionE)
        return idE

    def gen_antennaListE(self, doc, rruinfo):
        cellid = rruinfo['celllist'][0] 
        antls = rruinfo['antllist']
        antennaListE = doc.createElement('antennaList')
        for i in antls:
            antid = i['antlid']
            if (int(antid) % 2) == 0:
                antstr = antid +'b'
            else:
                antstr = antid +'a'
            if i['antldir'] != "":
                direction = i['antldir']
                antennaE = doc.createElement('antenna')
                nameE = doc.createElement('name')
                nameE.appendChild(doc.createTextNode("antenna"+ antstr))
                dirE = doc.createElement('dir')           
                dirE.appendChild(doc.createTextNode(direction))
                cellE = doc.createElement('cell')
                cellE.appendChild(doc.createTextNode(str(cellid)))
                antennaE.appendChild(nameE)
                antennaE.appendChild(dirE)
                antennaE.appendChild(cellE)
                antennaListE.appendChild(antennaE)
        return antennaListE

    def gen_hardwareE(self, doc, rruinfo):
        hardwareE = doc.createElement('hardware')

        optlink_ListE = doc.createElement('optlink_List')
        optlinkE = doc.createElement('optlink')

        physicalIdE = doc.createElement('physicalId')
        physicalIdE.appendChild(doc.createTextNode(rruinfo['celllist'][0]))
        virtualIdE = doc.createElement('virtualId')
        virtualIdE.appendChild(doc.createTextNode(rruinfo['celllist'][0]))
        linkRateE = doc.createElement('linkRate')
        linkRateE.appendChild(doc.createTextNode("auto"))

        optlinkE.appendChild(physicalIdE)
        optlinkE.appendChild(virtualIdE)
        optlinkE.appendChild(linkRateE)
        optlink_ListE.appendChild(optlinkE)

        antennaListE = self.gen_antennaListE(doc, rruinfo)

        hardwareE.appendChild(optlink_ListE)
        hardwareE.appendChild(antennaListE)
        return hardwareE

    def gen_softwareE(self, doc, frm_prop, frm_sw):
        softwareE = doc.createElement('software')
        fileE = doc.createElement('file')
        nameE = doc.createElement('name')
        version = frm_prop.split('PROP_')[1].split('.LAR')[0]
        nameE.appendChild(doc.createTextNode(frm_prop))
        usageStatusE = doc.createElement('usageStatus')
        usageStatusE.appendChild(doc.createTextNode('active'))
        versionE = doc.createElement('version')
        versionE.appendChild(doc.createTextNode(version))

        nameE2 = doc.createElement('name')
        nameE2.appendChild(doc.createTextNode(frm_sw))
        usageStatusE2 = doc.createElement('usageStatus')
        usageStatusE2.appendChild(doc.createTextNode('active'))
        versionE2 = doc.createElement('version')
        versionE2.appendChild(doc.createTextNode(version))

        fileE.appendChild(nameE)
        fileE.appendChild(usageStatusE)
        fileE.appendChild(versionE)
        fileE.appendChild(nameE2)
        fileE.appendChild(usageStatusE2)
        fileE.appendChild(versionE2)

        softwareE.appendChild(fileE)
        return softwareE

    def gen_defaultsE(self, doc):
        defaultsE = doc.createElement('defaults')
        managedObjectE = doc.createElement('managedObject')
        managedObjectE.setAttribute('class', "Module")
        managedObjectE.setAttribute('distName', "module")
        stateE = doc.createElement('state')
        stateTypeE = doc.createElement('stateType')
        stateTypeE.appendChild(doc.createTextNode("operational"))
        initStateE = doc.createElement('initState')
        initStateE.appendChild(doc.createTextNode("disabled"))

        stateE.appendChild(stateTypeE)
        stateE.appendChild(initStateE)
        managedObjectE.appendChild(stateE)
        defaultsE.appendChild(managedObjectE)
        return defaultsE

    def gen_supportedFeaturesE(self, doc):
        supportedFeaturesE = doc.createElement('supportedFeatures')
        itemE = doc.createElement('item')
        featureE = doc.createElement('feature')
        featureE.appendChild(doc.createTextNode("HIGHEST_MODULATION_LEVEL"))
        supportE = doc.createElement('support')
        supportE.appendChild(doc.createTextNode("0"))

        itemE.appendChild(featureE)
        itemE.appendChild(supportE)
        supportedFeaturesE.appendChild(itemE)
        return supportedFeaturesE

    def gen_soapE(self, doc, frm_prop, frm_sw):
        soapE = doc.createElement('soap-config')
        softwareE = self.gen_softwareE(doc, frm_prop, frm_sw)
        defaultsE = self.gen_defaultsE(doc)
        supportedFeaturesE = self.gen_supportedFeaturesE(doc)
        soapE.appendChild(softwareE)
        soapE.appendChild(defaultsE)
        soapE.appendChild(supportedFeaturesE)
        return soapE

    def gen_rru_info(self, doc, rruElement, rruinfo):
        idE = self.gen_idE(doc, rruinfo['rruname'], rruinfo['resourceSWVersion'], rruinfo['procode'])
        hardwareE = self.gen_hardwareE(doc, rruinfo)
        soapE = self.gen_soapE(doc, rruinfo['frm_prop'], rruinfo['frm_sw'])

        rruElement.appendChild(idE)
        rruElement.appendChild(hardwareE)
        rruElement.appendChild(soapE)
        return rruElement

    def get_version(self, targetxml, rruname):
        dom = minidom.parse(targetxml)
        root = dom.documentElement
        resourceSWVersion, frm_prop, frm_sw = '', '', ''
        hwResources = root.getElementsByTagName('hwResource')
        swFileKeys = root.getElementsByTagName('swFileKey')
        rruname = rruname.upper()
        for i in hwResources:
            if "_" + rruname in i.getAttribute('resourceBuildKey'):
                resourceSWVersion = i.getAttribute('resourceSWVersion')
        for j in swFileKeys:
            data = j.firstChild.data
            if "_" + rruname + "_FRM-PROP_" in data:
                frm_prop = data.split(rruname + '_')[1]
            if "_" + rruname + "_FRM-SW_" in data:
                frm_sw = data.split(rruname + '_')[1]
        if resourceSWVersion == '':
            raise Exception('Get resourceSWVersion for RRU {} failed'.format(rruname))
        if frm_prop == '':
            raise Exception('Get frm_prop for RRU {} failed'.format(rruname))
        if frm_sw == '':
            raise Exception('Get frm_sw for RRU {} failed'.format(rruname))
        return resourceSWVersion, frm_prop, frm_sw

    def get_info_from_targetxml(self):
        for i in self.rrulist:
            resourceSWVersion, frm_prop, frm_sw = self.get_version(self.target_xml, i['rruname'])
            i['resourceSWVersion'] = resourceSWVersion
            i['frm_prop'] = frm_prop
            i['frm_sw'] = frm_sw

    def get_procode(self):
        for i in self.managedObjects:
            if "com.nokia.srbts.eqm:RMOD" == i.getAttribute('class'):
                distname = i.getAttribute('distName')
                rruid = str(re.search('RMOD-(\d)', distname).group().split('-')[1])
                for j in i.getElementsByTagName('p'):
                    if "prodCodePlanned" == j.getAttribute('name'):
                        procode = str(j.firstChild.data)
                        for i in self.rrulist:
                            if rruid == i['rruid']:
                                i['procode'] = procode
                                i['distname'] = distname

    def get_rrulist(self):
        rrulist = []
        for i in self.managedObjects:
            if "com.nokia.srbts.eqmr:RMOD_R" == i.getAttribute('class'):
                rrudict = {}
                distname = i.getAttribute('distName')
                rrudict['rruid'] = str(distname).split('RMOD_R-')[1]
                for m in i.getElementsByTagName('list'):
                    if 'activeLteCellsList' == m.getAttribute('name'):
                        celllist = []
                        for n in m.getElementsByTagName('p'):
                            cellid = str(n.firstChild.data)
                            celllist.append(cellid)
                        rrudict['celllist'] = celllist
                for p in i.getElementsByTagName('p'):
                    if "productName" == p.getAttribute('name'):
                        rruname = str(p.firstChild.data)
                        rrudict['rruname'] = rruname
                rrulist.append(rrudict)
        return rrulist

    def get_antl(self):
        antlalllist = []       
        for rruinfo in self.rrulist:
            antldict = {}
            antllist = []
            for i in self.managedObjects:
                if "com.nokia.srbts.eqm:ANTL" == i.getAttribute('class'):
                    antldistname = i.getAttribute('distName')                    
                    antlid = str(re.search('ANTL-(\d)', antldistname).group().split('-')[1])
                    at = {}
                    if rruinfo['distname'] in antldistname:
                        at['antlid'] = antlid
                        at['antldir'] = ''
                        antllist.append(at)
            rruid = str(re.search('RMOD-(\d)', rruinfo['distname']).group().split('-')[1])
            for rru in self.rrulist:
                if rru['rruid'] == rruid:
                    rru['antllist'] = antllist
            antldict['rruid'] = rruid
            antldict['antllist'] = antllist
            antlalllist.append(antldict)
        return antlalllist

    def get_channel(self):
        channeldict = {}
        channeldictlist = []
        for i in self.managedObjects:
            if "com.nokia.srbts.mnl:CHANNEL" == i.getAttribute('class'):
                rru_channeldict = {}
                direction = ''
                antlDN = ''
                rru_antl = ''
                for j in i.getElementsByTagName('p'):
                    if "antlDN" == j.getAttribute('name'):
                        antlDN = str(j.firstChild.data)
                        rruid = re.search('RMOD-(\d)', antlDN).group().split('-')[1]
                        antlid = re.search('ANTL-(\d)', antlDN).group().split('-')[1]
                        rru_antl = rruid + '-' + antlid
                    if "direction" == str(j.getAttribute('name')):
                        direction = str(j.firstChild.data)
                    if rru_antl in channeldict:
                        channeldict[rru_antl] = channeldict[rru_antl] + direction
                        if 'RXTX' == channeldict[rru_antl] or 'TXRX' == channeldict[rru_antl]:
                            channeldict[rru_antl] = 'both'
                    else:
                        channeldict[rru_antl] = direction
                rru_channeldict['rruid'] = rruid
                rru_channeldict['antlid'] = antlid
                rru_channeldict['direction'] = channeldict[rru_antl]
                channeldictlist.append(rru_channeldict)
        for rru in self.rrulist:
            for info in channeldictlist:
                if info['rruid'] == rru['rruid']:
                    for antl in rru['antllist']:
                        if antl['antlid'] == info['antlid']:
                            antl['antldir'] = info['direction']

    def get_rruinfo_from_scfc(self):
        dom = minidom.parse(self.scf_xml)
        root = dom.documentElement
        self.managedObjects = root.getElementsByTagName('managedObject')
        self.rrulist = self.get_rrulist()
        self.get_procode()
        self.get_antl()
        self.get_channel()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s",  dest="scf_xml", default='',
                      help='scf xml file')
    parser.add_option("-t",  dest="targetbd_xml", default='',
                      help='targetbd xml file')

    (options, sys.argv[1:]) = parser.parse_args()

    scf_xml = options.scf_xml
    targetbd_xml = options.targetbd_xml
    if scf_xml == '':
        raise Exception('Please input the scfc xml file name.') 
    if targetbd_xml == '':
        raise Exception('Please input the targetbd xml file name.') 
    c = c_gen_iphy_xml(scf_xml, targetbd_xml)
    c.get_rruinfo_from_scfc()
    c.get_info_from_targetxml()
    #print(c.rrulist)
    iphy_xml = os.path.join(os.getcwd(),'iphy.xml')
    c.gen_iphy_xml(iphy_xml)
    print('Iphy xml file is {}, please check.'.format(iphy_xml))
