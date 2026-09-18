# Mehr Cool website — admin guide

This guide is for whoever looks after the website day to day. You do not need any technical
knowledge. Log in at **yourdomain/admin/** with the username and password you were given.

Every box in the admin has a short explanation underneath it. If you are unsure what a
field does, read the grey text under it. Changes go live the moment you press **Save**.

---

## The dashboard

When you log in you will see a box called **Where things live**. It links straight to the
places you will use most. Below it is the full list of sections.

| I want to… | Go to |
| --- | --- |
| Change the phone number, email, address or hours | **Site settings** |
| Change the homepage headline or video | **Site settings → Homepage hero** |
| Edit the menu or footer links | **Navigation** |
| Switch an accreditation logo on or off | **Accreditation badges** |
| Add a manufacturer or client logo | **Brands we service** / **Client logos** |
| Add or edit a service | **Services** |
| Add a case study | **Case studies** |
| Add a borough or town page | **Service areas** |
| Add a customer review | **Reviews** |
| See who has enquired or asked for a callback | **Emergency callbacks** / **Contact enquiries** |
| Edit About, Careers, legal pages | **Pages** |
| Change the options in a form dropdown | **Form dropdown options** |
| Redirect an old web address to a new one | **Redirects** |

---

## Change the phone number (or email, or address)

1. Click **Site settings**. It opens straight onto the settings form.
2. Under **Phone, WhatsApp & email**, change **Emergency phone**. This is the number every
   orange "Call" button dials, everywhere on the site.
3. Type it exactly as you want it to appear, for example `+44 77 7888 9080`. The site works
   out the tap-to-call link for you.
4. Press **Save**.

The same form holds the office number, the WhatsApp number and its pre-typed message, the
email address, the postal address and the map.

## Swap the hero video or picture

1. **Site settings → Homepage hero**.
2. **Hero poster** is the still image. It is shown instantly while the video loads, and it is
   what phones see instead of the video. Use a sharp photo, 1920 × 1080 pixels, under 250 KB.
3. **Hero video (MP4)** is the silent background clip. Keep it 10–20 seconds, 1920 × 1080, and
   under 8 MB. If you also have a WebM version, upload it to **Hero video (WebM)** — it is
   optional and only makes loading faster.
4. Change the **Hero headline**, the sentence under it and the two button labels in the same
   section.
5. Press **Save** and check the homepage.

## Change the words on the homepage

Almost every sentence on the homepage lives in **Site settings**:

- **Homepage hero** — headline, sub-headline, button labels.
- **Homepage sections** — the "What we do" heading and intro, the "Why choose us" heading and
  its four points, the "Recent work" and "What clients say" headings.
- **Call-to-action band** — the navy band at the bottom of most pages: heading, sentence and
  the tick-list beside the button.
- **Emergency strip** — the thin strip above the header.
- **Button labels & small headings** — the labels on the bottom-of-screen phone buttons, the
  footer contact heading, the QR card heading.

The three big tiles under the video (Repair / Maintenance / New installation) are under
**'I need…' tiles**.

## Add a service

1. **Services → Add service** (top right).
2. Pick the **Category** (Air Conditioning, Commercial Refrigeration or Emergency Services).
3. Type the **Name**. The **Slug** (web address) fills itself in — leave it.
4. Write a one-sentence **Short summary** (this appears on cards and in Google) and an
   **Intro** paragraph.
5. Upload a **Hero image** (1600 × 1000 pixels works best) and describe it in **Hero image alt**.
6. Under **Facts & proof** fill in the response time and price note if you want them shown,
   tick the brands you work with, and pick related services and case studies.
7. Add **Technical specifications** (label + value rows), **FAQs** (these also appear as
   questions in Google) and optional **Content blocks** for longer sections.
8. Set **Status** to **Published** and press **Save**. Use **Draft** while you are still writing.
9. Tick **Show this service in the homepage grid** if it should appear on the homepage.

Every service gets a **View on site** link at the top of its edit page.

## Publish a case study

1. **Case studies → Add case study**.
2. Fill in the **Title**, **Summary**, **Sector**, **Area** and the **Services** delivered.
3. Under **Client**, type the client's name. If you cannot name them, tick **Anonymise client**
   and give a label such as "A Mayfair boutique hotel".
4. Write the **Challenge**, **Solution** and **Result**. Numbers make results convincing:
   energy saved, downtime avoided, temperatures held.
5. Add a hero image and, if you have them, gallery photos with a short description of each.
6. Optionally attach a **Review** from the client and tick **Featured** to show it on the homepage.
7. Set **Status** to **Published** and **Save**.

## Add a borough or town page

Takes under a minute:

1. **Service areas → Add service area**.
2. Type the **Name** (e.g. "Greenwich"). The slug fills itself in.
3. Choose the **Region** so it sits in the right group on the Areas page.
4. Write two or three paragraphs in **Intro**: what kind of clients you have there, how long it
   takes to reach, any landmarks. Blank line = new paragraph.
5. Optionally add postcode prefixes ("SE10, SE3") and a local response time.
6. **Status → Published**, **Save**.

The page appears at `/areas/air-conditioning-refrigeration-greenwich/`, is added to the
sitemap automatically, and shows any case studies or reviews you have tagged with that area.
If there are none yet it shows your featured work instead.

## Add a review

**Reviews → Add review.** Type the reviewer's name, their role and company, the review text,
the star rating, where it was left (Google, Trustpilot, Checkatrade or directly) and the date.
Tick **Featured** to show it on the homepage. Tag an **Area** or **Service** so it appears on
those pages too.

The homepage rating summary is calculated from your published reviews. If your real Google
total is higher, enter it in **Site settings → Search engine defaults → Google review count**
and **Google rating** and those numbers will be used instead.

## Accreditations

Accreditation logos are **off by default** so the site never claims a certificate you do not
hold. When a certificate is issued:

1. **Accreditation badges** → open the badge (F-Gas, REFCOM, SafeContractor, CHAS, ISO 9001…).
2. Upload the official logo, add the certificate number and a link to the public register if
   there is one.
3. Tick **Is active**. It now appears in the trust strip, footer and call-to-action bands.
4. Only one badge should have **Show in header** ticked — normally F-Gas. That is the small
   mark next to the phone number in the sticky header.

## Menus and footer

**Navigation** lists every menu item. Each item has:

- **Label** — the words shown.
- **Caption** — optional. A short second line under the label, e.g. "Same-day repairs". Three
  or four words at most. It shows on wide screens and in the phone menu, and tucks away when
  the header shrinks as the visitor scrolls. Leave it blank and the menu item is a single line.
- **Icon** — optional. Pick from the same icon list used elsewhere; it sits to the left of the
  label and deepens from ice blue to navy when the visitor hovers over it.
- **Links to** — choose a service category, a service, a page, an area, or type a web address.
- **Parent** — leave blank for a top-level item, or pick a parent to put it in that item's
  dropdown (header) or column (footer).
- **Show in header / Show in footer** — where it appears.
- **Order** — lower numbers come first. You can edit order numbers directly in the list.

## Enquiries and emergency callbacks

**Emergency callbacks** and **Contact enquiries** list every form submission, newest first.
Each one is also emailed to the address in **Site settings → Lead notification email**.

- Change the **Status** (New → Contacted → Quoted → Won / Lost) directly in the list.
- Open a lead to add **Internal notes** — these are never shown to the customer.
- Tick several leads and choose **Export selected to CSV** to download a spreadsheet.

## Form dropdown options

The "What is this about?" and "What has failed?" dropdowns (and the quote wizard's options)
are lists you control. **Form dropdown options → Add**, choose which form field it belongs
to, type the label, **Save**. Untick **Is active** to hide an option without deleting it.

## Pages (About, legal, Careers)

**Pages** holds About, F-Gas compliance statement, Terms, Privacy, Cookies and Careers. Each
page is built from **Content blocks** — text, image + text, statistics, FAQ, call-to-action,
logo strip, video, gallery, feature grid. Add a block, choose its type and fill in only the
fields that apply.

**Writing text:** blank line = new paragraph; start a line with `- ` for a bullet; start a
line with `## ` for a sub-heading; wrap words in `**double stars**` for bold.

**Repeated items** (statistics, FAQs, feature grids) are typed one per line as
`Title :: Description`. For FAQs: `Question? :: Answer.`

Six pages with special names control the heading and intro of built-in pages and are not
shown on their own: `services`, `sectors`, `case-studies`, `areas`, `contact`,
`emergency-callout`. Edit them to change those headings.

## Search engine settings

Every service, page, case study, sector and area has a collapsed section called **Search
engine settings** at the bottom of its form. Leave it blank and the site writes sensible
titles and descriptions for you. Fill it in when you want to control exactly what Google shows.

Site-wide defaults (title suffix, default description, default sharing image) and your
Google Analytics / Tag Manager IDs are in **Site settings → Search engine defaults** and
**Analytics**.

## Redirects

If you rename a page, add a redirect so old links and Google results still work:
**Redirects → Add**, type the old path (`/old-page/`) and the new one (`/new-page/`).

## Users

Three kinds of user:

- **Superuser** — everything, including creating users.
- **Content Editor** group — pages, services, case studies, areas, reviews, badges, navigation, site settings.
- **Sales** group — enquiries and callbacks only.

To add a user: **Users → Add user**, set a username and password, **Save**, then tick
**Staff status** and add them to a group.

## If something looks wrong

- Changes not showing? Press **Ctrl/Cmd + Shift + R** to refresh without cache. The site
  caches the header and footer for 15 minutes.
- An image will not upload? Check the size guidance under the field. Images must be under 5 MB.
- The 500 error page still shows the phone number even if the database is down, so callers
  are never stranded.
