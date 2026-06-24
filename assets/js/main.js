/* === Minglu Lighting — Main JS === */
/* global PRODUCTS, CATEGORIES */

const WHATSAPP_NUMBER = '8618098910947';
const WHATSAPP_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M17.47 14.64c-.27-.13-1.62-.8-1.87-.89-.25-.09-.43-.13-.62.13-.19.27-.75.89-.92 1.07-.17.18-.34.2-.62.07-.27-.13-1.15-.42-2.19-1.35-.81-.73-1.36-1.63-1.52-1.9-.17-.27 0-.42.13-.55.13-.13.27-.34.41-.52.13-.17.17-.27.27-.47.09-.2.04-.37 0-.5-.04-.13-.62-1.5-.85-2.06-.22-.54-.45-.47-.62-.48h-.52c-.17 0-.47.07-.7.37-.24.3-.92.9-.92 2.2s.94 2.56 1.07 2.73c.13.17 1.88 2.87 4.57 3.88.64.27 1.13.43 1.52.55.64.2 1.22.17 1.68.1.52-.08 1.62-.66 1.85-1.3.23-.63.23-1.17.16-1.3-.07-.13-.25-.2-.52-.33zM12.02 21.47c-1.14 0-2.27-.17-3.34-.5l-.24-.09-2.49.65.67-2.43-.16-.25A9.18 9.18 0 012.7 12.02C2.7 6.98 6.83 3 12.02 3c2.42 0 4.7.94 6.4 2.64a8.98 8.98 0 012.6 6.38c0 5.2-4.13 9.45-9 9.45z"/></svg>';

/* ===== Product Gallery State ===== */
let currentGalleryIndex = 0;
let galleryImages = [];

/* ===== Header scroll effect ===== */
function initHeaderScroll() {
    const header = document.getElementById('header');
    if (!header) return;
    window.addEventListener('scroll', () => {
        header.classList.toggle('scrolled', window.scrollY > 30);
    });
}

/* ===== Hero Carousel ===== */
let heroSlideIndex = 0;
let heroSlideTimer = null;

function initHeroCarousel() {
    const slides = document.querySelectorAll('#heroCarousel .hero-product-img');
    const dots = document.querySelectorAll('#heroCarouselDots .dot');
    if (!slides.length) return;
    heroSlideTimer = setInterval(() => {
        heroSlideIndex = (heroSlideIndex + 1) % slides.length;
        updateHeroSlide(slides, dots);
    }, 4000);
}

function setHeroSlide(n) {
    const slides = document.querySelectorAll('#heroCarousel .hero-product-img');
    const dots = document.querySelectorAll('#heroCarouselDots .dot');
    heroSlideIndex = n;
    updateHeroSlide(slides, dots);
    clearInterval(heroSlideTimer);
    heroSlideTimer = setInterval(() => {
        heroSlideIndex = (heroSlideIndex + 1) % slides.length;
        updateHeroSlide(slides, dots);
    }, 4000);
}

function updateHeroSlide(slides, dots) {
    slides.forEach((s, i) => s.classList.toggle('active', i === heroSlideIndex));
    dots.forEach((d, i) => d.classList.toggle('active', i === heroSlideIndex));
}

function heroSlidePrev() {
    const slides = document.querySelectorAll('#heroCarousel .hero-product-img');
    const dots = document.querySelectorAll('#heroCarouselDots .dot');
    heroSlideIndex = (heroSlideIndex - 1 + slides.length) % slides.length;
    updateHeroSlide(slides, dots);
    clearInterval(heroSlideTimer);
    heroSlideTimer = setInterval(() => {
        heroSlideIndex = (heroSlideIndex + 1) % slides.length;
        updateHeroSlide(slides, dots);
    }, 4000);
}

function heroSlideNext() {
    const slides = document.querySelectorAll('#heroCarousel .hero-product-img');
    const dots = document.querySelectorAll('#heroCarouselDots .dot');
    heroSlideIndex = (heroSlideIndex + 1) % slides.length;
    updateHeroSlide(slides, dots);
    clearInterval(heroSlideTimer);
    heroSlideTimer = setInterval(() => {
        heroSlideIndex = (heroSlideIndex + 1) % slides.length;
        updateHeroSlide(slides, dots);
    }, 4000);
}

/* ===== Mobile menu ===== */
function initMobileMenu() {
    const btn = document.getElementById('mobileMenuBtn');
    const nav = document.getElementById('mainNav');
    if (!btn || !nav) return;
    btn.addEventListener('click', () => {
        nav.classList.toggle('open');
        btn.classList.toggle('active');
    });
}

/* ===== Build category dropdown ===== */
function buildCategoryDropdown() {
    const dd = document.getElementById('productsDropdown');
    if (!dd || typeof CATEGORIES === 'undefined') return;
    const base = window.location.pathname.includes('/product/') || window.location.pathname.includes('/blog/') ? '../' : '';
    dd.innerHTML = CATEGORIES.map(c =>
        `<a href="${base}category/${c.slug}.html">${c.name}</a>`
    ).join('');
}

/* ===== Build category cards (homepage) ===== */
function buildCategoryCards() {
    const grid = document.getElementById('categoriesGrid');
    if (!grid || typeof CATEGORIES === 'undefined' || typeof PRODUCTS === 'undefined') return;

    // Find a representative product image for each category
    function getCategoryImage(slug) {
        const product = PRODUCTS.find(p => p.categorySlug === slug && p.image && !p.image.includes('placeholder'));
        if (product) return product.image;
        // Fallback: any product with that category
        const anyProduct = PRODUCTS.find(p => p.categorySlug === slug);
        return anyProduct ? anyProduct.image : '';
    }

    grid.innerHTML = CATEGORIES.map(c => {
        const img = getCategoryImage(c.slug);
        return `
        <a href="category/${c.slug}.html" class="category-card">
            <div class="category-img">
                ${img ? `<img src="${img}" alt="${c.name}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'category-icon\\'>💡</div>'">` : `<div class="category-icon">💡</div>`}
            </div>
            <div class="category-title-bar">
                <h3>${c.name}</h3>
            </div>
        </a>`;
    }).join('');
}

/* ===== Build product card HTML ===== */
function buildProductCard(p) {
    return `
        <div class="product-card fade-in-up">
            <a href="product/${p.id}.html" class="product-card-img" target="_blank">
                <img src="${p.image || 'assets/images/placeholder.svg'}" alt="${p.name}" loading="lazy"
                     onerror="this.onerror=null;this.src='assets/images/placeholder.svg'">
                <div class="product-card-badge">${p.category}</div>
                ${p.description ? `<div class="product-card-overlay"><p>${p.description}</p></div>` : ''}
            </a>
            <div class="product-card-body">
                <h3><a href="product/${p.id}.html" class="product-card-title" target="_blank">${p.shortName || p.name}</a></h3>
                <div class="product-card-actions">
                    <a href="https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent('Hi Minglu Lighting, I have a project and need a quote for: ' + p.name)}" class="btn-whatsapp" target="_blank">
                        ${WHATSAPP_ICON}
                        WhatsApp
                    </a>
                </div>
            </div>
        </div>`;
}

/* ===== Render featured products on homepage ===== */
function renderFeaturedProducts() {
    const grid = document.getElementById('featuredProducts');
    if (!grid || typeof PRODUCTS === 'undefined') return;
    const featured = PRODUCTS.filter(p => p.featured).slice(0, 9);
    grid.innerHTML = featured.map(p => buildProductCard(p)).join('');
}

/* ===== Product listing page ===== */
function initProductsPage() {
    const grid = document.getElementById('productsGrid');
    const filterBar = document.getElementById('filterBar');
    if (!grid) return;

    // Build filter buttons
    if (filterBar && typeof CATEGORIES !== 'undefined') {
        let buttons = '<button class="filter-btn active" data-category="all">All Products</button>';
        buttons += CATEGORIES.map(c =>
            `<button class="filter-btn" data-category="${c.slug}">${c.name}</button>`
        ).join('');
        filterBar.innerHTML = buttons;

        filterBar.addEventListener('click', (e) => {
            if (!e.target.classList.contains('filter-btn')) return;
            filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const cat = e.target.dataset.category;
            const url = new URL(window.location);
            url.searchParams.set('category', cat);
            history.replaceState(null, '', url);
            renderProductsGrid(cat);
        });
    }

    // Check URL param
    const params = new URLSearchParams(window.location.search);
    const catParam = params.get('category');
    if (catParam && filterBar) {
        const btn = filterBar.querySelector(`[data-category="${catParam}"]`);
        if (btn) {
            filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        renderProductsGrid(catParam);
    } else {
        renderProductsGrid('all');
    }
}

function renderProductsGrid(filter) {
    const grid = document.getElementById('productsGrid');
    if (!grid || typeof PRODUCTS === 'undefined') return;
    const filtered = filter === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.categorySlug === filter);
    grid.innerHTML = filtered.map(p => buildProductCard(p)).join('');
    if (filtered.length === 0) {
        grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:var(--gray-500);padding:60px 0;">No products found in this category.</p>';
    }
}

/* ===== Product detail page ===== */
function initProductDetailPage() {
    const container = document.getElementById('productDetail');
    if (!container || typeof PRODUCTS === 'undefined') return;

    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');

    // Static page mode: no ?id= param, content is pre-rendered
    // Just initialize galleryImages from DOM so carousel JS still works
    if (!id) {
        const mainImg = document.getElementById('productMainImg');
        if (mainImg && mainImg.src) {
            galleryImages = [mainImg.src.replace(window.location.origin + '/', '')];
        }
        document.querySelectorAll('.gallery-thumb img').forEach(img => {
            const src = img.src.replace(window.location.origin + '/', '').replace(/^\.\.\//, '');
            if (src && !galleryImages.includes(src)) galleryImages.push(src);
        });
        initGallerySwipe();
        return;
    }

    const p = PRODUCTS.find(x => x.id === id);
    if (!p) { container.innerHTML = '<p>Product not found.</p>'; return; }

    // Breadcrumb
    const breadcrumb = document.getElementById('breadcrumbProduct');
    if (breadcrumb) breadcrumb.textContent = p.name;

    // Build gallery images (main image + gallery images)
    galleryImages = [];
    if (p.image) galleryImages.push(p.image);
    if (p.galleryImages && p.galleryImages.length > 0) {
        p.galleryImages.forEach(img => {
            if (img) galleryImages.push(img);
        });
    }
    currentGalleryIndex = 0;

    // Main image
    const mainImg = document.getElementById('productMainImg');
    if (mainImg && galleryImages.length > 0) {
        mainImg.src = galleryImages[0];
        mainImg.alt = p.name;
        mainImg.onerror = () => { mainImg.src = 'assets/images/placeholder.svg'; };
    } else if (mainImg) {
        mainImg.src = p.image || 'assets/images/placeholder.svg';
        mainImg.alt = p.name;
        mainImg.onerror = () => { mainImg.src = 'assets/images/placeholder.svg'; };
    }

    // Thumbnails
    const thumbsContainer = document.getElementById('galleryThumbs');
    if (thumbsContainer && galleryImages.length > 1) {
        thumbsContainer.innerHTML = galleryImages.map((img, idx) => `
            <div class="gallery-thumb${idx === 0 ? ' active' : ''}" onclick="switchGalleryImage(${idx}, this)">
                <img src="${img}" alt="${p.name}" loading="lazy" onerror="this.parentElement.style.display='none'">
            </div>
        `).join('');
        thumbsContainer.style.display = 'flex';
    } else if (thumbsContainer) {
        thumbsContainer.style.display = 'none';
    }

    // Touch swipe support for mobile gallery
    initGallerySwipe();

    // Detail images section
    const detailSection = document.getElementById('detailImagesSection');
    const detailGrid = document.getElementById('detailImagesGrid');
    if (detailSection && detailGrid && p.detailImages && p.detailImages.length > 0) {
        // Filter out duplicate detail images
        const uniqueDetails = [...new Set(p.detailImages)];
        detailGrid.innerHTML = uniqueDetails.map(img =>
            `<img src="${img}" alt="${p.name} detail" loading="lazy" onerror="this.parentElement.removeChild(this)">`
        ).join('');
        detailSection.style.display = 'block';
    }

    // Product info
    const title = document.getElementById('productTitle');
    if (title) title.textContent = p.shortName || p.name;

    // Features
    const featuresList = document.getElementById('productFeatures');
    if (featuresList && p.features && p.features.length > 0) {
        featuresList.innerHTML = p.features.map(f => `<li>${f}</li>`).join('');
    }

    // Related products
    const relatedGrid = document.getElementById('relatedProducts');
    if (relatedGrid) {
        const related = PRODUCTS.filter(x => x.categorySlug === p.categorySlug && x.id !== p.id).slice(0, 3);
        relatedGrid.innerHTML = related.length > 0
            ? related.map(r => buildProductCard(r)).join('')
            : '<p style="color:var(--gray-500);">No related products found.</p>';
    }

    // Set page title
    document.title = `${p.name} — Minglu Lighting`;

    // WhatsApp button
    const whatsAppBtn = document.getElementById('productWhatsAppBtn');
    if (whatsAppBtn) {
        whatsAppBtn.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent('Hi Minglu Lighting, I have a project and need a quote for: ' + p.name)}`;
    }
}

/* ===== Projects page ===== */
function initProjectsPage() {
    const container = document.getElementById('projectsContent');
    if (!container || typeof PROJECTS === 'undefined') return;

    const groups = {};
    PROJECTS.forEach(p => {
        if (!groups[p.category]) groups[p.category] = [];
        groups[p.category].push(p);
    });

    // Build flat list for lightbox navigation
    window._projectImages = [];
    let globalIdx = 0;

    let html = '';
    for (const [category, projects] of Object.entries(groups)) {
        html += `<h2 class="project-category-title">${category} Projects</h2>`;
        html += '<div class="project-grid">';
        projects.forEach((p) => {
            html += `
                <div class="project-card fade-in-up">
                    <div class="project-card-img" onclick="openLightbox(${globalIdx})" style="cursor:pointer;">
                        <img src="${p.image}" alt="${p.name}" loading="lazy" onerror="this.onerror=null;this.src='assets/images/placeholder.svg'">
                    </div>
                    <div class="project-card-body">
                        <h3>${p.name}</h3>
                        <div class="project-country">${p.country}</div>
                    </div>
                </div>`;
            window._projectImages.push({ src: p.image, name: p.name });
            globalIdx++;
        });
        html += '</div>';
    }
    container.innerHTML = html;
}

/* ===== Lightbox ===== */
let currentLightboxIndex = 0;

function openLightbox(index) {
    currentLightboxIndex = index;
    showLightboxImage();
    const overlay = document.getElementById('lightboxOverlay');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function showLightboxImage() {
    const data = window._projectImages[currentLightboxIndex];
    if (!data) return;
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxCaption = document.getElementById('lightboxCaption');
    lightboxImg.src = data.src;
    lightboxImg.alt = data.name;
    if (lightboxCaption) lightboxCaption.textContent = data.name;
    // Update counter
    const counter = document.getElementById('lightboxCounter');
    if (counter) counter.textContent = `${currentLightboxIndex + 1} / ${window._projectImages.length}`;
}

function lightboxPrev(e) {
    e.stopPropagation();
    if (currentLightboxIndex > 0) {
        currentLightboxIndex--;
        showLightboxImage();
    }
}

function lightboxNext(e) {
    e.stopPropagation();
    if (currentLightboxIndex < window._projectImages.length - 1) {
        currentLightboxIndex++;
        showLightboxImage();
    }
}

function closeLightbox() {
    const overlay = document.getElementById('lightboxOverlay');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

document.addEventListener('keydown', (e) => {
    const overlay = document.getElementById('lightboxOverlay');
    if (!overlay || !overlay.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') lightboxPrev(e);
    if (e.key === 'ArrowRight') lightboxNext(e);
});

/* ===== Gallery image switch (product detail page) ===== */
function switchGalleryImage(idx, thumbEl) {
    const mainImg = document.getElementById('productMainImg');
    if (mainImg && galleryImages[idx]) {
        mainImg.style.opacity = '0';
        setTimeout(() => {
            mainImg.src = galleryImages[idx];
            mainImg.style.opacity = '1';
        }, 150);
        currentGalleryIndex = idx;
    }
    // Update active thumbnail
    document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
    if (thumbEl) thumbEl.classList.add('active');
}

/* ===== Gallery arrow navigation ===== */
function changeGalleryImage(dir) {
    if (galleryImages.length <= 1) return;
    currentGalleryIndex += dir;
    if (currentGalleryIndex < 0) currentGalleryIndex = galleryImages.length - 1;
    if (currentGalleryIndex >= galleryImages.length) currentGalleryIndex = 0;
    
    const mainImg = document.getElementById('productMainImg');
    if (mainImg && galleryImages[currentGalleryIndex]) {
        mainImg.style.opacity = '0';
        setTimeout(() => {
            mainImg.src = galleryImages[currentGalleryIndex];
            mainImg.style.opacity = '1';
        }, 150);
    }
    
    // Update active thumbnail
    document.querySelectorAll('.gallery-thumb').forEach((t, i) => {
        t.classList.toggle('active', i === currentGalleryIndex);
    });
    
    // Scroll thumbnail into view
    const activeThumb = document.querySelectorAll('.gallery-thumb')[currentGalleryIndex];
    if (activeThumb) {
        activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
}

/* ===== Thumbnail scroll arrows ===== */
function scrollThumbnails(dir) {
    const thumbsContainer = document.getElementById('galleryThumbs');
    if (!thumbsContainer) return;
    const scrollAmount = 200;
    thumbsContainer.scrollBy({ left: dir * scrollAmount, behavior: 'smooth' });
}

/* ===== Touch swipe for mobile gallery ===== */
function initGallerySwipe() {
    const gallery = document.querySelector('.gallery-main');
    if (!gallery || galleryImages.length <= 1) return;

    let startX = 0, startY = 0, diffX = 0, diffY = 0;
    const threshold = 50; // minimum swipe distance in px

    gallery.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        diffX = 0;
        diffY = 0;
    }, { passive: true });

    gallery.addEventListener('touchmove', (e) => {
        diffX = e.touches[0].clientX - startX;
        diffY = e.touches[0].clientY - startY;
    }, { passive: true });

    gallery.addEventListener('touchend', () => {
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > threshold) {
            if (diffX > 0) {
                changeGalleryImage(-1); // swipe right → previous
            } else {
                changeGalleryImage(1);  // swipe left → next
            }
        }
    });
}

/* ===== Contact form → WhatsApp redirect ===== */
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = form.querySelector('[name="name"]')?.value || '';
        const email = form.querySelector('[name="email"]')?.value || '';
        const phone = form.querySelector('[name="phone"]')?.value || '';
        const category = form.querySelector('[name="category"]')?.value || '';
        const message = form.querySelector('[name="message"]')?.value || '';

        const text = `Hello Minglu Lighting,%0A%0A*New Inquiry*%0AName: ${name}%0AEmail: ${email}%0APhone: ${phone}%0AProduct Category: ${category}%0A%0A*Message:*%0A${message}`;
        window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${text}`, '_blank');
    });
}

/* ===== Animated counters (stats bar) ===== */
function initStatsCounters() {
    const statsData = [
        { el: 'statYears', target: 12, suffix: '+' },
        { el: 'statCountries', target: 30, suffix: '+' },
        { el: 'statProjects', target: 500, suffix: '+' },
        { el: 'statProducts', target: 50000, suffix: '+', format: true },
    ];
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            statsData.forEach(stat => {
                const el = document.getElementById(stat.el);
                if (!el || el.dataset.animated) return;
                el.dataset.animated = '1';
                const duration = 2000;
                const start = performance.now();
                function update(now) {
                    const elapsed = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const current = Math.floor(eased * stat.target);
                    el.textContent = (stat.format ? current.toLocaleString() : current) + (stat.suffix || '');
                    if (progress < 1) requestAnimationFrame(update);
                    else el.textContent = (stat.format ? stat.target.toLocaleString() : stat.target) + (stat.suffix || '');
                }
                requestAnimationFrame(update);
            });
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.3 });

    const statsBar = document.querySelector('.stats-bar');
    if (statsBar) observer.observe(statsBar);
}

/* ===== Footer product links ===== */
function buildFooterProductLinks() {
    const container = document.getElementById('footerProductLinks');
    if (!container || typeof CATEGORIES === 'undefined') return;
    const base = window.location.pathname.includes('/product/') || window.location.pathname.includes('/blog/') ? '../' : '';
    container.innerHTML = CATEGORIES.slice(0, 6).map(c =>
        `<a href="${base}category/${c.slug}.html">${c.name}</a>`
    ).join('');
}

/* ===== Init ===== */
document.addEventListener('DOMContentLoaded', () => {
    initHeaderScroll();
    initMobileMenu();
    buildCategoryDropdown();
    buildCategoryCards();
    renderFeaturedProducts();
    initProductsPage();
    initProductDetailPage();
    initContactForm();
    buildFooterProductLinks();
    initStatsCounters();
    initProjectsPage();
    initHeroCarousel();
    initBackToTop();
});

/* ============ Back to Top ============ */
function initBackToTop() {
    var btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '<span class="arrow">\u2191</span><span>TOP</span>';
    btn.title = 'Back to top';
    document.body.appendChild(btn);

    var whatsapp = document.querySelector('.whatsapp-float');
    var ticking = false;
    function update() {
        var scrolled = window.scrollY > 300;
        if (scrolled) {
            btn.classList.add('visible');
            if (whatsapp) whatsapp.classList.add('shift-left');
        } else {
            btn.classList.remove('visible');
            if (whatsapp) whatsapp.classList.remove('shift-left');
        }
        ticking = false;
    }

    // Check on load
    update();

    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(update);
            ticking = true;
        }
    }, { passive: true });

    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}
