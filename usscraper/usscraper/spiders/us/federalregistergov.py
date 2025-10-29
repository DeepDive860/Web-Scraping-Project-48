
import os
import time
import logging
import requests
import asyncio
from typing import Optional

import scrapy


def solve_2captcha_direct(api_key: str, site_key: str, page_url: str,
                          poll_interval: float = 5.0, timeout: int = 120) -> str:
    """
    Submit a reCAPTCHA v2 job to 2captcha and poll for the solution.
    Returns the solved token (string) or raises RuntimeError/TimeoutError.
    (This is synchronous/blocking and intended to be run in a thread.)
    """
    IN_URL = "http://2captcha.com/in.php"
    RES_URL = "http://2captcha.com/res.php"

    params = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
    }

   
    r = requests.post(IN_URL, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"2captcha in.php HTTP {r.status_code}: {r.text}")
    text = r.text.strip()
    if not text:
        raise RuntimeError("Empty response from 2captcha in.php")
    if text.startswith("OK|"):
        captcha_id = text.split("|", 1)[1]
    else:
     
        raise RuntimeError(f"2captcha in.php error: {text}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll_interval)
        resp = requests.get(RES_URL, params={"key": api_key, "action": "get", "id": captcha_id}, timeout=30)
        rtext = resp.text.strip()
        if not rtext:
            continue
        if rtext == "CAPCHA_NOT_READY":
            continue
        if rtext.startswith("OK|"):
            token = rtext.split("|", 1)[1]
            if not token:
                raise RuntimeError("2captcha returned OK but empty token")
            return token
 
        raise RuntimeError(f"2captcha res.php error: {rtext}")

    raise TimeoutError("Timed out waiting for 2captcha result")



class FederalRegisterDocumentSpider(scrapy.Spider):
    name = "federalregisterdocument"
    
    start_urls = [
        "https://www.federalregister.gov/documents/search?conditions%5Bsearch_type_id%5D=3&conditions%5Bterm%5D=%22information+collection%22+%26+%22omb+control+number%22&order=newest"
    ]

    custom_settings = {
     
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 0.5,
      
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 60000,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False}, 
    }

 
    site_key = "6LfpbQcUAAAAAMw_vbtM1IRqq7Dvf-AftcZHp_OK"

    
    TWO_CAPTCHA_KEY = "b655159829d6d1be4c9879f4c939e34b"
  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.TWO_CAPTCHA_KEY:
            self.logger.warning("TWOCAPTCHA_KEY not provided. Captcha solving will fail without it.")

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True, 
                },
                callback=self.parse, 
            )

   
    async def parse(self, response):
        self.logger.info("Loaded search page: %s", response.url)
        page = response.meta.get("playwright_page")
        if page is None:
            self.logger.warning("No playwright_page found in meta; falling back to non-playwright parsing")
            for req in self._extract_document_requests(response):
                yield req
            return

        try:
         
            try:
                await page.wait_for_selector("form[action='/unblock'], li.search-result-document, .search-result", timeout=15000)
            except Exception:
                self.logger.debug("Timeout waiting for initial selectors; continuing to check presence.")

            unblock_form = await page.query_selector("form[action='/unblock']")
            if unblock_form:
                self.logger.info("Unblock / captcha form detected — attempting automated solve")

                if not self.TWO_CAPTCHA_KEY:
                    self.logger.error("No TWO_CAPTCHA_KEY available; cannot solve captcha automatically.")
                    html = await page.content()
                    with open("failed_captcha_page.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    await page.close()
                    return

                
                loop = asyncio.get_running_loop()
                try:
                    token = await loop.run_in_executor(
                        None,
                        solve_2captcha_direct,
                        self.TWO_CAPTCHA_KEY,
                        self.site_key,
                        response.url,
                        5.0,    
                        120     
                    )
                except Exception as e:
                    self.logger.error("Captcha solve failed: %s", e)
                    html = await page.content()
                    with open("failed_captcha_page.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    await page.close()
                    return

                if not token:
                    self.logger.error("2captcha returned empty token; saved page for debugging")
                    html = await page.content()
                    with open("failed_captcha_page.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    await page.close()
                    return

                self.logger.info("Got token from 2captcha (len=%d). Injecting into page...", len(token))

             
                try:
                    await page.evaluate(
                        """(token) => {
                            var ta = document.getElementById('g-recaptcha-response');
                            if (!ta) {
                                ta = document.createElement('textarea');
                                ta.id = 'g-recaptcha-response';
                                ta.name = 'g-recaptcha-response';
                                ta.style.display = 'none';
                                document.body.appendChild(ta);
                            }
                            ta.value = token;
                            ta.dispatchEvent(new Event('input', {bubbles:true}));
                            ta.dispatchEvent(new Event('change', {bubbles:true}));
                        }""",
                        token,
                    )
                except Exception as e:
                    self.logger.error("Injection into page failed: %s", e)
                    html = await page.content()
                    with open("failed_captcha_page.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    await page.close()
                    return

             
                try:
                    await page.click("form[action='/unblock'] button[type='submit']")
                except Exception:
                    try:
                        await page.evaluate("document.querySelector(\"form[action='/unblock']\").submit();")
                    except Exception as e:
                        self.logger.error("Form submit failed: %s", e)

               
                try:
                    await page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    self.logger.debug("Timeout waiting for networkidle after submit (non-fatal).")

                try:
                    state_path = "playwright_state.json"
                    await page.context.storage_state(path=state_path)
                    self.logger.info("Saved Playwright storage_state to %s", state_path)
                except Exception as e:
                    self.logger.debug("Saving storage_state failed: %s", e)

            else:
                self.logger.info("No unblock form detected; page likely accessible.")

            rendered_html = await page.content()
            try:
                await page.close()
            except Exception:
                pass

            rendered_response = response.replace(body=rendered_html.encode("utf-8"))
            for req in self._extract_document_requests(rendered_response):
                yield req

        finally:
          
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass

    def _extract_document_requests(self, response):
      
        public_documents = response.css("li.search-result-document, li.search-result, .search-result-document, .search-result")
        self.logger.info("Found %d candidate document entries", len(public_documents))
        for document in public_documents:
            source = (
                document.css("h5 a::attr(href)").get()
                or document.css("a::attr(href)").get()
                or document.xpath(".//a[contains(@href, '/documents')]/@href").get()
            )
            if source:
                full = response.urljoin(source)
                yield scrapy.Request(
                    url=full,
                    callback=self.parse_document,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                )

  
    async def parse_document(self, response):
        page = response.meta.get("playwright_page")
        if page:
            try:
                await page.wait_for_selector("div#metadata_content_area, h1", timeout=8000)
            except Exception:
                pass
            html = await page.content()
            try:
                await page.close()
            except Exception:
                pass
            rendered = response.replace(body=html.encode("utf-8"))
        else:
            rendered = response

        title = (
            rendered.css("div#metadata_content_area h1::text").get()
            or rendered.css("h1.large-title::text").get()
            or rendered.xpath("//h1/text()").get()
        )
        title = title.strip() if title else None

        pdf_document = (
            rendered.css("a[href$='.pdf']::attr(href)").get()
            or rendered.css("li#utility-nav-pdf a::attr(href)").get()
            or rendered.xpath("//a[contains(translate(@href, 'PDF', 'pdf'), '.pdf')]/@href").get()
        )
        if pdf_document:
            pdf_document = rendered.urljoin(pdf_document)

        yield {
            "title": title,
            "pdf_document": pdf_document,
            "url": rendered.url,
        }
