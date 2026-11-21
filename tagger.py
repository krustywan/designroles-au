"""Rule-based tagging: discipline, seniority, leadership, location, work mode, pay, recruiter flag.

Free to run on every scrape. An AI pass can later replace or check these rules.
"""
import re

# ---------- Discipline ----------
# Order matters: first match on the TITLE wins. Description is only used to break ties.
DISCIPLINES = [
    ("Research", r"\b(ux|user|design|customer|experience|product|usability|qualitative|mixed[- ]methods)\s+research(er)?\b|research\s*ops|research operations|researchops|\buxr\b|research (lead|manager|designer)|research enablement|survey insights|behaviou?ral scien|human factors|customer listening|voice of (the )?customer"),
    ("Service, strategy & CX", r"service design|business design|design strateg|strategic design|\bcx\b|customer experience|human[- ]cent(red|ered)|\bhcd\b|innovation design|experience strateg|journey (design|manager|lead|specialist)|co-?design|design thinking|cx analyst|customer experience analyst|experience improvement|service improvement|customer strateg|proposition (design|lead|manager)|product discovery|engagement strateg|venture (lead|design)|inclusive (products?|design)"),
    ("Content", r"content design|content op(eration)?s\b|contentops|ux writ|content strateg|conversation(al)? design|copywriter.*(ux|product)|ux copy"),
    ("Systems & DesignOps", r"design system|designops|design ops|design operations|design technologist|design engineer|ui engineer.*design"),
    ("Leadership", r"head of (design|ux|user research|design research|ux research|experience|cx|product design|service design)|design (director|manager)|director.*(design|experience)|(ux|cx|research|experience design|product design|service design|content design) (manager|director)|chief design|vp.*design"),
    ("UX, UI & product", r"\bux\b|\bui\b|experience architect|user experience|user interface|product design|interaction design|experience design|digital design|web design|app design|\bixd\b|\bdx\b|usability|accessibility (designer|specialist|lead)"),
    ("Visual & brand", r"visual design|graphic design|brand design|motion design|illustrat|creative (lead|director|designer)|digital designer|multimedia design|presentation design|art director|communications? design|designer|design lead"),
]
DISC_RE = [(name, re.compile(p, re.I)) for name, p in DISCIPLINES]

# Titles that contain design words but are NOT design/research roles we want.
EXCLUDE = re.compile(
    r"interior|(?<!experience )(?<!information )architect|instructional|learning (experience )?design|curriculum|"
    r"engineer(?!.*design system)|solution design|network design|electrical|mechanical|civil|structural|hydraulic|"
    r"landscape|fashion|textile|kitchen|joinery|drafting|draftsperson|cad\b|bim\b|"
    r"clinical|research (fellow|assistant|associate|officer|scientist|nurse|coordinator|technician|engineer|analyst)|"
    r"postdoc|lecturer|professor|phd|academic|scientist|laboratory|trial|"
    r"market research|data|analyst|sales|account (manager|executive)|recruit|talent|payroll|finance|"
    r"game design|level design|sound design|lighting|set design|costume|"
    r"assessment design|program design|policy design|course design|"
    r"customer experience (officer|consultant|representative|specialist|agent|associate|advisor|team member)|"
    r"call cent|contact cent|customer service|store|retail assistant|cashier|nurse|teacher|"
    r"business analyst|product owner|product manager|marketing manager|marketing coordinator|"
    r"insights? (analyst|manager)|software|developer|devops|qa |tester|security",
    re.I,
)
# A few strong design terms override the exclusion (e.g. "UX Engineer" is a design-adjacent role we keep).
OVERRIDE = re.compile(r"(cx|customer experience)\s*(&|and)\s*insights?|cx analyst|customer experience analyst|survey insights|research enablement|research op|behaviou?ral scien|experience architect|\bux\b|user experience|service design|product design|content design|content op(eration)?s\b|contentops|design system|ux research|user research", re.I)


HARD_EXCLUDE = re.compile(r"cyber ?cx|supervisor|integrity|ethics|grants?\b|teacher|classroom|lecturer|tutor|venue|\(wood\)|\(metal\)|school|kindergarten|early childhood|csa \||design manager - |design coordinator - |civil|drainage|\brail\b|\broad\b|\bbridge\b|tunnel", re.I)
NON_DIGITAL = re.compile(r"garment|apparel|fashion|homewares|soft home|hard home|interior design|architectural (design|drafting|documentation)|building design|cad draft|technical cad|furniture|kitchen|landscape|joinery|packaging design|textile|footwear|jewell?ery|print designer|millinery|tech pack", re.I)


def discipline(title, desc=""):
    t = title or ""
    if HARD_EXCLUDE.search(t):
        return None
    if EXCLUDE.search(t) and not OVERRIDE.search(t):
        return None
    if not OVERRIDE.search(t) and len(NON_DIGITAL.findall(desc or "")) >= 2:
        return None
    for name, rx in DISC_RE:
        if rx.search(t):
            # A generic "Designer" title: use the description to pick a better discipline.
            if name == "Visual & brand" and re.fullmatch(r"(senior |junior |lead |principal )?(designer|design lead)", t.strip(), re.I):
                for n2, rx2 in DISC_RE[:-1]:
                    if len(rx2.findall(desc or "")) >= 3:
                        return n2
            return name
    # Research titles that are generic ("Researcher") count only if the description is about UX/design research.
    if re.search(r"\bresearcher\b", t, re.I) and re.search(r"user research|ux research|design research|usability", desc or "", re.I):
        return "Research"
    return None


# ---------- Seniority & leadership ----------
def seniority(title, desc=""):
    t = (title or "").lower()
    if re.search(r"\b(head of|director|chief|vp|vice president|general manager)\b", t):
        return "Head / Director"
    if re.search(r"\b(lead|leader|principal|staff|manager)\b", t):
        return "Lead / Principal"
    if re.search(r"\b(senior|snr|sr\.?)\b", t):
        return "Senior"
    if re.search(r"\b(graduate|grad|intern|internship|entry|cadet|trainee|apprentice)\b", t):
        return "Graduate / Intern"
    if re.search(r"\b(junior|jnr|jr\.?|associate|assistant)\b", t):
        return "Junior"
    m = re.search(r"(\d{1,2})\+?\s*(?:-\s*\d+\s*)?years", desc or "", re.I)
    if m:
        y = int(m.group(1))
        if y >= 7:
            return "Senior"
        if y <= 2:
            return "Junior"
    return "Mid"


def people_leader(title, desc=""):
    t = (title or "").lower()
    if re.search(r"\b(head of|director|manager|chief)\b", t):
        return True
    if re.search(r"direct reports|manage a team of|lead a team of|people leader|line manage", desc or "", re.I):
        return True
    return False


# ---------- Location ----------
STATES = {
    "NSW": r"\bnsw\b|new south wales|sydney|parramatta|newcastle|wollongong|north sydney|macquarie park|gadigal",
    "VIC": r"\bvic\b|victoria(?!n era)|melbourne|geelong|ballarat|bendigo|bundoora|burwood|docklands|wurundjeri",
    "QLD": r"\bqld\b|queensland|brisbane|gold coast|sunshine coast|townsville|cairns|toowoomba",
    "WA": r"\bwa\b(?! state)|western australia|perth|fremantle|joondalup|bunbury|claremont|crawley|kimberley|pilbara|kalgoorlie|geraldton|albany",
    "SA": r"\bsa\b|south australia|adelaide|roseworthy|whyalla|urrbrae",
    "ACT": r"\bact\b|canberra|bruce\b|barton",
    "TAS": r"\btas\b|tasmania|hobart|launceston|burnie",
    "NT": r"\bnt\b|northern territory|darwin|alice springs",
}
STATES_RE = {k: re.compile(v, re.I) for k, v in STATES.items()}
AU_RE = re.compile(r"australia|\bau\b|\baus\b|" + "|".join(STATES.values()), re.I)
APAC_RE = re.compile(r"apac|asia[- ]pacific|anz\b|oceania|new zealand|worldwide|anywhere|global|remote \(.*(australia|apac|asia)", re.I)


def states_of(location):
    return [k for k, rx in STATES_RE.items() if rx.search(location or "")]


def in_scope_location(location, workplace, desc=""):
    """True if the role is in Australia, or remote and open to Australia/APAC."""
    loc = location or ""
    if AU_RE.search(loc):
        return True
    remote = re.search(r"remote", f"{loc} {workplace}", re.I)
    if remote and (APAC_RE.search(loc) or re.search(r"(based|located|living|reside) (in|within) australia|australia[- ]based|apac|australian time ?zone|aest", desc or "", re.I)):
        return True
    return False


def work_mode(location, workplace, desc=""):
    s = f"{workplace} {location}".lower()
    if "hybrid" in s:
        return "Hybrid"
    if "remote" in s:
        return "Remote"
    if re.search(r"on-?site|in[- ]office", s):
        return "Onsite"
    d = (desc or "").lower()
    if re.search(r"fully remote|100% remote|remote[- ]first|work from anywhere in australia|remote role", d):
        return "Remote"
    if re.search(r"hybrid|flexible working|work from home \d|days in (the )?office|\d days (in|from) (the )?office|wfh", d):
        return "Hybrid"
    return "Not stated"


# ---------- Employment type ----------
def employment(etype, title, desc=""):
    s = f"{etype} {title} {(desc or '')[:1500]}".lower()
    if re.search(r"day rate|daily rate|contract(or)?\b(?! of employment)|contract role|\d+[- ]month contract", s) and "permanent" not in (etype or "").lower():
        return "Contract"
    if re.search(r"non-ongoing|fixed[- ]term|max(imum)? term|\bftc\b|secondment|parental leave", s):
        return "Fixed term"
    if re.search(r"intern(ship)?\b|graduate program", s):
        return "Internship / Grad"
    if re.search(r"casual", s):
        return "Casual"
    if re.search(r"part[- ]time", f"{etype}".lower()):
        return "Part time"
    return "Permanent"


# ---------- Pay ----------
NUM = r"\$?\s?(\d{2,3}(?:[,\s]?\d{3})?(?:\.\d+)?)\s?(k|K)?"
PAY_RE = re.compile(
    r"(?:A?\$|AUD\s?)\s?(\d{1,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?\s?[kK]|\d{3,4})"
    r"(?:\s*(?:-|–|to)\s*(?:A?\$|AUD\s?)?\s?(\d{1,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?\s?[kK]|\d{3,4}))?"
    r"(\s*(?:per|p\.?\s?|/)\s*(?:annum|a\b|year|yr|day|hour|hr|d\b|h\b))?",
    re.I,
)


def _num(s):
    s = s.replace(",", "").replace(" ", "")
    if s.lower().endswith("k"):
        return float(s[:-1]) * 1000
    return float(s)


def pay(salary_text, desc=""):
    """Advertised pay only. Returns (min, max, period, display) or None."""
    for text in (salary_text or "", desc or ""):
        for m in PAY_RE.finditer(text):
            lo = _num(m.group(1))
            hi = _num(m.group(2)) if m.group(2) else lo
            per = (m.group(3) or "").lower()
            ctx = text[max(0, m.start() - 60): m.end() + 60].lower()
            if "super" in text[m.end(): m.end() + 3].lower():
                pass
            if re.search(r"day|/d\b|daily", per) or (300 <= lo <= 2500 and re.search(r"day|daily|p\.d", ctx)):
                period = "day"
            elif re.search(r"hour|hr|/h", per) or (25 <= lo < 300 and re.search(r"hour|hr|p\.h", ctx)):
                period = "hour"
            else:
                period = "year"
            if period == "year" and not (40000 <= lo <= 600000 and 40000 <= hi <= 700000):
                continue
            if period == "day" and not (250 <= lo <= 3000):
                continue
            if period == "hour" and not (25 <= lo <= 400):
                continue
            if hi < lo:
                lo, hi = hi, lo
            if period == "year":
                disp = f"${lo/1000:.0f}k" + (f" – ${hi/1000:.0f}k" if hi != lo else "")
            else:
                disp = f"${lo:,.0f}" + (f" – ${hi:,.0f}" if hi != lo else "") + f" per {period}"
            if "super" in ctx:
                disp += " + super" if "plus super" in ctx or "+ super" in ctx or "plus 1" in ctx or "+super" in ctx else ""
            return dict(min=lo, max=hi, period=period, display=disp)
    return None


# ---------- Recruiter ----------
RECRUITERS = re.compile(
    r"beacham|talent nation|hays|michael page|page personnel|robert walters|randstad|hudson|talent international|aurec|"
    r"paxus|peoplebank|chandler macleod|people2people|davidson|bluefin|talentweb|halcyon knights|"
    r"recruitment|recruiting|staffing|talent solutions|search partners|bespoke careers|experis|"
    r"jobgether|launch recruitment|the onset|digital talent|f5 recruitment|clicks it|greythorn|"
    r"sustainable talent|interpro|finite|ignite|beyond talent|sharp & carter|sharp and carter",
    re.I,
)


def via_recruiter(employer, desc=""):
    if RECRUITERS.search(employer or ""):
        return True
    if re.search(r"our client is|our client,|my client|on behalf of (our|a|an) client|we are partnering with|we're partnering with|recruitment agency|is partnering with a", (desc or "")[:2000], re.I):
        return True
    return False


def summary(desc, n=420):
    """A short, rule-based summary: prefer sentences about the role over the company intro."""
    d = re.sub(r"\s+", " ", desc or "").strip()
    d = re.sub(r"^(about (us|the company|the role)|who we are|the opportunity|the role)[:\s]*", "", d, flags=re.I)
    if len(d) <= n:
        return d
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", d)[:25]
    role = re.compile(r"\b(you will|you'll|you’ll|this role|the role|as (a|an|our)|we('re| are) (looking|seeking)|reporting to|responsible for|in this (role|position)|your role|join (our|the) [\w ]{0,30}team)\b", re.I)
    start = next((k for k, x in enumerate(sents) if role.search(x)), 0)
    out = ""
    for x in sents[start:]:
        if len(out) + len(x) > n and out:
            break
        out = (out + " " + x).strip()
    if len(out) > n:
        out = out[:n][: out[:n].rfind(" ")] + "…"
    return out
