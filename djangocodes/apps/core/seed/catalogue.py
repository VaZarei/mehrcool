"""Seed: service categories, services, specifications, FAQs, form dropdown options."""

from __future__ import annotations

from apps.core import placeholders as ph
from apps.core.models import BrandServiced, PublishStatus
from apps.core.seed.site import attach
from apps.leads.models import ChoiceGroup, FormFieldChoice
from apps.services.models import Service, ServiceCategory, ServiceFAQ, ServiceSpecification

CATEGORIES = [
    {
        "slug": "commercial-refrigeration",
        "name": "Commercial Refrigeration",
        "headline": "Commercial refrigeration that holds temperature",
        "intro": (
            "Walk-in cold rooms, freezer rooms, display cabinets and cellar cooling for "
            "restaurants, supermarkets, hotels and pharmacies. We design, install, maintain "
            "and repair — with refrigerant handling logged on every visit as the F-Gas "
            "regulation requires."
        ),
        "icon": "snowflake",
        "order": 0,
        "colours": (ph.NAVY_DARK, ph.ICE),
    },
    {
        "slug": "air-conditioning",
        "name": "Air Conditioning",
        "headline": "Commercial air conditioning, installed and maintained to spec",
        "intro": (
            "VRF/VRV and split systems for offices, hospitality and retail. Manufacturer-trained "
            "on Daikin, Mitsubishi Electric, Toshiba and Fujitsu, with planned preventative "
            "maintenance contracts that keep systems efficient and compliant."
        ),
        "icon": "wind",
        "order": 1,
        "colours": (ph.NAVY, "#6F93D4"),
    },
    {
        "slug": "emergency-services",
        "name": "Emergency Services",
        "headline": "24/7 emergency refrigeration and air conditioning repair",
        "intro": (
            "When a cold room warms or a server room overheats, minutes matter. Duty engineers "
            "carry common parts and refrigerants, and attend across London day and night."
        ),
        "icon": "bolt",
        "order": 2,
        "colours": (ph.NAVY_DARK, "#34499E"),
    },
]

SERVICES = [
    {
        "category": "air-conditioning",
        "slug": "vrf-vrv-installation",
        "name": "VRF/VRV Installation",
        "short_summary": "Design and installation of multi-zone VRF/VRV climate control for offices, hotels and mixed-use buildings.",
        "intro": (
            "Variable Refrigerant Flow (VRF — Daikin's trademark is VRV) connects one outdoor condensing "
            "unit to many indoor units, each modulating independently. That means individual zone control, "
            "simultaneous heating and cooling with heat-recovery systems, and lower running costs than "
            "multiple split systems.\n\n"
            "We survey heat loads room by room, size pipework and refrigerant charge to manufacturer "
            "software, and commission every indoor unit with recorded superheat, subcooling and airflow "
            "figures. You receive as-installed drawings, the F-Gas record and the commissioning pack."
        ),
        "response": "Survey within 5 working days",
        "price": "Design and quote free for commercial sites",
        "featured": True,
        "icon": "wind",
        "brands": ["Daikin", "Mitsubishi Electric", "Toshiba", "Fujitsu"],
        "specs": [
            ("System types", "Heat pump (2-pipe) and heat recovery (3-pipe) VRF/VRV"),
            ("Refrigerants", "R32 and R410A depending on manufacturer range"),
            ("Capacity range", "8 kW to 150 kW+ per system, modular"),
            ("Indoor units", "Cassette, ducted, wall-mounted, floor-standing, AHU kits"),
            ("Controls", "Centralised touchscreen, BMS integration (BACnet/Modbus), app control"),
            ("Warranty", "Manufacturer warranty up to 7 years with a PPM contract"),
        ],
        "faqs": [
            (
                "How long does a VRF installation take?",
                "A single-floor office of around 400 m² is typically installed and commissioned in one to two weeks. Larger or occupied buildings are phased floor by floor so tenants keep working.",
            ),
            (
                "Can VRF heat as well as cool?",
                "Yes. Heat pump VRF switches the whole system between heating and cooling; heat recovery VRF lets some rooms heat while others cool at the same time, moving energy between them.",
            ),
            (
                "Do I need planning permission for the outdoor units?",
                "Often not, but listed buildings, conservation areas and some leases have restrictions on external plant. We check this during the survey and prepare acoustic data where required.",
            ),
        ],
    },
    {
        "category": "air-conditioning",
        "slug": "planned-preventative-maintenance",
        "name": "Planned Preventative Maintenance (PPM)",
        "short_summary": "Scheduled servicing that keeps air conditioning compliant, efficient and out of the breakdown log.",
        "intro": (
            "A PPM contract is a schedule of visits — usually two or four a year — where we clean coils and "
            "filters, check refrigerant charge and leak-test the circuit, verify controls and drains, and record "
            "everything in a service report you can hand to an auditor.\n\n"
            "Under the F-Gas regulation, systems containing the equivalent of 5 tonnes of CO₂ or more must be "
            "leak-checked at fixed intervals. We track the CO₂-equivalent charge of every asset on your schedule "
            "and time inspections accordingly, so compliance is automatic rather than a scramble."
        ),
        "response": "Fixed visit dates, agreed annually",
        "price": "From £45 per indoor unit per visit",
        "featured": True,
        "icon": "calendar-check",
        "brands": ["Daikin", "Mitsubishi Electric", "Toshiba", "Fujitsu", "Panasonic", "LG"],
        "specs": [
            ("Visit frequency", "2 or 4 visits per year, per asset"),
            (
                "Included",
                "Coil and filter clean, drain check, electrical inspection, controls test, refrigerant leak check",
            ),
            ("Reporting", "Digital service report per asset with photos and readings"),
            ("F-Gas", "Leak-check intervals tracked by CO₂-equivalent charge"),
            ("Response for contract clients", "Priority callout, discounted labour rate"),
        ],
        "faqs": [
            (
                "Is PPM a legal requirement?",
                "F-Gas leak checking is a legal requirement for systems above 5 tonnes CO₂-equivalent. Beyond that, PPM is how you meet insurer, landlord and TM44 obligations and keep the manufacturer's warranty valid.",
            ),
            (
                "What happens if you find a fault during a visit?",
                "Minor items are fixed on the spot where parts allow. Anything larger is quoted the same day with a fixed price, and contract clients receive discounted labour.",
            ),
        ],
    },
    {
        "category": "air-conditioning",
        "slug": "air-conditioning-repairs",
        "name": "Air Conditioning Repairs",
        "short_summary": "Fault-finding and repair on all major brands: refrigerant leaks, compressors, PCBs, fans and controls.",
        "intro": (
            "Most air conditioning faults present as one of a handful of symptoms — not cooling, tripping, "
            "leaking water, error codes — and each has a short list of causes. Our engineers arrive with gauges, "
            "electronic leak detectors and the common parts for Daikin, Mitsubishi Electric, Toshiba and Fujitsu "
            "systems, so first-visit fix rates stay high.\n\n"
            "If a repair is uneconomic we tell you, with a written comparison against replacement."
        ),
        "response": "Same or next working day",
        "price": "Diagnostic visit from £120 + VAT",
        "featured": False,
        "icon": "wrench",
        "brands": ["Daikin", "Mitsubishi Electric", "Toshiba", "Fujitsu", "Panasonic", "LG"],
        "specs": [
            (
                "Common repairs",
                "Refrigerant leak location and repair, compressor and fan motor replacement, PCB and sensor faults, condensate pump and drain issues",
            ),
            (
                "Diagnostics",
                "Manufacturer service tools, electronic leak detection, nitrogen pressure testing",
            ),
            ("Parts", "Genuine or manufacturer-approved parts, van stock for common items"),
        ],
        "faqs": [
            (
                "My unit shows an error code — what should I do?",
                "Note the code and, if safe, switch the unit off at the isolator. Send us a photo of the display by WhatsApp and we can often tell you the likely fault and bring the right part.",
            ),
        ],
    },
    {
        "category": "air-conditioning",
        "slug": "split-systems",
        "name": "Split System Installation",
        "short_summary": "Wall, cassette and ducted split systems for single rooms, small offices, shops and server rooms.",
        "intro": (
            "A split system pairs one outdoor unit with one (single split) or several (multi-split) indoor "
            "units. It is the right answer for a shop, a meeting room, a small office or a comms room that needs "
            "reliable cooling without the scale of VRF.\n\n"
            "Server and comms rooms get particular attention: we specify units rated for continuous low-ambient "
            "operation and, where uptime matters, install duty/standby pairs with automatic changeover."
        ),
        "response": "Installed within 10 working days of order",
        "price": "Single wall-mounted system from £1,650 + VAT installed",
        "featured": False,
        "icon": "wind",
        "brands": ["Daikin", "Mitsubishi Electric", "Toshiba", "Fujitsu", "Panasonic", "LG"],
        "specs": [
            (
                "Types",
                "Single split, multi-split (up to 5 indoor units), ducted, cassette, wall-mounted",
            ),
            ("Capacity", "2.5 kW to 14 kW per system"),
            ("Refrigerant", "R32"),
            (
                "Options",
                "Duty/standby changeover, low-ambient kits, condensate pumps, Wi-Fi control",
            ),
        ],
        "faqs": [
            (
                "How noisy is the outdoor unit?",
                "Modern inverter units run at 45–55 dB(A) at one metre — comparable to a quiet conversation. We position and mount them to keep noise away from neighbours and bedrooms.",
            ),
        ],
    },
    {
        "category": "commercial-refrigeration",
        "slug": "walk-in-cold-rooms",
        "name": "Walk-In Cold Rooms",
        "short_summary": "Modular walk-in cold rooms designed, built and commissioned for kitchens, food retail and pharmacies.",
        "intro": (
            "A walk-in cold room is a building inside your building: insulated panels, a door that seals, "
            "an evaporator matched to the load and a condensing unit sited where it can reject heat. Get the "
            "sizing wrong and the room struggles on the first hot Saturday in July.\n\n"
            "We calculate the load from product throughput, door openings, ambient temperature and lighting, "
            "then specify panels (typically 80–100 mm for chilled rooms) and plant with 20–25% headroom. "
            "Commissioning includes pull-down to temperature, defrost cycle proving and a temperature logger "
            "left running for 24 hours."
        ),
        "response": "Survey within 3 working days",
        "price": "Chilled rooms from £6,500 + VAT installed",
        "featured": True,
        "icon": "snowflake",
        "brands": ["Foster", "Williams", "Bitzer", "Danfoss"],
        "specs": [
            ("Panels", "80 mm or 100 mm PIR insulated, food-safe white or stainless facing"),
            ("Temperature", "Chilled +1 °C to +4 °C; freezer -18 °C to -22 °C"),
            ("Refrigerants", "R290 (propane) and R448A/R449A low-GWP blends"),
            ("Plant", "Monobloc, remote condensing unit or pack system"),
            (
                "Controls",
                "Digital controller with alarm relay and optional remote temperature monitoring",
            ),
            ("Floor", "Insulated floor or floorless on insulated slab"),
        ],
        "faqs": [
            (
                "How long does it take to build a cold room?",
                "A standard 3 m × 3 m chilled room is typically built and commissioned in two days. Freezer rooms and rooms with insulated floors take three to four.",
            ),
            (
                "Can you fit a cold room in a basement kitchen?",
                "Yes — panels are modular and carried in by hand. The main constraint is heat rejection: we route the condensing unit to an external wall or a ventilated plant area.",
            ),
            (
                "Which refrigerant will you use?",
                "For new plant we default to R290 (propane) or a low-GWP HFO blend. Both meet current and forthcoming F-Gas phase-down rules, so you are not buying obsolescence.",
            ),
        ],
    },
    {
        "category": "commercial-refrigeration",
        "slug": "display-refrigeration",
        "name": "Display Refrigeration",
        "short_summary": "Multideck, serve-over and island display cabinets for food retail, delis and convenience stores.",
        "intro": (
            "Display refrigeration works hardest in the worst conditions: open-fronted, under shop lighting, "
            "opposite a door that never shuts. We supply, install and maintain multidecks, serve-overs, "
            "patisserie cabinets and island freezers — integral units for smaller stores and remote-plant "
            "cabinets on a pack system for supermarkets.\n\n"
            "Maintenance focuses on the things that fail: fan motors, door gaskets, defrost heaters and "
            "condenser cleanliness. A dirty condenser can add 20% to running costs before it causes a breakdown."
        ),
        "response": "Repairs same or next day",
        "price": "Maintenance from £38 per cabinet per visit",
        "featured": True,
        "icon": "thermometer",
        "brands": ["Foster", "Williams"],
        "specs": [
            (
                "Cabinet types",
                "Multideck, serve-over, patisserie, island freezer, upright glass-door",
            ),
            ("Plant", "Integral (plug-in) or remote pack systems"),
            ("Refrigerants", "R290, R744 (CO₂), R448A/R449A"),
            ("Energy", "Night blinds, LED lighting, EC fan motors, glass-door retrofits"),
        ],
        "faqs": [
            (
                "Can you retrofit doors to open multidecks?",
                "Yes. Glass-door retrofits typically cut cabinet energy use by 30–40% and hold temperature more consistently. We measure the cabinet and source doors to fit.",
            ),
        ],
    },
    {
        "category": "commercial-refrigeration",
        "slug": "cellar-cooling",
        "name": "Cellar Cooling",
        "short_summary": "Beer cellar cooling installation and repair for pubs, bars and restaurants — keeping kegs at 11–13 °C.",
        "intro": (
            "Cask and keg beer wants a cellar between 11 °C and 13 °C. Too warm and the beer fobs and spoils; "
            "too cold and cask ale goes hazy. Cellar cooling units are simple, but they run continuously in a "
            "damp room and fail quietly — usually on the hottest weekend of the year.\n\n"
            "We install ceiling-mounted and split cellar coolers sized to cellar volume and keg throughput, "
            "and offer a pre-summer service that cleans coils, checks charge and tests the thermostat before "
            "the heat arrives."
        ),
        "response": "Emergency attendance 24/7",
        "price": "Pre-summer service from £145 + VAT",
        "featured": False,
        "icon": "thermometer",
        "brands": ["Bitzer", "Danfoss"],
        "specs": [
            ("Unit types", "Ceiling-mounted monobloc, split system with remote condenser"),
            ("Capacity", "Cellars from 15 m³ to 120 m³"),
            ("Set point", "11 °C to 13 °C, adjustable"),
            ("Refrigerant", "R290 or R449A"),
        ],
        "faqs": [
            (
                "The cellar is warm but the unit is running — what's wrong?",
                "Usually a dirty condenser, a low refrigerant charge or a failed fan. Prop the cellar door shut, avoid loading warm stock, and call us — this is the most common summer emergency we attend.",
            ),
        ],
    },
    {
        "category": "commercial-refrigeration",
        "slug": "freezer-rooms",
        "name": "Freezer Rooms",
        "short_summary": "Walk-in freezer rooms to -22 °C with insulated floors, heated door frames and alarmed controls.",
        "intro": (
            "Freezer rooms are cold rooms with less margin for error. Panels are thicker (100–150 mm), the floor "
            "must be insulated, door frames are heated to stop ice bridging, and the evaporator needs a reliable "
            "defrost so it does not become a block of ice.\n\n"
            "We build freezer rooms for kitchens, food manufacturers and pharmaceutical storage, with temperature "
            "alarms that call your phone if the room drifts — because product loss in a freezer is measured in "
            "thousands of pounds."
        ),
        "response": "Survey within 3 working days",
        "price": "Freezer rooms from £9,800 + VAT installed",
        "featured": False,
        "icon": "snowflake",
        "brands": ["Foster", "Williams", "Bitzer", "Danfoss"],
        "specs": [
            ("Panels", "100 mm to 150 mm PIR with insulated floor"),
            ("Temperature", "-18 °C to -22 °C (lower on request)"),
            ("Door", "Heated frame, pressure relief port, safety release"),
            ("Defrost", "Electric or hot-gas, timed and demand-based"),
            ("Alarms", "High-temperature alarm with SMS/app notification option"),
        ],
        "faqs": [
            (
                "How long will a freezer hold temperature in a power cut?",
                "A well-built, full freezer room with the door shut will typically stay below -12 °C for six to eight hours. Keep the door closed and call us; we can bring temporary plant if the outage is prolonged.",
            ),
        ],
    },
    {
        "category": "emergency-services",
        "slug": "emergency-callout",
        "name": "24/7 Emergency Callout",
        "short_summary": "Rapid-response diagnosis and repair for refrigeration and air conditioning breakdowns, day and night.",
        "intro": (
            "Call the emergency line and you speak to an engineer, not an answering service. We ask three "
            "questions — what has failed, where, and what the display says — then dispatch the nearest duty "
            "engineer with the likely parts.\n\n"
            "On arrival we stabilise first (temporary plant, refrigerant top-up, bypass), then diagnose and repair "
            "or quote. Every emergency visit ends with a written report, including the refrigerant record."
        ),
        "response": "Engineer on site in under 2 hours across London",
        "price": "Emergency callout from £180 + VAT (first hour)",
        "featured": True,
        "icon": "bolt",
        "brands": ["Daikin", "Mitsubishi Electric", "Toshiba", "Fujitsu", "Foster", "Williams"],
        "is_emergency": True,
        "specs": [
            ("Coverage", "London, Greater London, Berkshire — 24 hours, 365 days"),
            (
                "Van stock",
                "Common compressors, fan motors, controllers, R32/R290/R449A refrigerant, nitrogen",
            ),
            ("Temporary plant", "Portable cooling and hire cold-store arranged on request"),
            ("Reporting", "Written report and F-Gas record after every visit"),
        ],
        "faqs": [
            (
                "What counts as an emergency?",
                "Any failure that puts stock, product or people at risk: a cold or freezer room warming, display cabinets off, a server room overheating, or air conditioning failure in a care setting. If you are unsure, call — we will tell you honestly whether it can wait until morning.",
            ),
            (
                "Do you charge more at night and weekends?",
                "Out-of-hours attendance carries an uplift, which we state on the phone before dispatching. Contract clients receive priority response and discounted rates.",
            ),
        ],
    },
]

FORM_CHOICES = {
    ChoiceGroup.ENQUIRY_TYPE: [
        ("Planned maintenance (PPM) contract", "ppm-contract"),
        ("New installation quote", "installation-quote"),
        ("Repair — not urgent", "repair"),
        ("Tender / procurement enquiry", "tender"),
        ("Something else", "other"),
    ],
    ChoiceGroup.EMERGENCY_ISSUE: [
        ("Walk-in cold room or freezer warming", "cold-room"),
        ("Display fridge / freezer cabinet failed", "display-cabinet"),
        ("Cellar cooling down", "cellar"),
        ("Air conditioning failed", "air-conditioning"),
        ("Server / comms room overheating", "server-room"),
        ("Leak, alarm or tripping breaker", "leak-alarm"),
        ("Not sure", "unknown"),
    ],
    ChoiceGroup.BUILDING_TYPE: [
        ("Restaurant / café / bar", "restaurant"),
        ("Supermarket / convenience store", "retail"),
        ("Hotel", "hotel"),
        ("Office", "office"),
        ("Healthcare / pharmacy", "healthcare"),
        ("Data centre / comms room", "data-centre"),
        ("Warehouse / industrial", "industrial"),
        ("Other", "other"),
    ],
    ChoiceGroup.FLOOR_AREA: [
        ("Under 100 m²", "under-100"),
        ("100–500 m²", "100-500"),
        ("500–2,000 m²", "500-2000"),
        ("Over 2,000 m²", "over-2000"),
    ],
    ChoiceGroup.SYSTEM_TYPE: [
        ("Walk-in cold room / freezer", "cold-room"),
        ("Display refrigeration", "display"),
        ("Cellar cooling", "cellar"),
        ("VRF/VRV air conditioning", "vrf"),
        ("Split system air conditioning", "split"),
        ("Not sure — need advice", "advice"),
    ],
    ChoiceGroup.TIMELINE: [
        ("As soon as possible", "asap"),
        ("Within 1 month", "1-month"),
        ("1–3 months", "1-3-months"),
        ("Planning for later this year", "later"),
    ],
    ChoiceGroup.BUDGET_BAND: [
        ("Under £5,000", "under-5k"),
        ("£5,000 – £15,000", "5-15k"),
        ("£15,000 – £50,000", "15-50k"),
        ("Over £50,000", "over-50k"),
        ("Not yet set", "unknown"),
    ],
}


def seed_form_choices() -> None:
    """Dropdown options for every form."""
    for group, options in FORM_CHOICES.items():
        for order, (label, value) in enumerate(options):
            FormFieldChoice.objects.update_or_create(
                group=group,
                value=value,
                defaults={"label": label, "order": order, "is_active": True},
            )


def seed_services() -> None:
    """Categories, services, specs and FAQs."""
    brands = {b.name: b for b in BrandServiced.objects.all()}
    for data in CATEGORIES:
        cat, _ = ServiceCategory.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "name": data["name"],
                "headline": data["headline"],
                "intro": data["intro"],
                "icon": data["icon"],
                "order": data["order"],
                "status": PublishStatus.PUBLISHED,
                "hero_image_alt": f"{data['name']} — placeholder image",
            },
        )
        start, end = data["colours"]
        attach(
            cat.hero_image,
            ph.scene_jpeg(
                f"category-{cat.slug}.jpg", start=start, end=end, seed=data["order"] + 10
            ),
        )
        cat.save()

    for order, data in enumerate(SERVICES):
        category = ServiceCategory.objects.get(slug=data["category"])
        service, _ = Service.objects.update_or_create(
            category=category,
            slug=data["slug"],
            defaults={
                "name": data["name"],
                "short_summary": data["short_summary"],
                "intro": data["intro"],
                "typical_response_time": data["response"],
                "price_from_note": data["price"],
                "is_featured": data["featured"],
                "is_emergency": data.get("is_emergency", False),
                "icon": data["icon"],
                "order": order,
                "status": PublishStatus.PUBLISHED,
                "hero_image_alt": f"{data['name']} — placeholder image",
            },
        )
        attach(
            service.hero_image,
            ph.scene_jpeg(
                f"service-{service.slug}.jpg",
                seed=order + 20,
                end="#6F93D4" if order % 2 else ph.ICE,
            ),
        )
        service.save()
        service.brands.set([brands[b] for b in data["brands"] if b in brands])
        service.specifications.all().delete()
        for i, (label, value) in enumerate(data["specs"]):
            ServiceSpecification.objects.create(service=service, label=label, value=value, order=i)
        service.faqs.all().delete()
        for i, (q, a) in enumerate(data["faqs"]):
            ServiceFAQ.objects.create(service=service, question=q, answer=a, order=i)

    # Related services
    by_slug = {s.slug: s for s in Service.objects.all()}
    related = {
        "walk-in-cold-rooms": ["freezer-rooms", "display-refrigeration", "emergency-callout"],
        "freezer-rooms": ["walk-in-cold-rooms", "emergency-callout"],
        "display-refrigeration": ["walk-in-cold-rooms", "emergency-callout"],
        "cellar-cooling": ["emergency-callout", "walk-in-cold-rooms"],
        "vrf-vrv-installation": ["planned-preventative-maintenance", "split-systems"],
        "planned-preventative-maintenance": ["air-conditioning-repairs", "vrf-vrv-installation"],
        "air-conditioning-repairs": ["planned-preventative-maintenance", "emergency-callout"],
        "split-systems": ["vrf-vrv-installation", "planned-preventative-maintenance"],
        "emergency-callout": ["air-conditioning-repairs", "planned-preventative-maintenance"],
    }
    for slug, rel in related.items():
        by_slug[slug].related_services.set([by_slug[r] for r in rel])
