from datetime import date, timedelta

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class RjSaoGoncaloSpider(BaseGazetteSpider):
    TERRITORY_ID = "3304904"
    allowed_domains = ["saogoncalo.rj.gov.br", "pmsg.rj.gov.br"]
    name = "rj_sao_goncalo"
    start_urls = ["https://www.saogoncalo.rj.gov.br/diario-oficial/"]

    start_date = date(1998, 2, 3)
    edition_url = "https://servicos.pmsg.rj.gov.br/diario/{}.pdf"

    def parse(self, response):
        increment = timedelta(days=1)
        current_date = self.start_date
        while current_date < date.today():
            yield response.follow(
                url=self.edition_url.format(current_date.strftime("%Y_%m_%d")),
                method="HEAD",
                callback=self.parse_edition,
                errback=self.missing_edition,
                cb_kwargs={"current_date": current_date},
            )
            current_date += increment

    def parse_edition(self, response, current_date):
        yield Gazette(date=current_date, file_urls=[response.url], power="executive")

    def missing_edition(self, failure):
        current_date = failure.request.cb_kwargs.get("current_date")
        self.logger.warning(f"Could not find gazette for {current_date}")
