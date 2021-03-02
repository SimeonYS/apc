import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import ApcItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class ApcSpider(scrapy.Spider):
	name = 'apc'
	start_urls = ['https://www.apc.cw/news/page/1/']

	def parse(self, response):
		articles = response.xpath('//div[contains(@class,"post-item isotope-item clearfix ")]')
		for article in articles:
			date = article.xpath('.//div[@class="date_label"]/text()').get()
			post_links = article.xpath('.//div[@class="post-title"]//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))
		for page in range(2,5):
			next_page = f'https://www.apc.cw/news/page/{page}/'
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):
		title = response.xpath('//h2//text()').get()
		content = response.xpath('//div[@class="column_attr clearfix"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=ApcItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
