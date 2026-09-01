(() => {
  'use strict';

  const chips = [...document.querySelectorAll('[data-filter]')];
  const familyChoices = [...document.querySelectorAll('.family-choice')];
  const moreButton = document.querySelector('.family-more');
  const moreFamily = document.querySelector('#more-family');
  const cards = [...document.querySelectorAll('.condition-card')];
  const search = document.querySelector('#tracker-search');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#no-results');
  const journeyHeading = document.querySelector('#journey-heading');
  const journeyCopy = document.querySelector('#journey-copy');
  const library = document.querySelector('#library');
  const personalize = document.querySelector('#personalize');
  const familyName = document.querySelector('#family-name');
  const familyPhoto = document.querySelector('#family-photo');
  const photoPreview = document.querySelector('#photo-preview');
  const photoPlaceholder = document.querySelector('#photo-placeholder');
  const photoRemove = document.querySelector('#photo-remove');
  const personalizeStatus = document.querySelector('#personalize-status');
  const careDownloads = [...document.querySelectorAll('.care-download')];
  if (!chips.length || !cards.length || !search || !count || !empty) return;

  let activeGroup = 'all';
  let familyTerms = [];
  let familyLabel = '';
  let journeyStarted = false;
  let photoJpegBytes = null;
  let photoDataUrl = '';
  let preparingDownload = false;
  const normalize = value => value.trim().toLowerCase();

  // Must match scripts/build_trackers.py.
  const PHOTO_IMAGE_BOX = { x: 490, y: 607, width: 82, height: 82 };
  const NAME_POSITION = { x: 96, y: 666, maxWidth: 190 };

  function cardText(card) {
    return `${card.dataset.search || ''} ${card.textContent}`.toLowerCase();
  }

  function variantText(variant) {
    return `${variant.dataset.species || ''} ${variant.dataset.search || ''} ${variant.textContent}`.toLowerCase();
  }

  function variantFitsFamily(variant) {
    const group = variant.dataset.group || '';
    const groupMatch = activeGroup === 'all' || group === activeGroup;
    if (!groupMatch) return false;
    if (!familyTerms.length) return true;
    const text = variantText(variant);
    return familyTerms.some(term => text.includes(term));
  }

  function hasPersonalization() {
    return Boolean((familyName?.value || '').trim() || photoJpegBytes);
  }

  function updateDownloadLabels() {
    const label = hasPersonalization()
      ? 'Personalize & get their care paperwork <span aria-hidden="true">↓</span>'
      : 'Get their care paperwork <span aria-hidden="true">↓</span>';
    careDownloads.forEach(link => {
      if (!link.dataset.busy) link.innerHTML = label;
    });
  }

  function applyFilters() {
    try {
      const query = normalize(search.value);
      const browsing = journeyStarted || Boolean(query) || activeGroup !== 'all';
      let visible = 0;

      cards.forEach(card => {
        const variants = [...card.querySelectorAll('.tracker-variant')];
        const queryMatchesCard = !query || cardText(card).includes(query);
        let visibleVariants = 0;

        variants.forEach(variant => {
          const searchMatch = !query || queryMatchesCard || variantText(variant).includes(query);
          const showVariant = browsing && variantFitsFamily(variant) && searchMatch;
          variant.hidden = !showVariant;
          if (showVariant) visibleVariants += 1;
        });

        const showCard = browsing && visibleVariants > 0;
        card.hidden = !showCard;
        card.classList.toggle('has-multiple-variants', visibleVariants > 1);
        if (showCard) visible += 1;
      });

      if (!browsing) {
        count.textContent = 'Pick your family member above to see their primary health concerns.';
        empty.hidden = true;
        return;
      }

      count.textContent = visible === 1
        ? '1 primary health concern ready to choose'
        : `${visible} primary health concerns ready to choose`;
      empty.hidden = visible !== 0;
    } catch (error) {
      console.error('Steady Paws health-concern filtering failed:', error);
    }
  }

  function setActiveChip(group) {
    chips.forEach(item => {
      const selected = (item.dataset.filter || 'all') === group;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
  }

  function clearFamilySelection() {
    familyChoices.forEach(item => {
      item.classList.remove('is-selected');
      item.setAttribute('aria-pressed', 'false');
    });
  }

  function showPersonalization() {
    if (!personalize) return;
    personalize.hidden = false;
  }

  function selectFamily(choice) {
    try {
      activeGroup = choice.dataset.familyGroup || 'all';
      familyLabel = choice.dataset.familyLabel || 'family member';
      familyTerms = normalize(choice.dataset.familyTerm || '')
        .split(/\s*\|\s*/)
        .filter(Boolean);
      journeyStarted = true;
      search.value = '';

      clearFamilySelection();
      choice.classList.add('is-selected');
      choice.setAttribute('aria-pressed', 'true');
      setActiveChip(activeGroup);
      showPersonalization();

      if (journeyHeading) journeyHeading.textContent = 'What is the biggest health concern right now?';
      if (journeyCopy) {
        journeyCopy.textContent = activeGroup === 'all'
          ? 'Each health concern appears once. Open the concern you need and choose the version made for your family member.'
          : `Choose the main health concern you want to track for your ${familyLabel}. Their form has room to note other conditions they are living with too.`;
      }

      applyFilters();
      if (library) {
        const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        library.scrollIntoView({ behavior, block: 'start' });
      }
    } catch (error) {
      console.error('Steady Paws family picker failed:', error);
    }
  }

  function dataUrlToBytes(dataUrl) {
    const base64 = dataUrl.split(',')[1] || '';
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    return bytes;
  }

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error('That picture could not be opened.'));
      image.src = src;
    });
  }

  async function makeSquareJpeg(file) {
    if (!file.type.startsWith('image/')) throw new Error('Please choose a picture file.');
    if (file.size > 25 * 1024 * 1024) throw new Error('Please choose a picture smaller than 25 MB.');

    const objectUrl = URL.createObjectURL(file);
    try {
      const image = await loadImage(objectUrl);
      const size = Math.min(image.naturalWidth, image.naturalHeight);
      const sourceX = (image.naturalWidth - size) / 2;
      const sourceY = (image.naturalHeight - size) / 2;
      const canvas = document.createElement('canvas');
      canvas.width = 600;
      canvas.height = 600;
      const context = canvas.getContext('2d', { alpha: false });
      if (!context) throw new Error('This browser could not prepare the picture.');
      context.fillStyle = '#fffdf9';
      context.fillRect(0, 0, 600, 600);
      context.drawImage(image, sourceX, sourceY, size, size, 0, 0, 600, 600);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.88);
      return { dataUrl, bytes: dataUrlToBytes(dataUrl) };
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  function setPersonalizeStatus(message, isError = false) {
    if (!personalizeStatus) return;
    personalizeStatus.textContent = message;
    personalizeStatus.dataset.state = isError ? 'error' : 'ok';
  }

  function clearPhoto() {
    photoJpegBytes = null;
    photoDataUrl = '';
    if (familyPhoto) familyPhoto.value = '';
    if (photoPreview) {
      photoPreview.src = '';
      photoPreview.hidden = true;
    }
    if (photoPlaceholder) photoPlaceholder.hidden = false;
    if (photoRemove) photoRemove.hidden = true;
    setPersonalizeStatus('Private by design: their name and photo stay in this browser and are added to the PDF on this device. Steady Paws does not upload them.');
    updateDownloadLabels();
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

  async function personalizePdf(link) {
    const name = (familyName?.value || '').trim();
    if (!name && !photoJpegBytes) return false;
    if (!window.PDFLib) throw new Error('The personalization helper did not load. Please try again or download the plain form.');

    const { PDFDocument, StandardFonts, rgb } = window.PDFLib;
    const sourceUrl = link.dataset.pdfUrl || link.getAttribute('href');
    const response = await fetch(sourceUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error('The care form could not be opened for personalization.');

    const pdfDoc = await PDFDocument.load(await response.arrayBuffer());
    const page = pdfDoc.getPage(0);

    if (photoJpegBytes) {
      const photo = await pdfDoc.embedJpg(photoJpegBytes);
      page.drawRectangle({
        x: PHOTO_IMAGE_BOX.x - 2,
        y: PHOTO_IMAGE_BOX.y - 2,
        width: PHOTO_IMAGE_BOX.width + 4,
        height: PHOTO_IMAGE_BOX.height + 4,
        color: rgb(1, 0.992, 0.976),
      });
      page.drawImage(photo, PHOTO_IMAGE_BOX);
    }

    if (name) {
      const font = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      let size = 10;
      while (size > 7 && font.widthOfTextAtSize(name, size) > NAME_POSITION.maxWidth) size -= 0.5;
      page.drawText(name, {
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
    const download = document.createElement('a');
    download.href = url;
    download.download = safeDownloadName(link.dataset.downloadName || 'steady-paws-care-paperwork.pdf', name);
    document.body.appendChild(download);
    download.click();
    download.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    return true;
  }

  familyChoices.forEach(choice => {
    choice.setAttribute('aria-pressed', 'false');
    choice.addEventListener('click', () => selectFamily(choice));
  });

  if (moreButton && moreFamily) {
    moreButton.addEventListener('click', () => {
      const opening = moreFamily.hidden;
      moreFamily.hidden = !opening;
      moreButton.setAttribute('aria-expanded', String(opening));
      moreButton.classList.toggle('is-open', opening);
      if (opening) moreFamily.querySelector('.family-choice')?.focus();
    });
  }

  chips.forEach(chip => chip.addEventListener('click', () => {
    activeGroup = chip.dataset.filter || 'all';
    familyLabel = '';
    familyTerms = [];
    journeyStarted = true;
    clearFamilySelection();
    setActiveChip(activeGroup);
    if (journeyHeading) journeyHeading.textContent = 'Browse primary health concerns';
    if (journeyCopy) journeyCopy.textContent = 'Each concern is listed once. When several tailored forms exist, choose the one made for your family member.';
    applyFilters();
  }));

  search.addEventListener('input', () => {
    if (normalize(search.value)) journeyStarted = true;
    applyFilters();
  });

  familyName?.addEventListener('input', updateDownloadLabels);

  familyPhoto?.addEventListener('change', async () => {
    const file = familyPhoto.files?.[0];
    if (!file) return;
    setPersonalizeStatus('Preparing their photo on this device...');
    try {
      const prepared = await makeSquareJpeg(file);
      photoJpegBytes = prepared.bytes;
      photoDataUrl = prepared.dataUrl;
      if (photoPreview) {
        photoPreview.src = photoDataUrl;
        photoPreview.hidden = false;
      }
      if (photoPlaceholder) photoPlaceholder.hidden = true;
      if (photoRemove) photoRemove.hidden = false;
      setPersonalizeStatus('Their photo is ready. It has not been uploaded anywhere.');
      updateDownloadLabels();
    } catch (error) {
      clearPhoto();
      setPersonalizeStatus(error instanceof Error ? error.message : 'That picture could not be prepared.', true);
    }
  });

  photoRemove?.addEventListener('click', clearPhoto);

  careDownloads.forEach(link => link.addEventListener('click', async event => {
    if (!hasPersonalization() || preparingDownload) return;
    event.preventDefault();
    preparingDownload = true;
    const original = link.innerHTML;
    link.dataset.busy = 'true';
    link.textContent = 'Preparing their PDF...';
    setPersonalizeStatus('Adding their name and photo to this copy on your device...');
    try {
      await personalizePdf(link);
      setPersonalizeStatus('Their personalized care paperwork is ready. Nothing was uploaded or stored by Steady Paws.');
    } catch (error) {
      console.error('Steady Paws PDF personalization failed:', error);
      setPersonalizeStatus(error instanceof Error ? error.message : 'Their PDF could not be personalized. The plain form is still available.', true);
    } finally {
      preparingDownload = false;
      delete link.dataset.busy;
      link.innerHTML = original;
      updateDownloadLabels();
    }
  }));

  applyFilters();
  updateDownloadLabels();
})();
