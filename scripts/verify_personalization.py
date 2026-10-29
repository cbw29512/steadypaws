"""Browser regression for Your Pet’s Health Log local name/photo PDF and print personalization."""

from __future__ import annotations

import base64
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


def page_has_large_image(reader: PdfReader, minimum: int = 300) -> bool:
    for page in reader.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        xobjects = resources.get_object().get("/XObject")
        if not xobjects:
            continue
        for value in xobjects.get_object().values():
            candidate = value.get_object()
            if candidate.get("/Subtype") != "/Image":
                continue
            width = int(candidate.get("/Width", 0))
            height = int(candidate.get("/Height", 0))
            if width >= minimum and height >= minimum:
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


def scroll_and_click(driver: webdriver.Chrome, wait: WebDriverWait, by: str, value: str):
    """Perform a user-like click even when a long page initially places the control below the viewport."""
    element = wait.until(EC.presence_of_element_located((by, value)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'nearest'});", element)
    wait.until(lambda d: element.is_displayed() and element.is_enabled())
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)
    return element


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="steadypaws-browser-") as temp:
        root = Path(temp)
        downloads = root / "downloads"
        downloads.mkdir()
        photo = root / "family-photo.jpg"
        printed = root / "accessible-print.pdf"
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

            # Initial page must show every animal choice and both usable dropdowns.
            assert driver.find_element(By.ID, "choose-pet-prompt").is_displayed(), (
                "Animal-first prompt is missing on initial load"
            )
            assert not any(
                card.is_displayed()
                for card in driver.find_elements(By.CSS_SELECTOR, ".condition-card")
            ), "Trackers appear before an animal is chosen"
            assert driver.find_element(By.ID, "more-family").is_displayed(), (
                "Animal choices are hidden instead of visible"
            )
            animal_dropdown = driver.find_element(By.ID, "animal-select")
            condition_dropdown = driver.find_element(By.ID, "condition-select")
            assert animal_dropdown.is_displayed() and animal_dropdown.is_enabled(), (
                "Animal dropdown is missing or disabled"
            )
            assert condition_dropdown.is_displayed() and condition_dropdown.is_enabled(), (
                "Health-issue dropdown looks greyed out before animal selection"
            )
            # The dropdown and the visible animal cards must both work.
            driver.execute_script(
                "arguments[0].value='dog';"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                animal_dropdown,
            )
            wait.until(lambda d: any(
                card.is_displayed() and card.get_attribute("data-group") == "dog"
                for card in d.find_elements(By.CSS_SELECTOR, ".condition-card")
            ))
            scroll_and_click(driver, wait, By.CSS_SELECTOR, '[data-family-group="cat"]')
            assert animal_dropdown.get_attribute("value") == "cat", (
                "Animal buttons and animal dropdown are not synchronized"
            )
            selected_cards = wait.until(lambda d: [
                card for card in d.find_elements(By.CSS_SELECTOR, ".condition-card")
                if card.is_displayed()
            ])
            assert all(
                card.get_attribute("data-group") in ("cat", "universal")
                for card in selected_cards
            ), "Cat filter included another animal"
            assert all(
                len(card.find_elements(By.CSS_SELECTOR, ".tracker-variant")) == 1
                for card in selected_cards
            ), "Health issue card still stacks multiple animal forms"

            issue_filter = driver.find_element(By.ID, "condition-select")
            assert issue_filter.is_enabled(), "Health issue filter was not enabled"
            options = [
                option for option in issue_filter.find_elements(By.TAG_NAME, "option")
                if option.get_attribute("value")
            ]
            assert options, "Cat selection exposes no health issue choices"
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                issue_filter, options[0].get_attribute("value"),
            )
            narrowed = [
                card for card in driver.find_elements(By.CSS_SELECTOR, ".condition-card")
                if card.is_displayed()
            ]
            assert narrowed and all(
                card.get_attribute("data-condition") == options[0].get_attribute("value")
                for card in narrowed
            ), "Selected health issue is not narrowing results"

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
            variant = download_link.find_element(By.XPATH, "./ancestor::div[contains(@class,'tracker-variant')]")
            accessible_link = variant.find_element(By.CSS_SELECTOR, ".accessible-link")

            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'nearest'});", download_link)
            wait.until(lambda d: download_link.is_displayed() and download_link.is_enabled() and "personalized" in download_link.text.lower())
            try:
                download_link.click()
            except Exception:
                driver.execute_script("arguments[0].click();", download_link)

            wait.until(lambda d: "Personalized PDF ready" in d.find_element(By.ID, "personalize-status").text)
            downloaded = wait_for_download(downloads)
            assert downloaded.name.startswith("milo-"), f"Unexpected personalized filename: {downloaded.name}"

            reader = PdfReader(str(downloaded))
            text = reader.pages[0].extract_text() or ""
            assert "Milo" in text, "Personalized name was not embedded into the PDF"
            assert page_has_image(reader), "Personalized photo image was not embedded into the PDF"
            downloaded.unlink()

            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'nearest'});", accessible_link)
            try:
                accessible_link.click()
            except Exception:
                driver.execute_script("arguments[0].click();", accessible_link)

            wait.until(EC.url_contains("/care/"))
            care_name = wait.until(EC.presence_of_element_located((By.ID, "care-family-name")))
            assert care_name.get_attribute("value") == "Milo", "Name did not carry into the accessible worksheet"
            care_photo = wait.until(EC.visibility_of_element_located((By.ID, "care-family-photo")))
            wait.until(lambda d: d.execute_script("return arguments[0].naturalWidth", care_photo) > 0)

            result = driver.execute_cdp_cmd(
                "Page.printToPDF",
                {"printBackground": True, "preferCSSPageSize": True},
            )
            printed.write_bytes(base64.b64decode(result["data"]))
            print_reader = PdfReader(str(printed))
            assert page_has_large_image(print_reader), "Uploaded photo was not rendered into the browser-printed worksheet"

            care_download = driver.find_element(By.CSS_SELECTOR, '.care-actions a.button[href$=".pdf"]')
            assert "personalized" in care_download.text.lower(), "Care-page PDF action did not recognize personalization"
            try:
                care_download.click()
            except Exception:
                driver.execute_script("arguments[0].click();", care_download)
            wait.until(lambda d: "Personalized PDF ready" in d.find_element(By.ID, "care-personalization-status").text)
            second_download = wait_for_download(downloads)
            second_reader = PdfReader(str(second_download))
            second_text = second_reader.pages[0].extract_text() or ""
            assert "Milo" in second_text, "Care-page PDF download lost the personalized name"
            assert page_has_image(second_reader), "Care-page PDF download lost the personalized photo"

            print(
                "Personalization browser test PASS: homepage PDF + accessible worksheet print + care-page PDF all retain photo/name"
            )
            return 0
        finally:
            driver.quit()


if __name__ == "__main__":
    raise SystemExit(main())
