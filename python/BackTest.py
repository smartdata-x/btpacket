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
  
class btpacket:
  
  def __init__(self, platform_id, user_name, password):
    self.__uid = -1
    self.__platform_id = platform_id
    self.__user_name = user_name
    self.__password = password
    self.__token = ''
    self.__sessionid = ''
    self.http = 'http://61.147.114.76/cgi-bin/backtest/'
	
	
  def __result(self, pos, count):
    '''
      回测结果
      uid       :用户id
      token     :验证串,可以通过登录接口获得
      sessionid :回测条件的id
      pos       :起始位置
      count     :个数
    '''
    url = self.http + "kensho/1/btresult.fcgi"
    values = {}
    values['uid'] = self.__uid
    values['token'] = self.__token
    values['sessionid'] = self.__sessionid
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
  
  def __btcondition(self, sondition, start_time, end_time):
    '''
      uid        :用户id
      token      :验证串,可以通过登录接口获得
      sondition  :回测条件
      start_time :回测开始时间
      end_time   :回测结束时间
      函数功能   :通过回测条件获取sessionid
    '''
    url = self.http + "kensho/1/btsentence.fcgi"
    values = {}
    values['uid'] = self.__uid
    values['token'] = self.__token
    values['sonditions'] = sondition
    values['start_time'] = start_time
    values['end_time'] = end_time
    try:
      data = urllib.urlencode(values);
      req = urllib2.Request(url, data)
      response = urllib2.urlopen(req)
      sessionid = response.read()
      return sessionid
    except Exception as er:
      print(str(er))
      return {}
  
  def __fuzzy_search(self, conditions):
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
      conditions = btpacket.__replace_chinese_digits(self, conditions)
    # assemble parameters
    values = []
    search_url = self.http + "search/1/btsearch.fcgi"
    values.append(search_url)
    values.append('?uid=')
    values.append(str(self.__uid))
    values.append('&token=')
    values.append(self.__token)
    values.append('&sonditions=')
    values.append(urllib.quote(conditions))
    url = ''.join(values)
    try:
      req = urllib.urlopen(url)
      response = req.read()
      return response
    except Exception as e:
      print (str(e))
  
  def __chinese2digits(self, uchars_chinese):
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
  
  
  def __replace_chinese_digits(self, sentence):
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
      digits = btpacket.__chinese2digits(self, var)
      sentence = sentence.replace(var, "%d" % digits, 1)
    return sentence.encode('utf-8')
  
  def __md5en(self, password):
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

  def __return_blank(self, num):
    ret = ""
    for i in range(0, num):
      ret += " "
    return ret

  def __parse_stock(self, stock_json):
    try:
      ojt = json.loads(stock_json)
      body = ojt.get("body", "")
      stocks = body.get("stocks", "")

      l_stocks = []
      stock_info = {}
      print "symbol   trade     changepercent   amount      volume        name"
      for d in stocks:
        s = ""

        stock_info["symbol"]   = d.get("symbol", "")
        s += str(stock_info["symbol"])
        num = 9 - len(str(stock_info["symbol"]))
        s += btpacket.__return_blank(self, num)

        stock_info["trade"]            = d.get("trade", "")
        s += str(stock_info["trade"])
        num = 10 - len(str(stock_info["trade"]));
        s += btpacket.__return_blank(self, num)
        
        stock_info["changepercent"]          = d.get("changepercent", "")
        s += str(stock_info["changepercent"])
        num = 16 - len(str(stock_info["changepercent"]))
        s += btpacket.__return_blank(self, num)

        stock_info["amount"]           = d.get("amount", "")
        s += str(stock_info["amount"])
        num = 12 - len(str(stock_info["amount"]))
        s += btpacket.__return_blank(self, num)

        stock_info["volume"]          = d.get("volume", "")
        s += str(stock_info["volume"])
        num = 14 - len(str(stock_info["volume"]))
        s += btpacket.__return_blank(self, num)

        stock_info["name"]          = d.get("name", "")
        s += str(stock_info["name"])
        
        l_stocks.append(stock_info)
        
        print s
      
      
      return l_stocks;
    except Exception as er:
      print(str(er))
      return [];
    
  
  def login(self):
    '''
      函数功能    :用户登录，返回uid+token
      user_name   : 用户名
      password    : 密码
      platform_id : 运营部id标识
    '''
    url = 'http://61.147.114.76/cgi-bin/twookong122/user/1/user_login.fcgi'
    values = {}
    values['user_name'] = self.__user_name
    password = btpacket.__md5en(self, self.__password)
    if password == '':
      print('login faild reason: password')
      return
    values['password'] =  password
    values['platform_id'] = self.__platform_id
    try:
      data = urllib.urlencode(values)
      req = urllib2.Request(url, data)
      response = urllib2.urlopen(req)
      the_page = response.read()
      ojt = json.loads(the_page)
      ojt = ojt.get("result", "")
      ojt = ojt.get("user_info", "")

      self.__uid = int(ojt["user_id"])
      self.__token = ojt["token"]

    except Exception as er:
      print(str(er))
	  
  def search_sentence(self, sonditions):
    '''
      获取符合条件的语句
      uid       :用户id
      token     :验证串,可以通过登录接口获得 
      sondition :用户输入语句
    '''
    try:
      sentence = btpacket.__fuzzy_search(self, sonditions)
      ojt = json.loads(sentence)
      body = ojt["body"]
      prompt = body["prompt"]
    except Exception as e:
      print (str(e))
      return

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
  
  def get_back_result(self, sonditions, start_time, end_time, pos, count, return_choice):
    '''
      功能:获取回测结果
      sonditions :回测条件
      start_time :起始时间
      end_time   :结束时间
      pos        :输出第几个开始的数据
      count      :输出多少个数据
    '''
    try:
      sentence = btpacket.__fuzzy_search(self, sonditions)
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
        sondition ["id"]    = d.get("id", "")
        sondition["type"]   = d.get("type", "")
        sondition["params"] = d.get("params", "")
        l_condition.append(sondition)
      condition = json.dumps(l_condition)
      bt = btpacket.__btcondition(self, condition, start_time, end_time)
      ojt = json.loads(bt)
      body = ojt.get("body", "")
      bt_session = body.get("bt_session")
      self.__sessionid = str(bt_session);
      time.sleep(3)
      ret = btpacket.__result(self, pos, count)
      if return_choice is 1:
        ret = btpacket.__parse_stock(self, ret)
      else:
        btpacket.__parse_stock(self, ret)
      return ret
    except Exception as er:
      print(str(er))
      return {};
  
  def get_next_result(self, pos, count, return_choice):
    try:
      ret = btpacket.__result(self, pos, count)
      if return_choice is 1:
        ret = btpacket.__parse_stock(self, ret)
      else:
        btpacket.__parse_stock(self, ret)
      return ret;
    except Exception as er:
      print(str(er))
      return {}
  '''
  TUDO test
  '''
  if __name__ == "__main__":
    a = search("10001", "sgsgsd", "连续三天上涨二百三十五万元")
    print a;
  
