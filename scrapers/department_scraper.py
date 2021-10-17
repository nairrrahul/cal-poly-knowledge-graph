from models import Department
from autoscraper import AutoScraper
import os
from scraper import registry, Scraper
from bs4 import BeautifulSoup
import requests


@registry.register
class DepartmentScraper(Scraper):

    links = {}

    def compile_links(self):
        URL = "https://catalog.calpoly.edu"
        main_url = requests.get("https://catalog.calpoly.edu/collegesanddepartments/")
        bs = BeautifulSoup(main_url.content, "html.parser")
        urls = bs.find(class_="page_content").findAll("li")
        for i in urls:
            self.links[i.find("a").text] = URL + i.find("a")["href"]

    def scrape(self):
        scraper = AutoScraper()
        self.compile_links()
        config_path = os.path.join("scrapers", "config", "dept_scraper")
        if not os.path.exists(config_path):
            url_i = self.links["Aerospace Engineering"]
            wanted = {
                "program": ["Aerospace Engineering"],
                "course": ["AERO 121. Aerospace Fundamentals."],
                "college": ["College of Engineering"],
            }
            result = scraper.build(url=url_i, wanted_dict=wanted)
            scraper.save(config_path)
        scraper.load(config_path)
        for name, url in self.links.items():
            subsets = scraper.get_result_similar(url, group_by_alias=True)
            try:
                dept = Department.objects.get(name=name)
                dept.programs = list(set(subsets["program"]))
                dept.courses = list(set(subsets["course"]))
                dept.college = subsets["college"][-1]
                dept.save()
            except:
                Department(
                    name=name,
                    programs=list(set(subsets["program"])),
                    courses=list(set(subsets["course"])),
                    college=subsets["college"][-1],
                ).save()
