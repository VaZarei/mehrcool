"""Seed: content pages (About, legal, F-Gas statement, Careers) and index-page copy."""

from __future__ import annotations

from apps.core.models import PublishStatus
from apps.pages.models import BlockBackground, BlockType, Page, PageBlock, PageTemplate

ABOUT_BLOCKS = [
    dict(
        block_type=BlockType.RICH_TEXT,
        heading="Engineers first",
        body=(
            "Mehr Cool Refrigeration & Air Conditioning Ltd was incorporated in May 2024 and is based in Canary Wharf. "
            "The company was founded by working refrigeration engineers who had spent years watching good equipment fail "
            "for avoidable reasons: dirty condensers, skipped leak checks, undersized plant and paperwork nobody kept.\n\n"
            "We run the business the way we would want a contractor to run it for us. The engineer who quotes the job is "
            "the engineer who installs it. Every visit ends with a written report. Every gram of refrigerant is recorded."
        ),
    ),
    dict(
        block_type=BlockType.STAT_ROW,
        heading="",
        columns=4,
        background=BlockBackground.ICE,
        items=(
            "24/7 :: Emergency line answered by an engineer\n"
            "< 2 hrs :: Typical emergency response across London\n"
            "100% :: Engineers F-Gas certified\n"
            "10+ :: Manufacturers installed and maintained"
        ),
    ),
    dict(
        block_type=BlockType.FEATURE_GRID,
        heading="Why F-Gas matters to you",
        columns=3,
        items=(
            "It is the law :: Anyone handling fluorinated refrigerants in the UK must hold an F-Gas certificate. Using an uncertified contractor exposes the equipment owner to enforcement action, not just the contractor.\n"
            "Leak checks are mandatory :: Systems containing 5 tonnes CO₂-equivalent or more must be leak-tested at fixed intervals and the results recorded. We calculate the threshold for every asset and schedule accordingly.\n"
            "Records protect you :: Insurers, landlords and auditors ask for refrigerant logs. Ours are issued after every visit and kept for five years, as the regulation requires."
        ),
    ),
    dict(block_type=BlockType.LOGO_STRIP, logo_source="badges"),
    dict(
        block_type=BlockType.RICH_TEXT,
        heading="Company details",
        background=BlockBackground.ICE,
        body=(
            "**Legal name:** MEHR COOL REFRIGERATION & AIR CONDITIONING LTD\n\n"
            "**Company number:** 15733975 (registered in England and Wales)\n\n"
            "**Registered office:** Dept 2710, 126 East Ferry Road, Canary Wharf, London, E14 9FP\n\n"
            "**Principal activity:** SIC 43220 — Plumbing, heat and air-conditioning installation"
        ),
    ),
]

FGAS_BLOCKS = [
    dict(
        block_type=BlockType.RICH_TEXT,
        body=(
            "## Our obligations\n"
            "Mehr Cool Refrigeration & Air Conditioning Ltd handles fluorinated greenhouse gases (F-Gases) in the course "
            "of installing, maintaining and decommissioning refrigeration and air conditioning equipment. We operate under "
            "the F-Gas Regulation (EC 517/2014, as retained in UK law) and the associated UK company certification requirements.\n\n"
            "## Certification\n"
            "- Every engineer who handles refrigerant holds a valid F-Gas category certificate.\n"
            "- The company holds, or is in the process of obtaining, company certification through a recognised UK scheme. "
            "Certificate numbers are shown on our accreditation badges once issued and are available on request.\n\n"
            "## What we do on every job\n"
            "- Recover refrigerant rather than vent it, using certified recovery equipment.\n"
            "- Weigh and record all refrigerant added or removed, by type and quantity.\n"
            "- Issue a written record to the equipment operator after every intervention.\n"
            "- Leak-test systems at the intervals the regulation requires, based on CO₂-equivalent charge.\n"
            "- Label equipment with refrigerant type, charge and GWP.\n\n"
            "## Refrigerant choice\n"
            "For new installations we specify low-GWP refrigerants — R32 for air conditioning, R290 (propane) or R448A/R449A "
            "for commercial refrigeration — so that equipment we install today remains serviceable through the HFC phase-down.\n\n"
            "## Questions\n"
            "If you are an equipment operator and unsure of your own obligations, ask us. We will explain what applies to your "
            "systems in plain English."
        ),
    ),
]

LEGAL_TERMS = (
    "## 1. These terms\n"
    "These terms of business apply to all quotations, installations, maintenance contracts and repair work carried out by "
    'MEHR COOL REFRIGERATION & AIR CONDITIONING LTD (company number 15733975), referred to as "we" or "us".\n\n'
    "## 2. Quotations\n"
    "Written quotations are valid for 30 days unless stated otherwise. Prices exclude VAT unless shown as inclusive. "
    "Work outside the quoted scope is agreed in writing before it starts.\n\n"
    "## 3. Emergency callouts\n"
    "Emergency attendance is charged at the rate stated when the call is booked, including any out-of-hours uplift. "
    "Parts and refrigerant are charged in addition unless a fixed price is agreed.\n\n"
    "## 4. Payment\n"
    "Invoices are payable within 30 days. We may charge statutory interest on late payment. Title to equipment passes on full payment.\n\n"
    "## 5. Warranty\n"
    "Our workmanship is guaranteed for 12 months. Manufacturer warranties apply to equipment and may require a maintenance contract to remain valid.\n\n"
    "## 6. Access and site conditions\n"
    "You agree to provide safe access, power and water where needed. Delays caused by access restrictions may be charged.\n\n"
    "## 7. Liability\n"
    "Nothing in these terms limits liability for death or personal injury caused by negligence. Our liability for other losses is limited to the value of the work concerned.\n\n"
    "## 8. Governing law\n"
    "These terms are governed by the law of England and Wales."
)

LEGAL_PRIVACY = (
    "## Who we are\n"
    "MEHR COOL REFRIGERATION & AIR CONDITIONING LTD, Dept 2710, 126 East Ferry Road, Canary Wharf, London, E14 9FP, is the data controller for personal data collected through this website.\n\n"
    "## What we collect\n"
    "- Contact details you submit through our forms (name, phone, email, company, message).\n"
    "- Technical information about your visit (pages viewed, device type) via analytics cookies, where you consent.\n\n"
    "## Why we collect it\n"
    "To respond to your enquiry, arrange engineer visits, prepare quotations and, if you become a customer, deliver our services and keep the legal records the F-Gas regulation requires.\n\n"
    "## Legal basis\n"
    "Responding to enquiries: our legitimate interest and steps towards a contract. Service records: legal obligation. Analytics: consent.\n\n"
    "## How long we keep it\n"
    "Enquiry data is kept for 24 months. Customer and refrigerant records are kept for at least five years as required by law.\n\n"
    "## Your rights\n"
    "You may ask for a copy of your data, correction, deletion or restriction of processing. Contact us using the details on the Contact page. You may also complain to the Information Commissioner's Office."
)

LEGAL_COOKIES = (
    "## Essential cookies\n"
    "We set a session cookie and a security (CSRF) cookie so our forms work. These do not track you and cannot be switched off.\n\n"
    "## Analytics cookies\n"
    "If Google Analytics or Google Tag Manager is enabled on this site, Google may set cookies to measure how the site is used. "
    "IP addresses are anonymised. You can block these cookies in your browser without affecting the site.\n\n"
    "## Third-party content\n"
    "Embedded maps and videos may set their own cookies when loaded. We use privacy-enhanced embeds where available."
)

CAREERS = (
    "## Refrigeration & air conditioning engineers\n"
    "We are a small, growing company based in Canary Wharf and we hire engineers who take pride in a tidy install and an honest diagnosis.\n\n"
    "**You will need:**\n"
    "- F-Gas Category 1 certification\n"
    "- Experience on commercial refrigeration (cold rooms, display, cellar cooling) or VRF/split air conditioning — ideally both\n"
    "- A full UK driving licence\n"
    "- The ability to explain a fault to a chef at 11pm without jargon\n\n"
    "**We offer:**\n"
    "- Competitive salary with paid on-call and overtime\n"
    "- Company van, tools and manufacturer training\n"
    "- A say in how the company is run\n\n"
    "Send a short note about your experience to the email address on our Contact page. No agencies."
)

EMERGENCY_STEPS = (
    "Keep doors shut. :: A closed cold room holds temperature for hours; an open one loses it in minutes.\n"
    "Note the error code. :: A photo of the controller display saves us diagnostic time on arrival.\n"
    "Log the temperature. :: Your due-diligence record starts now — write down the time and reading."
)

PAGES = [
    dict(
        slug="about",
        title="About Mehr Cool",
        template=PageTemplate.STANDARD,
        order=0,
        intro="An independent refrigeration and air conditioning contractor in Canary Wharf, run by engineers, covering London, Greater London and Berkshire around the clock.",
        audience_note="Contract buyers (Path B)",
        blocks=ABOUT_BLOCKS,
    ),
    dict(
        slug="f-gas-compliance",
        title="F-Gas compliance statement",
        template=PageTemplate.NARROW,
        order=1,
        intro="How we meet the F-Gas Regulation (EC 517/2014) on every job, and what that means for equipment owners.",
        audience_note="Contract buyers (Path B)",
        blocks=FGAS_BLOCKS,
    ),
    dict(
        slug="terms",
        title="Terms of business",
        template=PageTemplate.NARROW,
        order=10,
        intro="",
        show_contact_cta=False,
        blocks=[dict(block_type=BlockType.RICH_TEXT, body=LEGAL_TERMS)],
    ),
    dict(
        slug="privacy",
        title="Privacy policy",
        template=PageTemplate.NARROW,
        order=11,
        intro="",
        show_contact_cta=False,
        blocks=[dict(block_type=BlockType.RICH_TEXT, body=LEGAL_PRIVACY)],
    ),
    dict(
        slug="cookies",
        title="Cookie policy",
        template=PageTemplate.NARROW,
        order=12,
        intro="",
        show_contact_cta=False,
        blocks=[dict(block_type=BlockType.RICH_TEXT, body=LEGAL_COOKIES)],
    ),
    dict(
        slug="careers",
        title="Careers",
        template=PageTemplate.NARROW,
        order=13,
        intro="Join a small team of engineers who care about doing the job properly.",
        blocks=[dict(block_type=BlockType.RICH_TEXT, body=CAREERS)],
    ),
    # Copy holders for built-in index pages (never served directly).
    dict(
        slug="services",
        title="Commercial refrigeration & air conditioning services",
        template=PageTemplate.STANDARD,
        order=20,
        intro="Every service we offer, grouped the way facilities teams buy them: cooling for product, cooling for people, and what happens when either stops.",
        audience_note="Copy for the /services/ index",
        blocks=[],
    ),
    dict(
        slug="sectors",
        title="Sectors we serve",
        template=PageTemplate.STANDARD,
        order=21,
        intro="Cooling failures cost different things in different buildings: stock in a supermarket, guests in a hotel, uptime in a data centre. We plan maintenance around what your building cannot afford to lose.",
        audience_note="Copy for the /sectors/ index",
        blocks=[],
    ),
    dict(
        slug="case-studies",
        title="Case studies",
        template=PageTemplate.STANDARD,
        order=22,
        intro="Real sites, real faults, measurable results. Filter by sector, service or area.",
        audience_note="Copy for the /case-studies/ index",
        blocks=[],
    ),
    dict(
        slug="areas",
        title="Areas we cover",
        template=PageTemplate.STANDARD,
        order=23,
        intro="Engineers based in Canary Wharf with vans across London, Greater London and Berkshire. Pick your area for local response times and recent work nearby.",
        audience_note="Copy for the /areas/ index",
        blocks=[],
    ),
    dict(
        slug="contact",
        title="Contact Mehr Cool",
        template=PageTemplate.STANDARD,
        order=24,
        intro="For a breakdown, call — we answer around the clock. For maintenance contracts, new installations and tenders, send the site details below and an engineer will reply within one working day.",
        audience_note="Copy for the /contact/ page",
        blocks=[],
    ),
    dict(
        slug="emergency-callout",
        title="Refrigeration or air conditioning down? Call now.",
        template=PageTemplate.STANDARD,
        order=25,
        intro="Leave your mobile number and the duty engineer rings you back within minutes.",
        audience_note="Copy for the /emergency-callout/ page (heading, intro, 3-step tips)",
        blocks=[
            dict(
                block_type=BlockType.FEATURE_GRID,
                heading="While you wait",
                columns=3,
                items=EMERGENCY_STEPS,
            )
        ],
    ),
]


def seed_pages() -> None:
    """Create pages and their blocks (blocks are replaced on re-run)."""
    for data in PAGES:
        blocks = data.pop("blocks")
        page, _ = Page.objects.update_or_create(
            slug=data["slug"],
            defaults={
                **{k: v for k, v in data.items() if k != "slug"},
                "status": PublishStatus.PUBLISHED,
            },
        )
        page.blocks.all().delete()
        for order, block in enumerate(blocks):
            PageBlock.objects.create(page=page, order=order, **block)
        data["blocks"] = blocks
