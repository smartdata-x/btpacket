# coding:utf-8

import urllib
import urllib2
import json
import time
import re
import sys

reload(sys)
sys.setdefaultencoding("utf8")

common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                            '十': 10, '百': 100, '千': 1000}
common_used_numerals = {}
for key in common_used_numerals_tmp:
    common_used_numerals[key.decode('utf-8')] = common_used_numerals_tmp[key]


def _result(uid, token, sessionid, pos, count):
  '''
    回测结果
    uid       :用户id
    token     :验证串,可以通过登录接口获得
    sessionid :回测条件的id
    pos       :起始位置
    count     :个数
  '''
  url = 'http://61.147.114.87/cgi-bin/backtest/kensho/v1/btresult.fcgi'
  values = {}
  values['uid'] = uid
  values['token'] = token
  values['sessionid'] = sessionid
  values['pos'] = pos
  values['count'] = count
  try:
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page
  except Exception as er:
    print(str(er))
    return {}

def btcondition(uid, token, sondition, start_time, end_time):
  '''
    uid        :用户id
    token      :验证串,可以通过登录接口获得
    sondition  :回测条件
    start_time :回测开始时间
    end_time   :回测结束时间
    函数功能   :通过回测条件获取sessionid
  '''
  url = 'http://61.147.114.87/cgi-bin/backtest/kensho/v1/btsentence.fcgi?'
  values = {}
  values['uid'] = uid
  values['token'] = token
  values['sonditions'] = sondition
  values['start_time'] = start_time
  values['end_time'] = end_time
  try:
    data = urllib.urlencode(values);
    print data;
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    sessionid = response.read()
    return sessionid
  except Exception as er:
    print(str(er))
    return {}

def _fuzzy_search(uid, token, conditions):
  '''
  模糊搜索功能
  :param uid: 用户id
  :param token: 验证串,可以通过登录接口获得
  :param conditions: 用户输入语句
  :return: 模糊搜索匹配语句
  '''
  is_decode = True
  conditions = conditions + ","
  if not isinstance(conditions, unicode):
    try:
      conditions = conditions.decode('utf-8')
    except Exception as e:
      is_decode = False
  if is_decode:
    conditions = _replace_chinese_digits(conditions)
  # assemble parameters
  values = []
  search_url = 'http://61.147.114.67/cgi-bin/phbacktest/search/1/btsearch.fcgi'
  values.append(search_url)
  values.append('?uid=')
  values.append(uid)
  values.append('&token=')
  values.append(token)
  values.append('&sonditions=')
  values.append(urllib.quote(conditions))
  url = ''.join(values)
  try:
    req = urllib.urlopen(url)
    response = req.read()
    return response
  except Exception as e:
    print (str(e))

def search_sentence(uid, token, sonditions):
  '''
    获取符合条件的语句
    uid       :用户id
    token     :验证串,可以通过登录接口获得 
    sondition :用户输入语句
  '''
  try:
    sentence = _fuzzy_search(str(uid), token, sonditions)
    ojt = json.loads(sentence)
    body = ojt["body"]
    prompt = body["prompt"]
  except Exception as e:
    print (str(e))
  if "basic" in prompt:
    benv = prompt["basic"]
  elif "technology" in prompt:
    benv = prompt["technology"]
  elif "news" in prompt:
    benv = prompt["news"]
  elif "events" in prompt:
    benv = prompt["events"]
  else:
    benv = []
  l_res = [];
  for d in benv:
    sen = d["mode_sentence"]
    print sen

def _chinese2digits(uchars_chinese):
  '''
  中文数字转阿拉伯数字
  :param uchars_chinese: 需要转换的中文数字
  :return: 转换后的阿拉伯数字
  '''
  total = 0
  r = 1  # 表示单位：个十百千...
  for i in range(len(uchars_chinese) - 1, -1, -1):
    val = common_used_numerals.get(uchars_chinese[i])
    if val is None:
      return uchars_chinese
    else:
      if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
        if val > r:
          r = val
          total = total + val
        else:
          r = r * val
      elif val >= 10:
        if val > r:
          r = val
        else:
          r = r * val
      else:
        total = total + r * val
  return total


def _replace_chinese_digits(sentence):
  '''
  替换中文数字
  :param sentence: 需要替换中文数字的语句
  :return: 替换后的语句
  '''
  total = ''
  all_patten_vec = []
  for i in range(0, len(sentence) - 1, 1):
    var = sentence[i]
    if common_used_numerals.has_key(var):
      total = total + var
      continue
    if total != '':
      all_patten_vec.append(total)
      total = ''
  if total != '':
    all_patten_vec.append(total)
  for var in all_patten_vec:
    digits = _chinese2digits(var)
    sentence = sentence.replace(var, "%d" % digits, 1)
  return sentence.encode('utf-8')

def get_back_result(uid, token, sonditions, start_time, end_time, pos, count):
  '''
    功能:获取回测结果
    sonditions :回测条件
    start_time :起始时间
    end_time   :结束时间
    pos        :输出第几个开始的数据
    count      :输出多少个数据
  '''
  try:
    sentence = _fuzzy_search(str(uid), token, sonditions)
    ojt = json.loads(sentence)
    body = ojt.get("body", "")
    check = body.get("check", "")
    if "checked_sentences" in check:
      be = check["checked_sentences"]
    else:
      be = []
    l_condition = []
    sondition = {}
    for d in be:
      sondition["id"]     = d.get("id", "")
      sondition["type"]   = d.get("type", "")
      sondition["params"] = d.get("params", "")
      l_condition.append(sondition)
    condition = json.dumps(l_condition)
    bt = btcondition(str(uid), token, condition, start_time, end_time)
    ojt = json.loads(bt)
    body = ojt.get("body", "")
    bt_session = body.get("bt_session")
    time.sleep(2)
    ret = _result(uid, token, str(bt_session), pos, count)
    return ret
  except Exception as er:
    return {};
    print(str(er))

def md5en(password):
  '''
    函数功能  ：返回原始密码加密后的字符串
    password  ：用户输入的原始密码
  '''
  url = "http://t.stock.iwookong.com/buildpwd.php"
  values = {}
  values["pwd"] = password
  try:
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    pattern = '.*class="container">(.*)</div'
    result = re.findall(pattern, the_page)
    pwd = result[0]  
    return pwd 
  except Exception as er:
    print(str(er))
    return ''

def login(user_name, password, platform_id):
  '''
    函数功能    :用户登录，返回uid+token
    user_name   : 用户名
    password    : 密码
    platform_id : 运营部id标识
  '''
  url = 'http://61.147.114.76/cgi-bin/twookong122/user/1/user_login.fcgi'
  values = {}
  values['user_name'] = user_name
  if md5en(password) == '':
    print('login faild reason: password')
  values['password'] =  md5en(password)
  values['platform_id'] = platform_id
  try:
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    ojt = json.loads(the_page)
    ojt = ojt.get("result", "")
    ojt = ojt.get("user_info", "")
    print "uid:"   + str(ojt["user_id"])
    print "token:" + ojt["token"] 
  except Exception as er:
    print(str(er))

'''
TUDO test
'''
if __name__ == "__main__":
  a = search("10001", "sgsgsd", "连续三天上涨二百三十五万元")
  print a;
