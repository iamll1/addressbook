import urllib2 as url
import re
from csv import reader

def main():
    infoURL = 'http://oid.nat.gov.tw/infobox1/personmain.jsp'

    try:
        # query data from infoURL
        response = url.urlopen(infoURL)
    except url.URLError, e:
        print 'Open url (%s) failed : %s' % (infoURL, e)
        return
    except ValueError, e:
        print '%s' % e
        return

    info = response.info()
    if _is_big5_charset(info.plist):
        web_data = response.read().decode('big5')
    else:
        web_data = response.read()

    # parser data inside NextLevel tag
    # NextLevel(\'l=\u9ad8\u96c4\u5e02,c=TW\',2,\'\u9ad8\u96c4\u5e02\')
    requestList = []
    for line in re.findall(r'NextLevel\((.*?)\)', web_data, re.M):
        utf_line = line.encode('utf-8')
        if __debug__:
            print "input %s: %s" % (type(utf_line), utf_line)
        requestList.append(utf_line)

    # remove first one, that is not data
    del requestList[0]

    questList = []
    for line in reader(requestList, delimiter=',', quotechar='\''):

        # fetch struct : sDn, sLevel, sTitle
        item_dict = _fetch_struct(line)
        if __debug__:
            print item_dict

        questList.append(item_dict)

    return questList


def _fetch_struct(data):
    """
    item_dict :{ sDn    : data_1,
                   sLevel : data_2,
                   sTitle : data_3
                 }
    """
    item_dict = {}

    # decode o=abcd,c=TW or l=abcd,c=TW
    for params in data[0].split(','):
        for foo in re.findall(r'(\w)=(.*)', params, re.M):
            item_dict[foo[0]] = foo[1]

    item_dict['sLevel'] = data[1]
    item_dict['sTitle'] = data[2]

    return item_dict


def _is_big5_charset(plist):
    assert isinstance(plist, list)

    big5_set_list = ['big5', 'ms950', 'cp950']
    re_pat = re.compile('charset=(?P<CODE>\S*)')

    for item in plist:
        m = re_pat.match(item)
        if not m:
            continue

        if m.group('CODE').lower() not in big5_set_list:
            continue

        return True
    return False

if __name__ == '__main__':
    questList = main()

    if __debug__:
        print (len(questList), questList)


# request to http://oid.nat.gov.tw/infobox1/personmain.jsp
# parameter sTitle sDn sLevel sDn

# save data use OID

# misc
# [l.split(',') for l in re.findall(r'showdata\((.*?)\)', data, re.M)]
