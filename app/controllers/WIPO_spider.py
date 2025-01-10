from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import warnings
import time
import pandas as pd
import os
from datetime import datetime

# 忽略弹出的warnings信息
warnings.filterwarnings('ignore')

class Crawler:
    def __init__(self):
        self.chrome_options = Options()
        # chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # self.ser = Service('chromedriver-win64\chromedriver.exe')
        self.ser = Service(os.path.join(current_dir, 'chromedriver-win64\chromedriver.exe'))

        self.driver = webdriver.Chrome(options=self.chrome_options, service=self.ser)
        self.action = ActionChains(self.driver)
        self.datas = []

    def GetUrl(self, url):
        try:
            self.driver.get(url)
        except TimeoutException:
            print(f"加载页面超时: {url}")
        except Exception as e:
            print(f"访问 {url} 时发生错误: {e}")

    def GetInfoByXpath(self, xpath, driver=None, waitTime=60, waitInterval=2):
        target_driver = driver or self.driver
        try:
            WebDriverWait(target_driver, waitTime, waitInterval).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return target_driver.find_elements(By.XPATH, xpath)
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"无法获取元素 (XPath: {xpath}): {e}")
            return []

    def ClickButtonByXpath(self, xpath, driver=None):
        try:
            elements = self.GetInfoByXpath(xpath, driver)
            if elements:
                elements[0].click()
            else:
                print(f"按钮 (XPath: {xpath}) 未找到")
        except Exception as e:
            print(f"点击按钮失败 (XPath: {xpath}): {e}")

    def ClickKey(self, key):
        try:
            ActionChains(self.driver).send_keys(key).perform()
        except Exception as e:
            print(f"按键 {key} 操作失败: {e}")

    def MoveMouseByXpath(self, xpath, driver=None):
        try:
            target = self.GetInfoByXpath(xpath, driver)[0]
            self.action.move_to_element(target).perform()
        except Exception as e:
            print(f"鼠标操作失败 (XPath: {xpath}): {e}")

    def ScrollPage(self, times=100, step=200):
        try:
            for i in range(times):
                self.driver.execute_script(f'window.scrollTo(0, {i * step})')
                time.sleep(0.03)
        except Exception as e:
            print(f"滚动页面时出错: {e}")

    def SetDownloadPath(self, download_path):
        try:
            self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': download_path})
        except Exception as e:
            print(f"设置下载路径失败: {e}")

    def openNewWindow(self, url):
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(url)
        except Exception as e:
            print(f"打开新窗口失败 (URL: {url}): {e}")

    def closeWindow(self):
        try:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            print(f"关闭窗口失败: {e}")

    def Search(self, searchText):
        try:
            searchBox = self.GetInfoByXpath('//*[@id="simpleSearchForm:fpSearch:input"]')[0]
            searchBox.send_keys(searchText + Keys.ENTER)
        except Exception as e:
            print(f"搜索 {searchText} 失败: {e}")

    def SortByDateDescending(self):
        try:
            self.ClickButtonByXpath('//*[@id="resultListCommandsForm:sort:input"]')
            self.ClickButtonByXpath('//*[@id="resultListCommandsForm:sort:input"]/option[2]')
            time.sleep(3)
        except Exception as e:
            print(f"排序失败: {e}")

    def GetInfoUrl(self):
        try:
            pageNum_xpath = '//*[@id="resultListCommandsForm:invalidPageNumber"]/span'
            pageNum = (int)(self.GetInfoByXpath(pageNum_xpath)[0].text.split('/')[-1].strip())  # 获取最大
            # pageNum = 98  # 手动设置爬取的页数
            count = 1
            for i in range(pageNum):
                for tr in self.GetInfoByXpath('//*[@id="resultListForm:resultTable_data"]/tr'):
                    try:
                        url = self.GetInfoByXpath('./td/div/div[1]/div[1]/a', driver=tr)[0].get_attribute('href')
                        title = self.GetInfoByXpath('./td/div/div[1]/div[1]/span[2]/span', driver=tr)[0].text
                        print(f"正在爬取第{count}条专利, 标题：{title}")
                        count += 1

                        date = self.GetInfoByXpath('./td/div/div[1]/div[2]/span[3]', driver=tr)[0].text
                        applicant = self.GetInfoByXpath('./td/div/div[2]/div/div[1]/span[3]/span[2]', driver=tr)[0].text
                        inventor = self.GetInfoByXpath('./td/div/div[2]/div/div[1]/span[4]/span[2]', driver=tr)[0].text
                        abstract = self.GetInfoByXpath('./td/div/div[2]/div/div[2]', driver=tr)[0].text
                        data = [title, applicant, inventor, date, abstract, '', '', '']
                        self.GetOtherInfo(url, data)
                    except StaleElementReferenceException:
                        print("元素引用过时，正在重新定位...")
                        continue  # 重试
                if i+1 != pageNum:
                    self.TryClickNextPage()
        except Exception as e:
            print(f"获取信息失败: {e}")

    def TryClickNextPage(self):
        try:
            nextPageButton = self.GetInfoByXpath('//*[@title="下一页"]', waitTime=10)
            if nextPageButton:
                nextPageButton[0].click()
                time.sleep(3)
            else:
                print("未找到下一页按钮")
        except Exception as e:
            print(f"点击下一页失败: {e}")

    def GetOtherInfo(self, url, data):
        try:
            self.openNewWindow(url)
            li_xpath = '//*[@id="detailMainForm:MyTabViewId"]/ul/li'

            # 等待元素加载，增加等待时间
            self.GetInfoByXpath(li_xpath, waitTime=60)  # 这里增加了最大等待时间

            # 获取所有li元素并处理
            li_elements = self.GetInfoByXpath(li_xpath)
            if not li_elements:
                print(f"未能获取到列表项，跳过 {url}")
                self.closeWindow()
                return

            for li in li_elements:
                try:
                    li.click()
                    infos = self.GetInfoByXpath(
                        '/html/body/div[2]/div[5]/div/div[1]/div[2]/form/div/div/div/div[1]/div/div/div[2]/div/div[2]/div')
                    for info in infos:
                        label = self.GetInfoByXpath('./span[1]', driver=info)[0].text
                        if label == '标题': data[5] = self.GetInfoByXpath('./span[2]', driver=info)[0].text
                        if label == '摘要': data[6] = self.GetInfoByXpath('./span[2]', driver=info)[0].text
                    if self.GetInfoByXpath(li_xpath)[1].text == '说明书':
                        self.GetInfoByXpath(li_xpath)[1].click()
                        data[7] = self.GetInfoByXpath('//*[@id="detailMainForm:MyTabViewId:descriptionPanel"]')[0].text
                except Exception as e:
                    print(f"处理元素时发生错误: {e}")
                    continue  # 出现错误时跳过当前元素

            self.closeWindow()
            self.datas.append(data)
            time.sleep(1)
        except Exception as e:
            print(f"获取其他信息失败: {e}")

    def SaveData(self):
        try:
            final_data = self.ProcessData()
            columns = self.GenerateColumns(len(final_data[0]))
            df = pd.DataFrame(final_data, columns=columns)

            search_keyword = 'zero trust'
            base_dir = os.path.join(os.getcwd(), "Data", search_keyword, "patents")
            os.makedirs(base_dir, exist_ok=True)

            csv_path = os.path.join(base_dir, f"{search_keyword}_patents.csv")
            df = df[["日期", "标题", "申请人", "发明人", "摘要", "标题（全语种）", "摘要（全语种）"]]
            df.replace({'\n': ' ', ',': '，'}, regex=True, inplace=True)

            # 处理标题重复
            title_count = {}
            for i, row in df.iterrows():
                title = row["标题"]
                if title in title_count:
                    title_count[title] += 1
                    df.at[i, "标题"] = f"{title}_{title_count[title]}"
                else:
                    title_count[title] = 1

            df.to_csv(csv_path, index=False, encoding='utf-8-sig')

            self.SaveAsTxt(final_data)
        except Exception as e:
            print(f"保存数据失败: {e}")

    def ProcessData(self):
        final_data = []
        for data in self.datas:
            instructions_content = data[7]
            if len(instructions_content) > 32500:
                split_data = data[:7]
                while len(instructions_content) > 32500:
                    split_data.append(instructions_content[:32500])
                    instructions_content = instructions_content[32500:]
                split_data.append(instructions_content)
                final_data.append(split_data)
            else:
                final_data.append(data)
        return self.FillData(final_data)

    def FillData(self, data):
        max_columns = max(len(row) for row in data)
        for i in range(len(data)):
            while len(data[i]) < max_columns:
                data[i].append('')
        return data

    def GenerateColumns(self, num_columns):
        columns = ["标题", "申请人", "发明人", "日期", "摘要", "标题（全语种）", "摘要（全语种）", "说明书"]
        for i in range(8, num_columns):
            columns.append(f"说明书_{i - 7}")
        return columns

    def SaveAsTxt(self, final_data):
        search_keyword = 'zero trust'
        base_dir = os.path.join(os.getcwd(), "Data", search_keyword, "patents")
        os.makedirs(base_dir, exist_ok=True)

        title_count = {}

        for data in final_data:
            title = data[0]

            # 截断标题至最大240字符
            if len(title) > 240:
                title = title[:240]

            # 替换文件名中的非法字符
            title = title.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_") \
                .replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")

            # 检查标题是否重复，重复时增加编号
            if title in title_count:
                title_count[title] += 1
                title = f"{title}_{title_count[title]}"
            else:
                title_count[title] = 1

            # 处理日期
            date_str = data[3]
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                except ValueError:
                    print(f"无法解析日期：{date_str}")
                    continue

            quarter = self.get_quarter(date)

            # 创建年份和季度文件夹结构
            year_dir = os.path.join(base_dir, str(date.year), quarter)
            os.makedirs(year_dir, exist_ok=True)

            # 保存txt文件
            filename = os.path.join(year_dir, f"{title}_{date_str}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"标题：{data[0]}\n")
                f.write(f"申请人：{data[1]}\n")
                f.write(f"发明人：{data[2]}\n")
                f.write(f"日期：{data[3]}\n")
                f.write(f"摘要：{data[4]}\n")
                f.write(f"标题（全语种）：{data[5]}\n")
                f.write(f"摘要（全语种）：{data[6]}\n")
                f.write(f"说明书：{data[7]}\n")
                f.write("\n")

    def get_quarter(self, date):
        """根据日期获取季度"""
        month = date.month
        if month in [1, 2, 3]:
            return 'Q1'
        elif month in [4, 5, 6]:
            return 'Q2'
        elif month in [7, 8, 9]:
            return 'Q3'
        elif month in [10, 11, 12]:
            return 'Q4'


class WIPOSpider:
    @staticmethod
    async def fetch_WIPO_data(keyword):
        url = 'https://patentscope2.wipo.int/search/zh/search.jsf'
        crawler = Crawler()
        crawler.GetUrl(url)
        # crawler.Search('zero trust')
        crawler.Search(keyword)
        crawler.SortByDateDescending()
        crawler.GetInfoUrl()
        crawler.SaveData()


WIPO_spider = WIPOSpider()