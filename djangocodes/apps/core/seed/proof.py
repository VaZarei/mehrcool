"""Seed: sectors, service areas, testimonials and case studies (demo proof content).

Every client name, project figure and review here is illustrative and listed in
``COPY_TO_VERIFY.md`` for the client to confirm or replace before launch.
"""

from __future__ import annotations

from datetime import date

from apps.core import placeholders as ph
from apps.core.models import PublishStatus
from apps.core.seed.site import attach
from apps.locations.models import AreaRegion, ServiceArea
from apps.projects.models import CaseStudy, Sector
from apps.services.models import Service
from apps.testimonials.models import ReviewSource, Testimonial

SECTORS = [
    (
        "restaurants",
        "Restaurants & hospitality",
        "building",
        "A restaurant loses money twice when refrigeration fails: the stock, and the covers turned away while the kitchen recovers. We plan cold room, display and kitchen air conditioning maintenance around service hours and hold priority slots for contract clients during summer.",
        ["walk-in-cold-rooms", "cellar-cooling", "emergency-callout", "split-systems"],
    ),
    (
        "supermarkets",
        "Supermarkets & food retail",
        "building",
        "Display refrigeration runs 24 hours a day under lights and foot traffic. We maintain multideck and island cabinets, pack systems and cold stores for independent supermarkets and convenience groups, with energy upgrades such as glass doors and EC fans that pay back inside two years.",
        ["display-refrigeration", "walk-in-cold-rooms", "freezer-rooms", "emergency-callout"],
    ),
    (
        "hotels",
        "Hotels",
        "building",
        "Guest comfort and kitchen compliance in one contract. VRF systems across bedrooms and function rooms, walk-in cold rooms behind the kitchen, cellar cooling under the bar — maintained on a schedule that works around occupancy and events.",
        [
            "vrf-vrv-installation",
            "planned-preventative-maintenance",
            "walk-in-cold-rooms",
            "cellar-cooling",
        ],
    ),
    (
        "offices",
        "Offices & commercial property",
        "building",
        "For landlords and facilities managers, air conditioning is a compliance asset as much as a comfort one: F-Gas leak checks, TM44 inspections and tenant complaints all land on the same desk. We run PPM contracts across multi-tenant buildings with consolidated reporting.",
        ["vrf-vrv-installation", "planned-preventative-maintenance", "air-conditioning-repairs"],
    ),
    (
        "healthcare",
        "Healthcare & pharmacies",
        "shield-check",
        "Vaccine fridges, pharmacy cold rooms and clinical air conditioning have documented temperature requirements and audit trails. We install alarmed, logged refrigeration and maintain it with the paperwork inspectors expect to see.",
        [
            "walk-in-cold-rooms",
            "freezer-rooms",
            "planned-preventative-maintenance",
            "emergency-callout",
        ],
    ),
    (
        "data-centres",
        "Data centres & comms rooms",
        "bolt",
        "Heat is the enemy of uptime. We specify close-control and duty/standby split systems for server and comms rooms, with low-ambient operation, automatic changeover and remote alerting so a cooling fault never becomes an outage.",
        [
            "split-systems",
            "air-conditioning-repairs",
            "planned-preventative-maintenance",
            "emergency-callout",
        ],
    ),
]

AREAS = [
    (
        "canary-wharf",
        "Canary Wharf",
        AreaRegion.EAST_LONDON,
        "E14",
        "Under 45 minutes",
        "Canary Wharf is home. Our registered office is on East Ferry Road, which means engineers are already on the Isle of Dogs when a call comes in from a Canada Square office or a Westferry restaurant.\n\nTypical work here: VRF maintenance across multi-tenant office floors, close-control cooling for comms rooms, and cold room and cellar cooling for the bars and restaurants around the docks.",
    ),
    (
        "city-of-london",
        "City of London",
        AreaRegion.CENTRAL_LONDON,
        "EC1, EC2, EC3, EC4",
        "Under 60 minutes",
        "The Square Mile runs on air conditioning and coffee. We look after VRF systems in serviced offices, split systems in comms rooms, and the refrigeration behind the lunchtime trade — display cabinets, cold rooms and cellar cooling in pubs and restaurants.\n\nAccess and out-of-hours working are the norm here; we carry the permits, RAMS and insurance evidence building managers ask for.",
    ),
    (
        "westminster",
        "Westminster & West End",
        AreaRegion.CENTRAL_LONDON,
        "SW1, W1, WC2",
        "Under 60 minutes",
        "From Soho kitchens to Victoria offices, Westminster mixes heritage buildings with dense hospitality. Listed-building constraints on external plant are common; we design around them with low-profile condensers, acoustic enclosures and internal plant rooms.",
    ),
    (
        "southwark",
        "Southwark & Bermondsey",
        AreaRegion.SOUTH_LONDON,
        "SE1, SE16",
        "Under 60 minutes",
        "Borough Market traders, Bermondsey Street restaurants and the offices along the South Bank keep us busy in SE1. Display refrigeration and walk-in cold rooms dominate; we also maintain air conditioning for several converted-warehouse office buildings.",
    ),
    (
        "hackney",
        "Hackney & Shoreditch",
        AreaRegion.EAST_LONDON,
        "E1, E2, E8",
        "Under 60 minutes",
        "Independent restaurants, bars and food producers in Shoreditch and Hackney need refrigeration that survives basement kitchens and tight sites. We fit compact cold rooms and cellar coolers and run pre-summer maintenance rounds across the borough.",
    ),
    (
        "stratford",
        "Stratford & Newham",
        AreaRegion.EAST_LONDON,
        "E15, E20",
        "Under 60 minutes",
        "Retail at Westfield and the surrounding food outlets, plus the new residential and office blocks around the Olympic Park. Display refrigeration maintenance and split-system installs are our most common jobs in E15 and E20.",
    ),
    (
        "islington",
        "Islington & Camden",
        AreaRegion.NORTH_LONDON,
        "N1, NW1",
        "Under 75 minutes",
        "Upper Street, Camden Market and the King's Cross development bring a dense mix of restaurants, bars and offices. Cellar cooling repairs peak here every summer; we schedule pre-season services from April.",
    ),
    (
        "croydon",
        "Croydon",
        AreaRegion.SOUTH_LONDON,
        "CR0, CR2",
        "Under 90 minutes",
        "South London's largest commercial centre, with supermarkets, offices and a growing restaurant quarter around Boxpark. We maintain display refrigeration and air conditioning across the town centre and Purley Way retail parks.",
    ),
    (
        "ealing",
        "Ealing & Acton",
        AreaRegion.WEST_LONDON,
        "W3, W5, W13",
        "Under 90 minutes",
        "West London food retail and hospitality, plus light-industrial units in Park Royal with process cooling and cold storage needs. Freezer room builds and pack-system maintenance are regular work here.",
    ),
    (
        "heathrow-hounslow",
        "Heathrow & Hounslow",
        AreaRegion.WEST_LONDON,
        "TW3, TW4, TW6",
        "Under 90 minutes",
        "Hotels and airport-adjacent logistics dominate around Heathrow. VRF maintenance across hotel bedrooms and temperature-controlled storage for freight forwarders are our core services in the area.",
    ),
    (
        "reading",
        "Reading",
        AreaRegion.BERKSHIRE,
        "RG1, RG2, RG30",
        "Under 2 hours",
        "Reading's business parks, data centres and town-centre hospitality extend our Berkshire coverage. We run PPM contracts for office VRF systems and close-control cooling for comms rooms along the M4 corridor.",
    ),
    (
        "slough",
        "Slough & Windsor",
        AreaRegion.BERKSHIRE,
        "SL1, SL3, SL4",
        "Under 2 hours",
        "Slough Trading Estate's food manufacturers and distribution units need cold storage that meets audit standards; Windsor's hotels and restaurants need discreet plant and quiet condensers. We cover both from the M4.",
    ),
]

TESTIMONIALS = [
    (
        "Daniel R.",
        "Operations Manager",
        "Restaurant group, Soho",
        5,
        ReviewSource.GOOGLE,
        date(2025, 7, 14),
        True,
        "westminster",
        "cellar-cooling",
        "Cellar cooler died on a Friday in July. Rang at 6pm, engineer on site by half seven, kegs back to temperature before the evening rush. Fitted a new unit the following week at the price quoted.",
    ),
    (
        "Priya S.",
        "Facilities Manager",
        "Serviced offices, Canary Wharf",
        5,
        ReviewSource.GOOGLE,
        date(2025, 5, 2),
        True,
        "canary-wharf",
        "planned-preventative-maintenance",
        "We moved our VRF maintenance to Mehr Cool this year. The F-Gas paperwork is finally in order, the reports are clear enough to forward to tenants, and they turn up when they say they will.",
    ),
    (
        "Tom H.",
        "Store Manager",
        "Convenience store, Stratford",
        5,
        ReviewSource.GOOGLE,
        date(2025, 3, 21),
        True,
        "stratford",
        "display-refrigeration",
        "Multideck kept icing up and two previous companies couldn't fix it. Mehr Cool found a failed defrost sensor in twenty minutes. Straightforward people who know their kit.",
    ),
    (
        "Marie L.",
        "Head Chef",
        "Hotel kitchen, Westminster",
        5,
        ReviewSource.DIRECT,
        date(2024, 11, 8),
        True,
        "westminster",
        "walk-in-cold-rooms",
        "New walk-in built over two days between services with zero disruption. Temperature logger left running overnight and the report emailed the next morning. Exactly what we needed.",
    ),
    (
        "Kwame A.",
        "IT Manager",
        "Law firm, City of London",
        5,
        ReviewSource.GOOGLE,
        date(2025, 8, 30),
        False,
        "city-of-london",
        "split-systems",
        "Duty/standby cooling for our comms room with automatic changeover. Clear explanation, tidy install, and the monitoring alerts have already caught one fault before it mattered.",
    ),
    (
        "Sarah B.",
        "Pharmacy Manager",
        "Pharmacy group, Southwark",
        5,
        ReviewSource.GOOGLE,
        date(2025, 1, 17),
        False,
        "southwark",
        "planned-preventative-maintenance",
        "Vaccine fridges and cold room serviced on schedule with the temperature records our inspector asked for. Responsive on the phone and honest about what does and doesn't need doing.",
    ),
]

CASE_STUDIES = [
    {
        "slug": "walk-in-freezer-replacement-soho-restaurant-group",
        "title": "Walk-in freezer replacement for a Soho restaurant group",
        "client": "Dockside Dining Group",
        "anon": False,
        "sector": "restaurants",
        "area": "westminster",
        "services": ["freezer-rooms", "emergency-callout"],
        "scale": "3 kitchens, 1 central freezer",
        "completed": date(2025, 2, 20),
        "featured": True,
        "summary": "A failing 1990s freezer room feeding three restaurants was replaced in a 48-hour window without a single lost service.",
        "challenge": "The group's central production kitchen ran one ageing freezer room serving three Soho restaurants. The R404A plant was leaking, the floor had lifted, and each breakdown meant hiring a refrigerated trailer at short notice. A full replacement had been put off for two years because the kitchen could not close.",
        "solution": "We surveyed on a Monday, agreed a Sunday-to-Tuesday programme, and hired a temporary cold store for the changeover. The old room was stripped and a new 100 mm PIR freezer room with insulated floor, heated door frame and R449A remote condensing unit was built and commissioned inside the window. A high-temperature alarm now calls the head chef and our duty engineer.",
        "result": "Zero services lost. Energy monitoring over the first quarter showed a 31% reduction in refrigeration electricity against the old plant, and emergency callouts for the freezer dropped from six in the previous year to none. The group moved all three sites onto a PPM contract.",
        "testimonial": "Marie L.",
    },
    {
        "slug": "vrf-maintenance-canary-wharf-serviced-offices",
        "title": "Bringing 42 VRF indoor units back into F-Gas compliance",
        "client": "Meridian Offices",
        "anon": True,
        "anon_label": "A serviced-office operator in Canary Wharf",
        "sector": "offices",
        "area": "canary-wharf",
        "services": ["planned-preventative-maintenance", "air-conditioning-repairs"],
        "scale": "4 floors, 42 indoor units",
        "completed": date(2025, 4, 30),
        "featured": True,
        "summary": "An office operator inherited a VRF estate with no leak-check history. We audited every asset, repaired two leaks and put the building on a compliant PPM schedule.",
        "challenge": "A new building manager discovered that the previous contractor had left no F-Gas records for four floors of Daikin VRV. With a landlord audit approaching, the operator needed the estate surveyed, any leaks fixed and a defensible maintenance schedule — quickly, and without disturbing tenants.",
        "solution": "We tagged and logged all 42 indoor units and three outdoor systems, calculated CO₂-equivalent charge per circuit, and carried out electronic leak detection over two out-of-hours visits. Two leaking flare joints were repaired and recharged, coils and filters cleaned throughout, and a quarterly PPM schedule set with leak-check intervals matched to each circuit's charge.",
        "result": "The landlord audit passed with a complete asset register and leak-check log. Tenant comfort complaints fell from an average of nine a month to two over the following quarter, and the operator has since added a second building to the contract.",
        "testimonial": "Priya S.",
    },
    {
        "slug": "display-refrigeration-energy-upgrade-stratford-store",
        "title": "Glass-door retrofit cuts a convenience store's cabinet energy by 36%",
        "client": "Freshmarket Stores",
        "anon": False,
        "sector": "supermarkets",
        "area": "stratford",
        "services": ["display-refrigeration"],
        "scale": "14 display cabinets",
        "completed": date(2024, 10, 12),
        "featured": True,
        "summary": "Doors, EC fans and a condenser clean turned a struggling multideck line into the store's quietest, cheapest-to-run asset.",
        "challenge": "Fourteen open multideck cabinets on a remote pack were struggling to hold temperature on warm afternoons, and the store's electricity bill had risen sharply. The owner assumed the pack needed replacing.",
        "solution": "Inspection showed the pack was healthy but the condenser was heavily fouled and the cabinets were fighting a warm shop. We cleaned and pressure-washed the condenser, replaced the shaded-pole evaporator fans with EC motors, and fitted retrofit glass doors to all fourteen cabinets over two nights.",
        "result": "Sub-metered cabinet energy fell by 36% against the same month the previous year, product temperatures stabilised within the 1–4 °C band, and the pack's run hours dropped enough to defer replacement by an estimated five years. Payback on the retrofit is projected at 22 months.",
        "testimonial": "Tom H.",
    },
    {
        "slug": "duty-standby-cooling-city-law-firm-comms-room",
        "title": "Duty/standby cooling for a City law firm's comms room",
        "client": "A City of London law firm",
        "anon": True,
        "anon_label": "A City of London law firm",
        "sector": "data-centres",
        "area": "city-of-london",
        "services": ["split-systems"],
        "scale": "12 kW IT load",
        "completed": date(2025, 6, 6),
        "featured": False,
        "summary": "A single ageing wall unit was the only thing keeping a firm's servers cool. We replaced it with a monitored duty/standby pair.",
        "challenge": "The firm's comms room relied on one 7 kW wall-mounted split that had already failed twice, each time taking the practice management system offline. There was no alerting; the first sign of trouble was staff noticing the room was hot.",
        "solution": "We installed two 8 kW low-ambient ducted units with an automatic changeover controller that alternates duty weekly and brings the standby online on fault or high temperature. A temperature and fault relay now alerts both the IT manager and our duty engineer.",
        "result": "No cooling-related downtime since commissioning. The monitoring caught a condensate pump fault within weeks — the standby took over automatically and the repair was made during working hours without anyone in the office noticing.",
        "testimonial": "Kwame A.",
    },
]


def seed_sectors() -> None:
    """Sectors with key services."""
    services = {s.slug: s for s in Service.objects.all()}
    for order, (slug, name, icon, intro, keys) in enumerate(SECTORS):
        sector, _ = Sector.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "icon": icon,
                "intro": intro,
                "order": order,
                "status": PublishStatus.PUBLISHED,
                "hero_image_alt": f"{name} — placeholder image",
            },
        )
        attach(
            sector.hero_image,
            ph.scene_jpeg(f"sector-{slug}.jpg", seed=order + 40, start=ph.NAVY, end="#A7BFE8"),
        )
        sector.save()
        sector.key_services.set([services[k] for k in keys if k in services])


def seed_areas() -> None:
    """Borough and town landing pages."""
    for order, (slug, name, region, postcodes, response, intro) in enumerate(AREAS):
        ServiceArea.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "region": region,
                "postcode_prefixes": postcodes,
                "typical_response_time": response,
                "intro": intro,
                "order": order,
                "status": PublishStatus.PUBLISHED,
            },
        )


def seed_testimonials() -> None:
    """Reviews tagged to areas and services."""
    areas = {a.slug: a for a in ServiceArea.objects.all()}
    services = {s.slug: s for s in Service.objects.all()}
    for order, (
        author,
        role,
        company,
        rating,
        source,
        when,
        featured,
        area,
        service,
        quote,
    ) in enumerate(TESTIMONIALS):
        Testimonial.objects.update_or_create(
            author_name=author,
            company=company,
            defaults={
                "author_role": role,
                "rating": rating,
                "source": source,
                "date": when,
                "is_featured": featured,
                "area": areas.get(area),
                "service": services.get(service),
                "quote": quote,
                "order": order,
                "status": PublishStatus.PUBLISHED,
            },
        )


def seed_case_studies() -> None:
    """Case studies linked to sectors, areas, services and testimonials."""
    sectors = {s.slug: s for s in Sector.objects.all()}
    areas = {a.slug: a for a in ServiceArea.objects.all()}
    services = {s.slug: s for s in Service.objects.all()}
    reviews = {t.author_name: t for t in Testimonial.objects.all()}
    for order, data in enumerate(CASE_STUDIES):
        cs, _ = CaseStudy.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "client_name": data["client"],
                "client_anonymised": data["anon"],
                "anonymised_label": data.get("anon_label", ""),
                "sector": sectors[data["sector"]],
                "area": areas.get(data["area"]),
                "scale_metric": data["scale"],
                "summary": data["summary"],
                "challenge": data["challenge"],
                "solution": data["solution"],
                "result": data["result"],
                "completed_on": data["completed"],
                "is_featured": data["featured"],
                "testimonial": reviews.get(data["testimonial"]),
                "status": PublishStatus.PUBLISHED,
                "hero_image_alt": f"{data['title']} — placeholder image",
            },
        )
        attach(
            cs.hero_image,
            ph.scene_jpeg(
                f"case-{cs.slug[:40]}.jpg", seed=order + 60, end="#4A72C0", accent=ph.YELLOW
            ),
        )
        cs.save()
        cs.services.set([services[s] for s in data["services"] if s in services])
    # Related case studies on services
    for service in Service.objects.all():
        service.related_case_studies.set(CaseStudy.objects.filter(services=service)[:3])
