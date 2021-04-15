import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import NcblyItem
from itemloaders.processors import TakeFirst


class NcblySpider(scrapy.Spider):
	name = 'ncbly'
	start_urls = ['https://www.ncb.ly/en/media-center/news/']

	def parse(self, response):
		post_links = response.xpath('//h4/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[text()="Next"]/@href').getall()
		if next_page:
			yield FormRequest.from_response(response, formdata={
				'__EVENTTARGET': 'ctl00$cph_body$pgrCustomRepeater$ctl02$ctl00'}, callback=self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1[@class="new-mc-big-title"]/text()').get()
		description = response.xpath('//div[@class="col col_8_of_12 mc-body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="new-mc-big-date"]/text()').get()

		item = ItemLoader(item=NcblyItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
