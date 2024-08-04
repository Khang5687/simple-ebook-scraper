import os
import re
import requests
import threading
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import load_cookie


class AEL:
    def __init__(self):
        self.session = requests.Session()

        # Update cookies and headers
        cookies_dict = load_cookie()
        self.session.cookies.update(cookies_dict)

        # Headers to bypass "Access Denied" when trying to download certain chapters
        self.session.headers.update(
            {
                "Host": "www.accessengineeringlibrary.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                "Accept-Language": "en,en-US;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://www.accessengineeringlibrary.com/",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Cookie": load_cookie(is_str=True),
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
            }
        )
        self.url = "https://www.accessengineeringlibrary.com"
        self.chapters = []
        self.chapter_links = []
        # self.failed_downloads = {
        #     "count": 0,
        #     "chapter": [],
        # }

        # TODO: Validate cookies, if not valid, ask for login

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

        # Remove all the subdirectories from the URL
        # Example: https://www.accessengineeringlibrary.com/content/book/9780071793056
        url = re.sub(r"(/book/\d+).*", r"\1/", url)
        # Append /front-matter/preface1 to the url
        placeholder_url = url + "front-matter/preface1"
        self.response = self.session.get(placeholder_url)
        if self.response.status_code == 200:
            match = re.search(
                r'name="f\[0\]" value="book_title:([^"]+)"', self.response.text
            )
            book_title = match.group(1) if match else None
            return book_title
        return None

    def getChapters(self) -> str:
        """
        This method retrieves the chapters of the book as a string for printing.
        The actual HTML elements array can be accessed by self.chapters.

        Returns:
            str: The string representation of the chapters
        """
        soup = BeautifulSoup(self.response.text, "html.parser")
        toc_list = soup.find("ul", id="toc-list")

        # Find all <li> tags within this <ul>
        li_tags = toc_list.find_all("li")

        # Find the chapter name and href links
        # Extract the text from <a> tags within <article> tags under each <li> tag
        for li in li_tags:
            article_tag = li.find("article", class_="toc-list-item")
            if article_tag:
                a_tag = article_tag.find("a")
                if a_tag:
                    href = a_tag["href"]
                    # Filter out sub-sections (href containing '#')
                    if not re.search(r"/book/\d+/.+?#", href):
                        # a_tag is an HTML element, so we can access its attributes like href
                        # Get the chapter name
                        chapter_name = "".join(
                            [
                                str(content).strip()
                                for content in a_tag.contents
                                if not content.name == "span"
                            ]
                        )
                        # Page link is the URL + href attribute of the <a> tag
                        chapter_page_link = self.url + href

                        # Chapter template to store the chapter name and page link
                        # Later to be appended to self.chapters list
                        chapter_template = {
                            "name": chapter_name,
                            "page_link": chapter_page_link,
                        }
                        self.chapters.append(chapter_template)

    def downloadChapters(self, use_threading=True):
        """Download chapters via PDF links from self.chapters

        Args:
            use_threading (bool, optional): Enable threading to allow multiple download sessions. Defaults to True.
        """
        # Create a directory to store the downloaded files
        if not os.path.exists("segments"):
            os.makedirs("segments")

        def download_chapter(chapter, index):
            chapter_name = chapter["name"]
            chapter_link = chapter["page_link"]

            # Generate the file path to save the downloaded file with an index
            file_path = f"segments/{index:03d}_{chapter_name}.pdf"

            # Send a GET request to get PDF download link
            # print("Sending request to {}".format(chapter_link))
            response = self.session.get(chapter_link)
            chapter_download_link = re.search(r'href="([^"]+\.pdf)"', response.text)

            # Check if the chapter has a PDF download link
            if chapter_download_link is None or response.status_code != 200:
                print(f"Failed to find download link for {chapter_name}.pdf")
                return

            chapter_download_link = self.url + chapter_download_link.group(1)
            # Send a GET request to download the PDF file with stream=True
            response = self.session.get(chapter_download_link, stream=True)

            # Check if the request was successful
            if response.status_code == 200:
                total_size = int(response.headers.get("content-length", 0))
                block_size = 1024  # 1 Kibibyte
                t = tqdm(
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    desc=f"Downloading {chapter_name}.pdf",
                )

                # Save the downloaded file to the specified file path
                with open(file_path, "wb") as file:
                    for data in response.iter_content(block_size):
                        t.update(len(data))
                        file.write(data)
                t.close()

                if total_size != 0 and t.n != total_size:
                    print(f"Failed to download {chapter_name}.pdf")
                else:
                    print(f"Downloaded {chapter_name}.pdf")
            else:
                print(f"Failed to download {chapter_name}.pdf")

        # Download the chapters in order
        if use_threading:
            threads = []
            for index, chapter in enumerate(self.chapters):
                thread = threading.Thread(
                    target=download_chapter, args=(chapter, index)
                )
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()
        else:
            for index, chapter in enumerate(self.chapters):
                download_chapter(chapter, index)

    # TODO: Handle error when downloading chapters, i.e. PyPDF2.errors.PdfReadError: EOF marker not found which indicates that the cookie is invalid
