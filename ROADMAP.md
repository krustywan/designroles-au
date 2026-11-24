# Roadmap

What's next for DesignRoles AU. Tick items off as they ship; add new ones at the bottom of their section.

## First things after launch
- [ ] **Adzuna feed** for recruiter roles and the states that block GitHub (NSW, ACT, Tasmania). Adzuna's free developer key needs the site's public web address, so sign up once the board is live at its launch address, then add the app ID and key as GitHub secrets `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`. Its terms require a "Jobs by Adzuna" label on every role it supplies, with "Jobs" linking to Adzuna. Show only roles we don't already have direct from the employer, clearly marked.

## More sources
- [ ] Connectors still needed: WA Health jobs, Dayforce (QLD Country Bank), SBS, ReadyTech (currentjobs), UKG/Workforce Ready, Airswift
- [ ] Victorian Government jobs: blocked from GitHub's computers, needs an access request
- [ ] Employment Hero job board (Betashares, Merchantwise and other small employers post here). Its listing page can't be searched by keyword, so it needs a smarter connector
- [ ] Optus's own careers site (careers.optus.com.au) only shows 10 jobs per page with no search. Singtel's feed already gives us most Optus roles
- [ ] Salient Group and other recruiters whose sites don't publish a job feed
- [x] LiveHire / Humanforce careers pages (Super Retail Group brands), via a reusable "careers site" connector
- [x] ACER, Coates, Breville, Atari, Riot Games, Macquarie, Marsh McLennan, AustralianSuper
- [ ] Connector for the shared "Careers Site" platform (WA Gov, National Archives, Compass, Are Media, ASC, Michael Hill all use it), plus a scan for every Australian employer on it
- [x] APS Jobs (via the Public Service Gazette)
- [x] Queensland Government SmartJobs
- [x] IAG (via its Phenom careers site)
- [x] Large corporates: 205 checked, 100+ added (banks, insurers, telcos, retail, energy, consultancies)
- [ ] Ask the ~25 employers that block automated tools for access (Canva's site, AGL, AustralianSuper, Bunnings, Monash and others)
- [x] NSW Government agencies (via nswconnect, Cornerstone), ELMO Talent, WordPress/Refari recruiter boards
- [ ] Connectors for Taleo, LiveHire, Dayforce, Teamtailor, NGA (RACQ, Healthscope, Hostplus, Sydney Water, ECU)
- [ ] Ask the Victorian Government for access (its jobs site blocks GitHub's computers)
- [x] South Australian and Northern Territory Government job boards
- [x] Chemist Warehouse, EPA Victoria, DFFH's own job board, Law Institute of Victoria (BambooHR)
- [ ] NSW (iworkfor), ACT and Tasmanian Government boards: they block GitHub and this session, so they wait on Adzuna (above)

## Board
- [ ] Remember when each role was first seen, so "new this week" works
- [ ] Remove closed roles automatically
- [ ] Live email alerts (the sign-up form is a mock today)

## Quality
- [ ] AI tagging pass, with the keyword rules as a fallback
- [ ] Test with 10–20 designers and researchers; log what they find useful

## Next phase: job alerts
- [ ] Email alerts for a saved search (keywords, location and filters), daily or weekly
- [ ] Choose a mailing service (e.g. Buttondown, Resend or Mailchimp's free tier), with double opt-in and one-click unsubscribe
- [ ] Bring back the Job alerts page and the "Get roles like this by email" box on each role (both designed, removed for now)

## Growth: prove the board works
Measure success before building anything to earn money from it.
- [ ] Add privacy-friendly visitor analytics (no cookies, no personal data)
- [ ] Turn the email alert sign-up into real alerts, so subscribers can be counted
- [ ] Set the success targets: monthly visitors, alert subscribers, and clicks through to employers' ads
- [ ] Share with design and research communities; track growth for 2–3 months

## Revenue: recruiter feeds (only once the growth targets are met)
The likely revenue approach. Recruiters pay to reach a focused design and research audience.
- [ ] Apply to be listed as a job board in JobAdder and Broadbean, the tools recruiters use to post one ad to many boards
- [ ] Accept recruiter-posted roles with full ad text, pay and a direct link, badged "Via recruiter"
- [ ] Pitch design-specialist recruiters with the traffic and subscriber numbers
- [ ] Decide pricing (e.g. per post, monthly plan, or featured roles) and keep employer-sourced roles free

## Later: AI job summaries (consider once the board takes off)
- [ ] Turn on AI summaries of each ad: about the role, what you'll do, what they're looking for, perks. The code is already built (`summarise.py`) and switched off; it starts working as soon as an `ANTHROPIC_API_KEY` repository secret is added.
- Cost: about US$0.15–0.20 a month at today's volume (Claude Haiku 5.5, each role summarised once and reused). Set a monthly spend limit in the Anthropic Console before turning it on.
- Revisit alongside revenue: e.g. as part of a paid tier, sponsored listings, or covered by recruiter-feed income once the growth targets are met.

## Done
- [x] Prototype scraper and board
- [x] Every role links to its original ad
- [x] Daily run on GitHub Actions, published with GitHub Pages

## Sites that block GitHub (saved copies)
Some job sites block GitHub's computers, where the daily update runs. For these, a `*_refresh.py` script saves a copy
of the roles from a computer the site lets in, and the daily update uses that copy when the live site refuses it
(skipping roles past their closing date). A weekly scheduled task runs every `*_refresh.py` and commits the results.
- Victorian Government (careers.vic.gov.au): `vic_refresh.py` → `vic_cache.json`
- To add another: write `<name>_refresh.py` and a fallback in the connector, following the Victorian one.
