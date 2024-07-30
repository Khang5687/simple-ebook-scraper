import re
import requests
from utils import load_cookie
from bs4 import BeautifulSoup


class AEL:
    def __init__(self):
        self.url = "https://www.accessengineeringlibrary.com"

        # Validate cookies, if not valid, ask for login

        self.headers = {"Cookie": load_cookie()}

    def getTitle(self, userInput):
        if re.search(
            r"https?://(?:\w+\.)?accessengineeringlibrary\.com/content/book/\d+",
            userInput,
        ):
            url = userInput
        else:
            # URL is not from accessengineeringlibrary.com or does not match the pattern
            if userInput.isdigit():
                # URL is a number
                url = f"{self.url}/content/book/{userInput}"
            else:
                print("Did not reach response.get")
                return None

        # Change URL to /front-matter/preface1
        url = re.sub(r"(/book/\d+).*", r"\1/", url)
        url = url + "front-matter/preface1"

        self.response = requests.get(url)
        if self.response.status_code == 200:
            match = re.search(
                r'name="f\[0\]" value="book_title:([^"]+)"', self.response.text
            )
            book_title = match.group(1) if match else None
            return book_title
        return None

    def getChapters(self):
        """
        This is a headache
        """
        soup = BeautifulSoup(self.response.text, "html.parser")
        toc_list = soup.find("ul", id="toc-list")

        # Find all <li> tags within this <ul>
        li_tags = toc_list.find_all("li")

        self.chapters = []
        # Extract the text from <a> tags within <article> tags under each <li> tag
        for li in li_tags:
            article_tag = li.find("article", class_="toc-list-item")
            if article_tag:
                a_tag = article_tag.find("a")
                if a_tag:
                    href = a_tag["href"]
                    # Filter out sub-sections (href containing '#')
                    if not re.search(r"/book/\d+/.+?#", href):
                        self.chapters.append(a_tag)

        # Print the Chapters
        for chapter in self.chapters:
            # Get all contents of the <a> tag excluding <span> tags
            main_text = "".join(
                [
                    str(content).strip()
                    for content in chapter.contents
                    if not content.name == "span"
                ]
            )
            return main_text

    # TODO: Fetch download links from a_tags

    # TODO: Download the chapters
