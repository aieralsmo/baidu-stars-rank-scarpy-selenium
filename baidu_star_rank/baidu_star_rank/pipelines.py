# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pandas as pd

import re

class CSVStarRankPipeline(object):


	def process_item(self, item, spider):

		# 获取文件存储路径
		week_file_save_path = spider.settings.get('WEEK_FILE_SAVE_PATH')
		week_ud_file_save_path = spider.settings.get('WEEK_UD_FILE_SAVE_PATH')
		month_file_save_path = spider.settings.get('MONTH_FILE_SAVE_PATH')

		data = []
		item = dict(item)
		if item["banner_tab"] == "月榜":
			date = item["date"]
		else:
			
			s = item["date"]
			pattern = r'.*?(\d+\.\d+\.\d+).*?'
			r = re.compile(pattern)
			d = re.findall(r,s)
			if d:
				d1 = d[0].replace('.','-')
				d2 = d[1].replace('.','-')
				date = d1+"~"+d2
			else:
				date = item["date"]
		items = {
			"排名": item["rank"],
			"明星": item["name"],
			"百分比": item["percentage"],
			"搜索量": str(item["value"]).replace(',', '').replace('k',''),
			"趋势": item["trend"],
			"日期": date,
			"指数类型": item["type_tab"],
			"榜类型": item["banner_tab"]

		}

		try:
			data.append(items)
			df = pd.DataFrame(data=data)
			if item["banner_tab"] == "周榜":
				file_save_path = week_file_save_path
			elif item["banner_tab"] == "周上升榜":
				file_save_path = week_ud_file_save_path
			elif item["banner_tab"] == "月榜":
				file_save_path = month_file_save_path

			df.to_csv(file_save_path, encoding="UTF-8", index=False, mode='a', header=False)
			# print("成功写入一条数据！")
			
		except Exception as e:
			with open('save_error.log', 'a',encoding="UTF8") as wf:
				wf.write(e.message)
		finally:
			return item
			




