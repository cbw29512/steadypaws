(() => {
  'use strict';

  const STORAGE_KEY = 'steadypaws.personalization.v1';
  const PDF_LIB_URL = '/assets/vendor/pdf-lib-1.17.1.min.js?v=1.17.1';
  const PHOTO_IMAGE_BOX = { x: 490, y: 607, width: 82, height: 82 };
  const NAME_POSITION = { x: 96, y: 666, maxWidth: 190 };
  let pdfLibPromise = null;
  let preparingDownload = false;

  function readPersonalization() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return { name: '', photoDataUrl: '' };
      const parsed = JSON.parse(raw);
      return {
        name: typeof parsed.name === 'string' ? parsed.name.trim().slice(0, 48) : '',
        photoDataUrl: typeof parsed.photoDataUrl === 'string' && parsed.photoDataUrl.startsWith('data:image/jpeg;base64,')
          ? parsed.photoDataUrl
          : '',
      };
    } catch (error) {
      console.warn('Steady Paws could not read personalization from this tab:', error);
      return { name: '', photoDataUrl: '' };
    }
  }

  function dataUrlToBytes(dataUrl) {
    const base64 = dataUrl.split(',')[1] || '';
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    return bytes;
  }

  function safeDownloadName(filename, name) {
    const cleanName = name
      .normalize('NFKD')
      .replace(/[^a-zA-Z0-9 _-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
      .toLowerCase()
      .slice(0, 32);
    return cleanName ? `${cleanName}-${filename}` : filename;
  }

  function loadPdfLib() {
    if (window.PDFLib) return Promise.resolve(window.PDFLib);
    if (pdfLibPromise) return pdfLibPromise;
    pdfLibPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = PDF_LIB_URL;
      script.async = true;
      script.onload = () => window.PDFLib
        ? resolve(window.PDFLib)
        : reject(new Error('The personalization helper could not start.'));
      script.onerror = () => reject(new Error('The personalization helper could not be loaded.'));
      document.head.appendChild(script);
    });
    return pdfLibPromise;
  }

  function addPhotoToWorksheet(identityGrid, photoDataUrl, name) {
    if (!photoDataUrl) return null;
    const block = document.createElement('div');
    block.className = 'care-personalized-photo';
    block.setAttribute('aria-label', name ? `Photo of ${name}` : 'Family member photo');

    const image = document.createElement('img');
    image.id = 'care-family-photo';
    image.src = photoDataUrl;
    image.alt = name ? `Photo of ${name}` : 'Family member photo';
    block.appendChild(image);

    const note = document.createElement('span');
    note.textContent = 'Their photo';
    block.appendChild(note);
    identityGrid.prepend(block);
    return image;
  }

  async function downloadPersonalizedPdf(link, personalization) {
    const pdfLib = await loadPdfLib();
    const { PDFDocument, StandardFonts, rgb } = pdfLib;
    const response = await fetch(link.getAttribute('href'), { cache: 'no-store' });
    if (!response.ok) throw new Error('The printable PDF could not be opened.');

    const pdfDoc = await PDFDocument.load(await response.arrayBuffer());
    const page = pdfDoc.getPage(0);

    if (personalization.photoDataUrl) {
      const photo = await pdfDoc.embedJpg(dataUrlToBytes(personalization.photoDataUrl));
      page.drawRectangle({
        x: PHOTO_IMAGE_BOX.x - 2,
        y: PHOTO_IMAGE_BOX.y - 2,
        width: PHOTO_IMAGE_BOX.width + 4,
        height: PHOTO_IMAGE_BOX.height + 4,
        color: rgb(1, 0.992, 0.976),
      });
      page.drawImage(photo, PHOTO_IMAGE_BOX);
    }

    if (personalization.name) {
      const font = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      let size = 10;
      while (size > 7 && font.widthOfTextAtSize(personalization.name, size) > NAME_POSITION.maxWidth) size -= 0.5;
      page.drawText(personalization.name, {
        x: NAME_POSITION.x,
        y: NAME_POSITION.y,
        size,
        font,
        color: rgb(0.208, 0.282, 0.259),
      });
    }

    const bytes = await pdfDoc.save();
    const blob = new Blob([bytes], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const temp = document.createElement('a');
    const filename = (link.getAttribute('href') || '').split('/').pop() || 'steady-paws-care-paperwork.pdf';
    temp.href = url;
    temp.download = safeDownloadName(filename, personalization.name);
    document.body.appendChild(temp);
    temp.click();
    temp.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 3000);
  }

  const personalization = readPersonalization();
  const identityGrid = document.querySelector('.identity-grid');
  const actions = document.querySelector('.care-actions');
  const pdfLink = actions?.querySelector('a.button[href$=".pdf"]');
  const printButton = document.querySelector('#care-print-personalized');
  const status = document.querySelector('#care-personalization-status');
  const nameInput = document.querySelector('#care-family-name');
  if (!identityGrid || !actions || !pdfLink || !printButton || !status || !nameInput) return;

  printButton.addEventListener('click', () => window.print());
  if (personalization.name) nameInput.value = personalization.name;
  const photoImage = addPhotoToWorksheet(identityGrid, personalization.photoDataUrl, personalization.name);

  if (personalization.name || personalization.photoDataUrl) {
    pdfLink.textContent = 'Download personalized PDF';
    status.textContent = 'Personalization carried over from the previous page and stays in this browser tab. It will be included when you print this worksheet or download the PDF.';
    pdfLink.addEventListener('click', async event => {
      if (preparingDownload) {
        event.preventDefault();
        return;
      }
      event.preventDefault();
      preparingDownload = true;
      const original = pdfLink.textContent;
      pdfLink.textContent = 'Preparing personalized PDF...';
      try {
        await downloadPersonalizedPdf(pdfLink, personalization);
        status.textContent = 'Personalized PDF ready ✓ Their name and photo were added on this device.';
      } catch (error) {
        console.error('Steady Paws care-page personalization failed:', error);
        status.textContent = 'The personalized PDF could not be prepared. The web worksheet can still be printed with the photo shown here.';
      } finally {
        preparingDownload = false;
        pdfLink.textContent = original;
      }
    });
  }

  if (photoImage) {
    photoImage.addEventListener('load', () => document.documentElement.dataset.personalizedPhotoReady = 'true', { once: true });
    if (photoImage.complete && photoImage.naturalWidth > 0) document.documentElement.dataset.personalizedPhotoReady = 'true';
  }
})();
