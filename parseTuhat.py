import urllib2, re, logging
from selenium.webdriver import Firefox
from contextlib import closing
from functools import partial

FORMAT = 'URL: %(url)s ; %(message)s'
logging.basicConfig(format=FORMAT)
_log_file = logging.getLogger("abstract_extraction")


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
def get_html(url, user_agent=USER_AGENT):
        req = urllib2.Request(url, None, {'User-Agent':user_agent})
        response = urllib2.urlopen(req)
        html = response.read()
        response.close()
        return html

class_attrs = ["abstractSection", "abstract", "pb_abstract", "abstract-content", "svAbstract", "article", "section", "abstractText", "JournalAbstract", "abstract-field", "articleBody_abstract"] 

def class_abstract_extractor(index, browser):
        return browser.find_element_by_class_name(class_attrs[index]).text

find_abstract_by_class = [ partial(class_abstract_extractor, index) for index in range(len(class_attrs))]

def find_abstract_by_id(browser):
        element = browser.find_element_by_id("abstract")
        if element is None:
                element = browser.find_element_by_id("Main_LabelAbstract")
        if element is None:
                element = browser.find_element_by_id("abstractBox")
        return element.text

def find_abstract_by_xpath1(browser):
        return browser.find_element_by_xpath("//div[@id='article-body']/section[1]/div").text

def find_abstract_by_xpath2(browser):
        return browser.find_element_by_xpath("//td/font").text

def find_abstract_by_xpath3(browser):
        return browser.find_element_by_xpath("//p[4]").text

def find_abstract_by_xpath4(browser):
        '''
                When any of the authors has more than one affiliation. The tag index should be increased correspondingly.
                Here, the number of affiliations is assumed to be no more than 3.
        '''
        abstract = browser.find_element_by_xpath("//p[6]").text
        if abstract == "":
                abstract = browser.find_element_by_xpath("//p[7]").text
        if abstract == "":
                abstract = browser.find_element_by_xpath("//p[8]").text
        return abstract

finder_dict = {
                        "www.bioone.org":find_abstract_by_class[0],
                        "apsjournals.apsnet.org":find_abstract_by_class[0],
                        "www.mitpressjournals.org":find_abstract_by_class[0],
                        "epubs.siam.org":find_abstract_by_class[0],
                        "pubsonline.informs.org":find_abstract_by_class[0],
                        "online.liebertpub.com":find_abstract_by_class[0],

                        "gji.oxfordjournals.org":find_abstract_by_class[1],
                        "www.plosone.org":find_abstract_by_class[1],
                        "bioinformatics.oxfordjournals.org":find_abstract_by_class[1],
                        "www.ploscompbiol.org":find_abstract_by_class[1],
                        "www.cell.com":find_abstract_by_class[1],


                        "www.atmos-chem-phys.net":find_abstract_by_class[2],
                        "www.biogeosciences.net":find_abstract_by_class[2],

                        "link.springer.com":find_abstract_by_class[3],
                        "sciencedirect":find_abstract_by_class[4],
                        "ieeexplore.ieee.org":find_abstract_by_class[5],

                        "iwc.oxfordjournals.org":find_abstract_by_class[6],
                        "www.computer.org":find_abstract_by_class[7],
                        "journal.frontiersin.org":find_abstract_by_class[8],
                        "helda.helsinki.fi":find_abstract_by_class[9],
                        "www.degruyter.com":find_abstract_by_class[10],

                        "www.biomedcentral.com": find_abstract_by_xpath1,
                        "www.almob.org": find_abstract_by_xpath1,
                        "journals.cambridge.org":find_abstract_by_xpath4,
                        "www.inderscience.com": find_abstract_by_xpath2,
                        "diglib.eg.org":find_abstract_by_xpath3,
                        "www.scitepress.org":find_abstract_by_id,
                        "pubs.acs.org":find_abstract_by_id,
                        "dl.acm.org":find_abstract_by_id,
                        "www.nature.com":find_abstract_by_id,
                        "onlinelibrary.wiley.com":find_abstract_by_id,
                        "www.igi-global.com":find_abstract_by_id
                        }
       
class Author():
	pass

class Paper():
        '''
                To store the information about the paper.
                The purpose is to extract the meta information of a paper with the doi link.
                Actually the title should also be extracted instead of giving from external.
        '''
        _author = []
        _title = ""
        _paper_link = ""
        _doi = ""
        _abstract = None
        _year = ""

        def __init__(self, doi, title=""):
                self._doi = doi
                self._title = title
                self.abstract_downloader()

        @property
        def abstract(self):
                return self._abstract

        @property
        def title(self):
                return self._title
        @property
        def doi(self):
                return self._doi

        def print_info(self):
                '''
                        The print function can be adujsted according to the specific purpose.
                '''
                print self._doi, self.title, self._abstract


        def abstract_downloader(self):
                if self._abstract is None:
                        with closing(Firefox()) as br:
                                br.get(self._doi)
                                self._link = br.current_url
                                try:
                                        self._abstract = finder_dict[br.current_url.split("/")[2]](br).encode('ascii', 'ignore').replace('\n','')
                                except Exception as e:
                                        _log_file.warning("Error: %s", str(e), extra={'URL':self._link})
class PaperList(list):
        def __init__(self):
                list.__init__(self)
                pass


class TuhatPublicationExtractor():
        '''
                The class aims to scan the tuhat database for faculty of science and to collect all the doi links related to the researchers from Department of Computer Science.
        '''
        def __init__(self):
		self._department = "Department of Computer Science"
		self._publication_url = "https://tuhat.halvi.helsinki.fi/portal/en/organisations-units/faculty-of-science(8d59209f-6614-4edd-9744-1ebdaf1d13ca)/publications.html"
                self._tuhat_paper_link_pattern = re.compile('<h2 class="title"><a .*? href="(.*?)".*?</a></h2>')
                self._author_pattern = re.compile('<a rel="Person".*?<span>(.*?)</span></a>')

                self._page_list_pattern = re.compile('html\?page=(.*?)"><span>')
                self._affiliation_pattern = re.compile('<li class="(.*?)".*?<span>(.*?)</span>.*?</li>')
                self._doi_link_pattern = re.compile('<span>(http:.*doi.*?)</span>')

                self._result = PaperList()

        @property
        def result(self):
                return self._result

        def extract_tuhat_paper_links(self):
                html = get_html(self._publication_url)
                total_page_num = int(self._page_list_pattern.findall(html, re.S)[-2])

                tuhat_paper_links = []
                tuhat_paper_links.extend(self._tuhat_paper_link_pattern.findall(html, re.S))
                for page in range(2, total_page_num-1):
                        html = get_html("%s?page=%d"%(self._publication_url, page-1))
                        tuhat_paper_links.extend(self._tuhat_paper_link_pattern.findall(html, re.S))
                return tuhat_paper_links

        def extract_paper_info(self):
                for url in self.extract_tuhat_paper_links():
			html = get_html(url)
                        affiliation = self._affiliation_pattern.findall(html, re.S)
                        doi = self._doi_link_pattern.findall(html, re.S)
                        title =  html[html.find("<h1>")+4:html.find("</h1>")]
			for key, value in affiliation:
				if value == self._department and doi:
					self._result.append(Paper(doi[0], title))
					break


        def extract_metadata(self, html):
               pass 


if __name__ == "__main__":
        tuhatPaperExtractor = TuhatPublicationExtractor()
        tuhatPaperExtractor.extract_paper_info()
        doi_title = []
        with open('abstract_all_cs.txt', 'w') as abstract_stream:
                for p in tuhatPaperExtractor.result:
                        abstract_stream.write("%s\n"%p.abstract)
                        doi_title.append((p.doi, p.title))
        with open('doi_title_all_cs.txt', 'w') as dta_stream:
                        for doi, title in doi_title:
                                dta_stream.write("%s %s\n"%(doi, title))
