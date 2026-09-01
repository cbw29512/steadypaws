"""Browser regression for Steady Paws local name/photo PDF personalization."""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://127.0.0.1:4173/"


def make_test_photo(path: Path) -> None:
    image = Image.new("RGB", (640, 480), "#d9e7e2")
    draw = ImageDraw.Draw(image)
    draw.ellipse((185, 105, 455, 375), fill="#55756c")
    draw.ellipse((235, 155, 285, 205), fill="#fffdf9")
    draw.ellipse((355, 155, 405, 205), fill="#fffdf9")
    image.save(path, format="JPEG", quality=90)


def page_has_image(reader: PdfReader) -> bool:
    page = reader.pages[0]
    resources = page.get("/Resources")
    if not resources:
        return False
    resources = resources.get_object()
    xobjects = resources.get("/XObject")
    if not xobjects:
        return False
    for value in xobjects.get_object().values():
        candidate = value.get_object()
        if candidate.get("/Subtype") == "/Image":
            return True
    return False


def wait_for_download(directory: Path, timeout: float = 20.0) -> Path:
    deadline = time.time() + timeout
    while time.time() < deadline:
        candidates = [
            item for item in directory.glob("*.pdf")
            if not item.name.endswith(".crdownload") and item.stat().st_size > 1000
        ]
        if candidates:
            return max(candidates, key=lambda item: item.stat().st_mtime)
        time.sleep(0.25)
    raise AssertionError("Personalized PDF did not download")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="steadypaws-browser-") as temp:
        root = Path(temp)
        downloads = root / "downloads"
        downloads.mkdir()
        photo = root / "family-photo.jpg"
        make_test_photo(photo)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1440,1200")
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(downloads),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
            },
        )

        chromedriver = shutil.which("chromedriver")
        service = Service(executable_path=chromedriver) if chromedriver else Service()
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        try:
            driver.execute_cdp_cmd(
                "Page.setDownloadBehavior",
                {"behavior": "allow", "downloadPath": str(downloads)},
            )
            driver.get(BASE_URL)

            wait.until(lambda d: d.execute_script(
                "const logo=document.querySelector('.brand-logo'); return !!logo && logo.complete && logo.naturalWidth > 0;"
            ))

            cat = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-family-group="cat"]')))
            cat.click()
            personalize = wait.until(EC.visibility_of_element_located((By.ID, "personalize")))
            assert personalize.is_displayed(), "Personalization panel did not open"

            name = driver.find_element(By.ID, "family-name")
            name.send_keys("Milo")

            photo_input = driver.find_element(By.ID, "family-photo")
            assert photo_input.is_displayed(), "Photo file input is not visibly usable"
            photo_input.send_keys(str(photo))

            wait.until(lambda d: "Photo ready" in d.find_element(By.ID, "personalize-status").text)
            preview = driver.find_element(By.ID, "photo-preview")
            wait.until(lambda d: preview.is_displayed() and d.execute_script("return arguments[0].naturalWidth", preview) > 0)

            download_link = wait.until(lambda d: next(
                (element for element in d.find_elements(By.CSS_SELECTOR, ".care-download") if element.is_displayed()),
                None,
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", download_link)
            wait.until(lambda d: "Personalize" in download_link.text)
            download_link.click()

            wait.until(lambda d: "Personalized PDF ready" in d.find_element(By.ID, "personalize-status").text)
            downloaded = wait_for_download(downloads)
            assert downloaded.name.startswith("milo-"), f"Unexpected personalized filename: {downloaded.name}"

            reader = PdfReader(str(downloaded))
            text = reader.pages[0].extract_text() or ""
            assert "Milo" in text, "Personalized name was not embedded into the PDF"
            assert page_has_image(reader), "Personalized photo image was not embedded into the PDF"
            print(f"Personalization browser test PASS: {downloaded.name}")
            return 0
        finally:
            driver.quit()


if __name__ == "__main__":
    raise SystemExit(main())
