# -*- coding: utf-8 -*-
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def get_company_name(body):
    if not body:
        return []
    company_str_list = (u'公司', u'厂', u'经营部', u'商行')
    company_name_list = []
    for company_str in company_str_list:
        results = re.findall('(?<=[ ->]).*?(?<=%s)' %(company_str), body)
        for cp in results:
            cp = re.sub(u'.*(?<=[|\.-; =",@\'>\b：])', '', cp)
            if cp and len(cp) > 12 and len(cp) < 60:
                company_name_list.append(cp)
    return list(set(company_name_list)) if company_name_list else company_name_list

chinese_symbol=u'\uff0d\u3002\u2502\u3003\uff1f\uff01\uff0c\u3001\uff1b\uff1a\u300c\u300d\u300e\u300f\u2018\u2019\u201c\u201d\u3014\u3015\u3010\u3011\u2014\u2026\u2013\uff0e\u300a\u300b\u3008\u3009\u26e4\u3000\xa0'
english_symbol=u' !@"#$%*-_=+,./<>?;:\'{}|\\'
SYMBOL= chinese_symbol + english_symbol

def get_company_name_from_title(title):
    company_name_set = []
    company_str_list = (u'\u516c\u53f8', u'\u7ecf\u8425\u90e8', u'\u5546\u884c', u'\u5382')
    for ele in company_str_list:
        if title[::-1].startswith(ele[::-1]):
            _, pos = find_first_of(title[::-1], SYMBOL)
            if pos <= len(title):
                company_name = title[::-1][:pos][::-1]
                company_name_set.append(company_name)
            if pos > len(title):
                company_name_set.append(title)
        else:
            pos = title.find(ele)
            if pos == -1:
                continue
            company_name = title[:(pos + len(ele))]
            _, pos = find_first_of(company_name[::-1], SYMBOL)
            if pos <= len(title):
                company_name = company_name[::-1][:pos][::-1]
                company_name_set.append(company_name)
            else:
                company_name_set.append(company_name)
    return company_name_set

def get_address(body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    if not body:
        return []
    content = re.findall(u'(?<=地址[ ：:]).*?(?=[ <])', body)
    if not content:
        content = re.findall(u'(?<=地&nbsp;&nbsp;址[ ：:]).*?(?=[ <])', body)
        if not content:
            return None
    address = []
    for addr in content:
        args = re.split(u'[：:]+', addr, 1)
        if len(args) == 2:
            address.append(args[1])
        else:
            address.append(addr)
    return address

def get_telephone(body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    #body = w3lib.html.remove_tags(body)
    body = w3lib.html.replace_entities(body)
    body = body.replace(u'\xa0', u'')
    if not body:
        return []
    content = re.findall(u'(?<=电话[ ：:]).*(?=[ <])', body)
    #content = re.findall(u'(?<=\u7535\u8bdd[ ：:]).*?(?=[ <])', body)
    #telephone = []
    if not content:
        #content = re.findall(u'(?<=电&nbsp;&nbsp;话[ ：:]).*?(?=[ <])', body)
        content = re.findall(u'(?<=固话[ ：:]).*(?=[ <])', body)
        #content = re.findall(u'(?<=\u5ea7\u673a[ ：:]).*?(?=[ <])', body)
        if not content:
            content = re.findall(u'(?<=座机[ ：:]).*(?=[ <])', body)
            if not content:
                content = re.findall(u'(?<=热线[ ：:]).*(?=[ <])', body)
                if not content:
                    return None
    #for tel in content:
    #    ret = re.search(u'\d+', tel)
    #    if not ret:
    #        continue
    #    args = re.split(u'[：:]+', tel, 1)
    #    if len(args) == 2:
    #        telephone.append(args[1])
    #    else:
    #        telephone.append(tel)
    #return telephone
    return content

def get_mail( body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    if not body:
        return []
    content = re.findall(u'(?<=邮箱[ ：:]).*?(?=[ <])', body)
    mailSet = []
    if not content:
        content = re.findall(u'(?<=邮&nbsp;&nbsp;箱[ ：:]).*?(?=[ <])', body)
        if not content:
            content = re.findall(u'(?<=[Ee]-mail[ ：:]).*?(?=[ <])', body)
            if not content:
                return None
    for mail in content:
        ret = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', mail)
        if not ret:
            continue
        mailSet.append(mail)
    return mailSet

def get_fax(body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    if not body:
        return []
    content = re.findall(u'(?<=传真[ ：:]).*?(?=[ <])', body)
    faxSet = []
    if not content:
        content = re.findall(u'(?<=传&nbsp;&nbsp;真[ ：:]).*?(?=[ <])', body)
        if not content:
            return None
    for fax in content:
        #ret = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', mail)
        #if not ret:
        #    continue
        faxSet.append(fax)
    return faxSet

def get_site( body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    if not body:
        return []
    content = re.findall(u'(?<=网址[ ：:]).*?(?=[ <])', body)
    siteSet = []
    if not content:
        content = re.findall(u'(?<=网&nbsp;&nbsp;址[ ：:]).*?(?=[ <])', body)
        if not content:
            return None
    for site in content:
        #ret = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', mail)
        #if not ret:
        #    continue
        siteSet.append(site)
    return siteSet

def get_mp(body):
    #pdb.set_trace()
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    #body = w3lib.html.remove_tags(body)
    #body = w3lib.html.remove_tags(body)
    body = w3lib.html.replace_entities(body)
    body = body.replace(u'\xa0', u'')
    if not body:
        return []
    content = re.findall(u'(?<=手机[ ：:]).*(?=[ <])', body)
    #content = re.findall(u'(?<=\u624b\u673a[ ：:]).*?(?=[ <])', body)
    mpSet = []
    if not content:
        content = re.findall(u'(?<=手机号码[ ：:]).*(?=[ <])', body)
        if not content:
            #content = re.findall(u'(?<=手&nbsp;&nbsp;机[ ：:]).*?(?=[ <])', body)
            content = re.findall(u'(?<=热线[ ：:]).*(?=[ <])', body)
            if not content:
                return None
    for mp in content:
        #ret = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', mail)
        #if not ret:
        #    continue
        mpSet.append(mp)
    return mpSet

def get_contacter( body):
    #pdb.set_trace()
    body = w3lib.html.replace_entities(body)
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    if not body:
        return []
    content = re.findall(u'(?<=[:： ]).*?(?<=[男女]士)', body)
    contacterSet = []
    if not content:
        content = re.findall(u'(?<=联系人[ ：:]).*?(?=[ <\xa0\t])', body)
        if not content:
            return None
    for contacter in content:
        #ret = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', mail)
        #if not ret:
        #    continue
        contacterSet.append(contacter)
    return contacterSet

def clearNumber(number):
    if not number:
        return None
    target = u'!"#$%&*=+_/。，；'
    for char in target:
        number = number.replace(char, u'')
    return number

def clearNumberChinese(number):
    if not number:
        return None
    ret = re.findall(u'([\u4e00-\u9fa5]+)', number)
    for ele in ret:
        if number:
            number = number.replace(ele, u'')

    return number

def clearCompany_name(company_name):
    if not company_name:
        return None
    company_name_set = extract_company_name(company_name)
    if company_name_set:
        company_name = company_name_set[0]
    else:
        return None
    return company_name.strip(SYMBOL)

def find_first_of(target, split_set):
    find_ch = ''
    find_pos = len(target) + 100
    for ch in split_set:
        pos = target.find(ch)
        if pos == -1:
            continue
        if pos < find_pos:
            find_pos = pos
            find_ch = ch
    return find_ch, find_pos

def extract_company_name(title):
    if not title:
        return []
    #extract from title
    company_name_set = []
    #sel = Selector(text = body)
    #title = sel.xpath('//title/text()').extract()[0].strip()
    company_str_list = (u'\u516c\u53f8', u'\u7ecf\u8425\u90e8', u'\u5546\u884c', u'\u5382')
    for ele in company_str_list:
        if title[::-1].startswith(ele[::-1]):
            _, pos = find_first_of(title[::-1], SYMBOL)
            if pos <= len(title):
                company_name = title[::-1][:pos][::-1]
                company_name_set.append(company_name)
            if pos > len(title):
                company_name_set.append(title)
        else:
            pos = title.find(ele)
            if pos == -1:
                continue
            company_name = title[:(pos + len(ele))]
            _, pos = find_first_of(company_name[::-1], SYMBOL)
            if pos <= len(title):
                company_name = company_name[::-1][:pos][::-1]
                company_name_set.append(company_name)
            else:
                company_name_set.append(company_name)
    return company_name_set

def numberClearChinese(number):
    if not number:
        return None
    number = re.sub(u'[\u4e00-\u9fa5]+', u' ', number)
    return number

def numberClearChineseSymbol(number):
    if not number:
        return None
    number = re.sub(u'[{0:s}]+'.format(chinese_symbol), u' ', number)
    return number


def clearTelephone(telephone):
    if not telephone:
        return None
    #result = re.findall(u'[0-9-()（） ]{7,18}', telephone)
    #result = re.findall(u'(\(\d{3,4}\)|\d{3,4}[- ]|\s)?\d{8}', telephone)
    result = re.findall(u'(?:\(\d{3,4}\)|\d{3,4}[- ]|\s)(?:\d{7,8})', telephone)
    filter_result = []
    #for pattern in [u'400', u'800', u'86', u'+86', u'(86)', u'（86）']:
    for ele in result:
        for pattern in [u'400', u'800']:
            if not ele.startswith(pattern):
                filter_result.append(ele)
    if filter_result:
        filter_result = [ele for ele in filter_result if ele]
        filter_result = [ele.strip() for ele in filter_result]
        filter_result = list(set(filter_result))
        check_set = [ele for ele in filter_result if len(ele)>8]
        if check_set:
            return check_set
        #return filter_result
    result = re.findall(u'(?:13[0-9]|14[5|7]|15[0-3]|15[5-9]|18[0,5-9])(?:\d{8})', telephone)
    #result = re.findall(u'(?:\(86\)|\+86|\+\(86\)|86\s)?(?:13[0-9]|14[5|7]|15[0-3]|[5-9]|18[0,5-9])(?:\d{8})', mp)
    filter_result = []
    for ele in result:
        for pattern in [u'400', u'800']:
            if not ele.startswith(pattern):
                filter_result.append(ele)
    if filter_result:
        filter_result = [ele for ele in filter_result if ele]
        filter_result = [ele.strip() for ele in filter_result]
        filter_result = list(set(filter_result))
        check_set = [ele for ele in filter_result if len(ele)==11]
        if check_set:
            return check_set
        return filter_result
    return None

def clearTelephoneSet(telephone_set):
    result = []
    if not telephone_set:
        return None
    for telephone in telephone_set:
        ret = clearTelephone(telephone)
        if ret:
            result.extend(ret)

    result = list(set(result))
    check_result = [ele for ele in result if ele and len(ele) > 8]
    if check_result:
        return check_result
    else:
        return result

def clearMp(mp):
    if not mp:
        return None
    #result = re.findall(u'(?:(13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))(?:\d{8})', mp)
    result = re.findall(u'(?:13[0-9]|14[5|7]|15[0-3]|15[5-9]|18[0,5-9])(?:\d{8})', mp) 
    #result = re.findall(u'(?:\(86\)|\+86|\+\(86\)|86\s)?(?:13[0-9]|14[5|7]|15[0-3]|[5-9]|18[0,5-9])(?:\d{8})', mp)
    filter_result = []
    for ele in result:
        for pattern in [u'400', u'800']:
            if not ele.startswith(pattern):
                filter_result.append(ele)
    if filter_result:
        filter_result = [ele for ele in filter_result if ele]
        filter_result = [ele.strip() for ele in filter_result]
        filter_result = list(set(filter_result))
        check_set = [ele for ele in filter_result if len(ele)==11]
        if check_set:
            return check_set
        return filter_result
    #result = re.findall(u'[0-9-()（） ]{7,18}', telephone)
    #result = re.findall(u'(\(\d{3,4}\)|\d{3,4}[- ]|\s)?\d{8}', telephone)
    result = re.findall(u'(?:\(\d{3,4}\)|\d{3,4}[- ]|\s)(?:\d{7,8})', mp)
    filter_result = []
    #for pattern in [u'400', u'800', u'86', u'+86', u'(86)', u'（86）']:
    for ele in result:
        for pattern in [u'400', u'800']:
            if not ele.startswith(pattern):
                filter_result.append(ele)
    if filter_result:
        filter_result = [ele for ele in filter_result if ele]
        filter_result = [ele.strip() for ele in filter_result]
        filter_result = list(set(filter_result))
        check_set = [ele for ele in filter_result if len(ele)>8]
        if check_set:
            return check_set
        return filter_result
    return None

def clearMpSet(mp_set):
    result = []
    if not mp_set:
        return None
    for mp in mp_set:
        ret = clearMp(mp)
        if ret:
            result.extend(ret)

    result = list(set(result))
    check_result = [ele for ele in result if ele and len(ele) == 11]
    if check_result:
        return check_result
    else:
        return result

def clearContactorNumbers(contactor):
    if not contactor:
        return None

    result = re.sub(u'[0-9]+', u'', contactor)
    return result

def telephoneMatchFilter(telephone_set):
    if not telephone_set:
        return None

    result = []
    for ele in telephone_set:
        if re.match(u'(?:\(\d{3,4}\)|\d{3,4}[- ]|\s)(?:\d{7,8})', ele):
            result.append(ele)

    if not result:
        return telephone_set
    return result

def tel2mp(telephone, mp):
    telephone_final = u''
    mp_final = u''
    if re.match(u'(?:\(\d{3,4}\)|\d{3,4}[- ]|\s)(?:\d{7,8})', telephone):
        telephone_final = telephone
    else:
        if re.match(u'(?:\(\d{3,4}\)|\d{3,4}[- ]|\s)(?:\d{7,8})', mp):
            telephone_final = mp

    if re.match(u'(?:13[0-9]|14[5|7]|15[0-3]|15[5-9]|18[0,5-9])(?:\d{8})', mp):
        mp_final = mp
    else:
        if re.match(u'(?:13[0-9]|14[5|7]|15[0-3]|15[5-9]|18[0,5-9])(?:\d{8})', telephone):
            mp_final = telephone
    return telephone_final, mp_final

def get_contacter(body):
    body = body.replace(u' ', u'')
    body = body.replace(u'\u3000', u'')
    if not body:
        return []
    content = re.findall(u'(?<=[:： ]).*?(?<=[男女]士)', body)
    contacterSet = []
    if not content:
        content = re.findall(u'(?<=联系人[ ：:]).*?(?=[ <\xa0\t])', body)
        if not content:
            return None
    for contacter in content:
        if re.match(u'[\u4e00-\u9fa5]+', contacter):
            contacterSet.append(contacter)
    return contacterSet
