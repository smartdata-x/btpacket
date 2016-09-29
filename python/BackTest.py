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


def result(uid, token, sessionid, pos, count):
    '''
    uid       :用户id
    token     :验证串,可以通过登录接口获得
    sessionid :回测条件的id
    pos       :起始位置
    count     :个数
    '''
    url = 'http://61.147.114.87/cgi-bin/backtest/kensho/v1/btresult.fcgi';
    values = {};
    values['uid'] = uid;
    values['token'] = token;
    values['sessionid'] = sessionid;
    values['pos'] = pos;
    values['count'] = count;
 
    try:
        data = urllib.urlencode(values);
        req = urllib2.Request(url, data);
        response = urllib2.urlopen(req);
        the_page = response.read();

        return the_page;
    except Exception as er:
        print(str(er));


def btcondition(uid, token, sondition, start_time, end_time):
  '''
  condition:
  start_time: start time of back test
  end_time: end time of back test
  '''
  fcgi_path = 'http://61.147.114.87/cgi-bin/backtest/kensho/v1/btsentence.fcgi?'
  connector = '&'
  
  uid_str = 'uid=' + uid
  token_str = 'token=' + token
  sondition = urllib.quote(sondition);
  sondition_str = 'sonditions=' + sondition
  start_time = 'start_time=' + start_time
  end_time = 'end_time=' + end_time

  request_url = fcgi_path + uid_str + connector + token_str +connector + start_time + connector + end_time + connector + sondition_str
  #print request_url;
  
  try:
    req = urllib2.Request(request_url)
    response = urllib2.urlopen(req)
    sessionid = response.read()
  
    return sessionid
  except Exception as er:
    print(str(er))

 

def search(uid, token, sonditions):
    '''
    uid       :用户id
    token     :验证串,可以通过登录接口获得
    sondition :用户输入语句
    '''

    sonditions = sonditions + ",";
    url = 'http://61.147.114.67/cgi-bin/phbacktest/search/1/btsearch.fcgi'
    values = []
    values.append(url)
    values.append('?uid=')
    values.append(uid)
    values.append('&token=')
    values.append(token)
    values.append('&sonditions=')
    values.append(_replace_chinese_digits(sonditions.decode('utf-8')))
    url = ''.join(values)
    #print url;
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
     sentence = search(str(uid), token, sonditions);
     ojt = json.loads(sentence);
     body = ojt["body"];
     prompt = body["prompt"];
   except Exception as e:
     print (str(e))

   
   if "basic" in prompt:
     benv = prompt["basic"];
   elif "technology" in prompt:
     benv = prompt["technology"];
   elif "news" in prompt:
     benv = prompt["news"];
   elif "events" in prompt:
     benv = prompt["events"];
   else:
     benv = [];

   l_res = [];
   for d in benv:
     sen = d["mode_sentence"];
     print sen;
   

def _chinese2digits(uchars_chinese):
    '''
    中文转数字
    '''
    total = 0
    r = 1  # 表示单位：个十百千...
    for i in range(len(uchars_chinese) - 1, -1, -1):
        val = common_used_numerals.get(uchars_chinese[i])
        if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
                # total =total +  r * x
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
   获取回测结果
   sonditions :回测条件
   start_time :起始时间
   end_time   :结束时间
   pos        :输出第几个开始的数据
   count      :输出多少个数据
   '''
   
   sentence = search(str(uid), token, sonditions);
   #print sentence;
   ojt = json.loads(sentence);
   body = ojt["body"];
   check = body["check"];

   if "checked_sentences" in check:
     be = check["checked_sentences"];
   else:
     be = [];

   l_condition = [];
   sondition = {};
   for d in be:
     sondition["id"]     = d["id"];
     sondition["type"]   = d["type"];
     sondition["params"] = d["params"];
     l_condition.append(sondition);

   condition = json.dumps(l_condition);
   bt = btcondition(str(uid), token, condition, start_time, end_time);
   ojt = json.loads(bt);
   body = ojt["body"];
   bt_session = body["bt_session"];
   time.sleep(3);
   ret = result(uid, token, str(bt_session), pos, count);
   
   return ret;

def md5en(password):
  # password    ：用户输入的原始密码
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
    print(str(er));


def login(user_name, password, platform_id):
  '''
   user_name   : 用户名
   password    : 密码
   platform_id : 运营部id标识
   callaback   : jsonp回调参数  若没有该字段，结果返回json格式数据 
   test        : http://61.147.114.76/cgi-bin/twookong122/user/1/user_login.fcgi?
                 user_name=kerry&password=85c7860d7f1c777636c38745593f77eb&platform_id=1
  '''
  url = 'http://61.147.114.76/cgi-bin/twookong122/user/1/user_login.fcgi'
  values = {}
  values['user_name'] = user_name
  values['password'] =  md5en(password)
  values['platform_id'] = platform_id
  try:
    data = urllib.urlencode(values);
    req = urllib2.Request(url, data);
    response = urllib2.urlopen(req);
    the_page = response.read();
    ojt = json.loads(the_page);
    ojt = ojt["result"];
    ojt = ojt["user_info"];
    
    print "uid:"   + str(ojt["user_id"]);
    print "token:" + ojt["token"];
  
  except Exception as er:
    print(str(er));

'''
TUDO test
'''
if __name__ == "__main__":
    a = search("10001", "sgsgsd", "连续三天上涨二百三十五万元")
    print a;
