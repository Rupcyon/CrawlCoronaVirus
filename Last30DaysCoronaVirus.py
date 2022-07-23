import requests
import re
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


class CoronaVirusSpider(object):
    def __init__(self):
        self.home_url = 'http://ncov.dxy.cn/ncovh5/view/pneumonia'

    def get_content_from_url(self, url):
        """
        根据URL,获取响应内容的字符串数据
        :param url: 请求的URL
        :return 响应内容的字符串
        """
        response = requests.get(url)
        home_page = response.content.decode()
        return home_page

    def parse_home_page(self, home_page, tag_id):
        """
        解析首页内容，获取解析后的Python数据
        param ： home_page首页的内容
        return : 解析后的python数据
        """
        soup = BeautifulSoup(home_page, 'lxml')
        script = soup.find(id=tag_id)
        text = script.text
        json_str = re.findall(r'\[.+\]', text)[0]
        data = json.loads(json_str)
        return data

    def save(self, data, path):
        with open(path, 'w', encoding='utf8') as fp:
            json.dump(data, fp, ensure_ascii=False)

    def crawl_last_day_corona_virus(self):
        """
        采集最近一天的各国疫情信息
        :return:
        """
        # 1.发送请求，获取首页内容
        home_page = self.get_content_from_url(self.home_url)
        # 2.解析首页内容，获取最近一天的各国疫情数据
        last_day_corona_virus = self.parse_home_page(home_page, "getListByCountryTypeService2true")
        # 3.保存数据
        self.save(last_day_corona_virus, './last_day_corona_virus.json')

    def crawl_corona_virus(self):
        with open('D:\PythonProject\Pachong\last_day_corona_virus.json', encoding='utf8') as fp:
            last_day_corona_virus = json.load(fp)

        for country in tqdm(last_day_corona_virus,'近30天各国疫情数据'):
            corona_virus = []
            statistics_data_url = country['statisticsData']
            statistics_data_json_str = self.get_content_from_url(statistics_data_url)  # 得到各个国家3-7月份的数据
            statistics_data = json.loads(statistics_data_json_str)['data']
            statistics_data = statistics_data[-30:]
            for one_day in statistics_data:
                one_day["provinceName"] = country["provinceName"]
                one_day['countryShortCode'] = country['countryShortCode']
                # append整体放列表，extend元素放列表
            corona_virus.extend(statistics_data)
        self.save(corona_virus, 'D:\PythonProject\Pachong\corona_virus.json')

    def run(self):
        self.crawl_corona_virus()

if __name__ == '__main__':
    spider = CoronaVirusSpider()
    spider.run()
