from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'downloads'
OUT.mkdir(parents=True, exist_ok=True)

BRAND = HexColor('#163A33')
BRAND2 = HexColor('#255C50')
CREAM = HexColor('#FBFAF6')
INK = HexColor('#18312C')
MUTED = HexColor('#5F706B')
LINE = HexColor('#D7E1DC')

TRACKERS = [
    dict(filename='diabetic-cat-tracker.pdf', species='CAT', title='Feline Diabetes Tracker', subtitle='Daily glucose, insulin, meals, water and behavior notes', fields=['Time','Glucose*','Insulin given','Food/appetite','Water','Urination','Behavior / notes'], summary=['Weight','Appetite trend','Thirst/urination trend','Energy/activity','Glucose pattern to discuss','Insulin doses missed/changed only per vet','Vomiting/diarrhea','Questions for veterinarian']),
    dict(filename='ckd-cat-tracker.pdf', species='CAT', title='Chronic Kidney Disease Tracker', subtitle='Hydration, appetite, weight, litter box and medication notes', fields=['Time','Food/appetite','Water','Urination','Weight*','Medication/fluids*','Energy / notes'], summary=['Weight trend','Appetite trend','Water intake trend','Urination changes','Vomiting/nausea signs','Energy/grooming','Home fluids/medications recorded','Blood pressure/lab questions']),
    dict(filename='hyperthyroid-cat-tracker.pdf', species='CAT', title='Hyperthyroidism Tracker', subtitle='Weight, appetite, thirst, activity, GI and treatment notes', fields=['Time','Food/appetite','Water','Urination','Weight*','Activity/behavior','Vomiting/stool / notes'], summary=['Weight trend','Appetite trend','Thirst/urination trend','Activity/restlessness','Vomiting/diarrhea','Coat/grooming changes','Medication/treatment notes','T4/BP/kidney questions']),
    dict(filename='feline-asthma-tracker.pdf', species='CAT', title='Feline Asthma Tracker', subtitle='Cough, wheeze, breathing effort, possible triggers and medication use', fields=['Time','Cough/wheeze','Breaths/min*','Breathing effort','Possible trigger','Medication*','Episode / notes'], summary=['Episode frequency','Cough/wheeze trend','Resting breathing trend','Breathing effort changes','Possible trigger patterns','Medication use recorded','Activity tolerance','Questions for veterinarian']),
    dict(filename='cat-arthritis-mobility-tracker.pdf', species='CAT', title='Arthritis & Mobility Tracker', subtitle='Jumping, stairs, litter access, grooming, activity and comfort', fields=['Time','Getting up','Jumping','Stairs','Litter access','Grooming','Activity / comfort'], summary=['Jumping ability','Stair use','Litter box access','Grooming reach','Play/activity','Sleep/rest comfort','Slip/fall events','Pain/mobility questions']),
    dict(filename='cat-heart-disease-tracker.pdf', species='CAT', title='Heart Disease Tracker', subtitle='Resting breathing, activity, appetite, weakness and medication notes', fields=['Time','Breaths/min*','Breathing effort','Activity','Appetite','Medication*','Weakness / notes'], summary=['Resting respiratory trend','Breathing effort changes','Activity tolerance','Appetite/weight','Weakness/collapse events','Medication doses recorded','Sleep/rest changes','Cardiology questions']),
    dict(filename='cat-hypertension-tracker.pdf', species='CAT', title='Hypertension Tracker', subtitle='Vet-directed blood pressure, vision, behavior, appetite and medication notes', fields=['Time','BP reading*','Medication*','Vision changes','Behavior','Appetite','Balance / notes'], summary=['Vet-directed BP readings','Vision changes','Disorientation/behavior','Balance/weakness','Appetite/weight','Medication doses recorded','Kidney/thyroid notes','Questions for veterinarian']),
    dict(filename='cat-chronic-gi-ibd-tracker.pdf', species='CAT', title='Chronic GI / IBD Tracker', subtitle='Meals, vomiting, stool, appetite, weight and medication notes', fields=['Time','Food/appetite','Vomiting','Stool','Weight*','Medication*','Energy / notes'], summary=['Appetite trend','Weight trend','Vomiting frequency','Stool consistency/frequency','Blood/mucus observed','Energy/activity','Diet/medication notes','Questions for veterinarian']),
    dict(filename='cat-seizure-tracker.pdf', species='CAT', title='Seizure Episode Tracker', subtitle='Episode timing, duration, recovery and medication record', fields=['Date/time','Duration','What happened','Recovery time','Possible trigger','Medication*','Post-event notes'], summary=['Episode count','Longest duration','Cluster pattern','Recovery changes','Possible trigger pattern','Medication doses recorded','Behavior between events','Neurology questions']),
    dict(filename='cat-cancer-supportive-care-tracker.pdf', species='CAT', title='Cancer & Supportive Care Tracker', subtitle='Comfort, appetite, hydration, mobility, medication and good-day notes', fields=['Time','Comfort','Food/appetite','Water','Mobility','Medication*','Good day? / notes'], summary=['Good days vs hard days','Comfort/pain changes','Appetite/weight','Hydration','Mobility/toileting','Sleep/rest','Medication effects','Quality-of-life questions']),
    dict(filename='dog-diabetes-tracker.pdf', species='DOG', title='Canine Diabetes Tracker', subtitle='Glucose, insulin, meals, water, urination and activity notes', fields=['Time','Glucose*','Insulin given','Food/appetite','Water','Urination','Activity / notes'], summary=['Weight trend','Appetite trend','Thirst/urination trend','Energy/activity','Glucose pattern to discuss','Insulin doses recorded','Eye/vision changes','Questions for veterinarian']),
    dict(filename='dog-ckd-tracker.pdf', species='DOG', title='Canine Chronic Kidney Disease Tracker', subtitle='Water, urination, appetite, weight, GI and medication notes', fields=['Time','Food/appetite','Water','Urination','Weight*','Medication/fluids*','GI / energy notes'], summary=['Weight trend','Appetite trend','Water intake trend','Urination changes','Vomiting/diarrhea','Hydration concerns','Medication/fluids recorded','Lab/BP questions']),
    dict(filename='dog-arthritis-mobility-tracker.pdf', species='DOG', title='Arthritis & Mobility Tracker', subtitle='Getting up, stairs, walks, play, slips and comfort', fields=['Time','Getting up','Stairs','Walk tolerance','Play/activity','Slip/fall','Comfort / notes'], summary=['Getting up after rest','Stair ability','Walk duration/tolerance','Play/activity','Limping/stiffness','Slip/fall events','Weight trend','Pain/mobility questions']),
    dict(filename='dog-heart-disease-tracker.pdf', species='DOG', title='Heart Disease Tracker', subtitle='Resting breathing, cough, activity, appetite and medication notes', fields=['Time','Breaths/min*','Cough','Breathing effort','Activity','Medication*','Appetite / notes'], summary=['Resting respiratory trend','Cough frequency','Breathing effort changes','Exercise tolerance','Weakness/collapse','Appetite/weight','Medication doses recorded','Cardiology questions']),
    dict(filename='dog-cushings-tracker.pdf', species='DOG', title="Cushing's Syndrome Tracker", subtitle='Thirst, urination, appetite, panting, skin/coat and medication notes', fields=['Time','Water','Urination','Appetite','Panting','Skin/coat','Medication* / notes'], summary=['Thirst trend','Urination/accidents','Appetite trend','Panting','Activity/weakness','Skin/coat changes','Medication doses recorded','Monitoring-test questions']),
    dict(filename='dog-hypothyroidism-tracker.pdf', species='DOG', title='Hypothyroidism Tracker', subtitle='Energy, weight, exercise tolerance, skin/coat and medication notes', fields=['Time','Energy','Exercise','Food/appetite','Weight*','Skin/coat','Medication* / notes'], summary=['Energy/mentation','Exercise tolerance','Weight trend','Appetite','Skin/coat changes','Cold seeking/comfort','Medication doses recorded','Thyroid-test questions']),
    dict(filename='dog-seizure-epilepsy-tracker.pdf', species='DOG', title='Seizure / Epilepsy Tracker', subtitle='Date, duration, severity, recovery, possible triggers and medication record', fields=['Date/time','Duration','Severity','What happened','Recovery','Possible trigger','Medication* / notes'], summary=['Episode count','Longest duration','Cluster pattern','Severity trend','Recovery changes','Possible trigger pattern','Medication doses recorded','Neurology questions']),
    dict(filename='dog-allergy-skin-tracker.pdf', species='DOG', title='Allergy & Skin Tracker', subtitle='Itch, licking, skin, ears, paws, possible exposures and treatment notes', fields=['Time','Itch 0-10','Licking','Skin','Ears/paws','Possible exposure','Treatment* / notes'], summary=['Itch trend','Licking/chewing','Skin redness/lesions','Ear changes','Paw changes','Possible flare factors','Bath/treatment notes','Dermatology questions']),
    dict(filename='dog-chronic-gi-tracker.pdf', species='DOG', title='Chronic GI Tracker', subtitle='Meals, vomiting, stool, appetite, weight and medication notes', fields=['Time','Food/appetite','Vomiting','Stool','Weight*','Medication*','Energy / notes'], summary=['Appetite trend','Weight trend','Vomiting frequency','Stool consistency/frequency','Blood/mucus observed','Energy/activity','Diet/medication notes','Questions for veterinarian']),
    dict(filename='dog-cancer-supportive-care-tracker.pdf', species='DOG', title='Cancer & Supportive Care Tracker', subtitle='Comfort, appetite, hydration, mobility, medication and good-day notes', fields=['Time','Comfort','Food/appetite','Water','Mobility','Medication*','Good day? / notes'], summary=['Good days vs hard days','Comfort/pain changes','Appetite/weight','Hydration','Mobility/toileting','Sleep/rest','Medication effects','Quality-of-life questions']),
    dict(filename='universal-medication-appointment-planner.pdf', species='ALL PETS', title='Medication & Appointment Planner', subtitle='A simple record to bring to every veterinary visit', fields=['Date/time','Medication','Dose given*','Food relation','Observed effect','Refill needed?','Notes'], summary=['Current medications','Supplements','Missed doses','Side effects/changes','Upcoming refills','Next appointment','Labs/tests requested','Questions for veterinarian']),
    dict(filename='universal-quality-of-life-tracker.pdf', species='ALL PETS', title='Daily Quality-of-Life Tracker', subtitle='Track comfort, function, engagement and good days over time', fields=['Date','Comfort','Appetite','Hydration','Mobility','Engagement','Good day? / notes'], summary=['Good days vs hard days','Comfort/pain','Eating/drinking','Mobility/toileting','Sleep/rest','Social engagement','Favorite activities','Questions/goals of care']),
]

def wrap_text(text, font, size, max_width):
    words = text.split(); lines, current = [], ''
    for word in words:
        test = word if not current else current + ' ' + word
        if stringWidth(test, font, size) <= max_width: current = test
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines

def header(c, species, title, subtitle, page):
    w, h = letter
    c.setFillColor(CREAM); c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setFillColor(BRAND); c.rect(0, h-88, w, 88, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 10); c.drawString(36, h-30, 'STEADY PAWS')
    c.setFillColor(HexColor('#D7E9E2')); c.setFont('Helvetica-Bold', 8); c.drawRightString(w-36, h-30, species)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 21); c.drawString(36, h-56, title)
    c.setFillColor(HexColor('#D7E9E2')); c.setFont('Helvetica', 8.7); c.drawString(36, h-73, subtitle)
    c.setFillColor(MUTED); c.setFont('Helvetica', 7.5); c.drawRightString(w-36, 20, f'Page {page} | steadypaws.netlify.app')

def disclaimer(c):
    w, _ = letter; y = 45
    c.setFillColor(HexColor('#FFF5DF')); c.roundRect(36, y, w-72, 35, 6, stroke=0, fill=1)
    c.setFillColor(HexColor('#5B513C')); c.setFont('Helvetica', 6.9)
    message = 'Organizational tool only - not diagnosis or treatment. Record only measurements your veterinary team asks you to collect. Contact a veterinarian for concerning or urgent changes.'
    for i, line in enumerate(wrap_text(message, 'Helvetica', 6.9, w-94)[:2]): c.drawString(47, y+22-(i*10), line)

def draw_identity(c):
    w, h = letter; y = h - 116
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 8)
    for label, x, width in [('Pet name',36,180),('Week of',225,130),('Veterinarian',365,211)]:
        c.drawString(x, y, label); c.setStrokeColor(LINE); c.line(x, y-13, x+width, y-13)

def draw_daily_table(c, fields):
    w, h = letter; x0, y_top, table_w, row_h = 36, h-158, w-72, 42
    weights = [0.95] + [1]*(len(fields)-2) + [1.5]; total = sum(weights); widths = [table_w*weight/total for weight in weights]
    c.setFillColor(BRAND); c.roundRect(x0, y_top-24, table_w, 24, 5, stroke=0, fill=1)
    x = x0; c.setFillColor(white); c.setFont('Helvetica-Bold', 6.8)
    for field, width in zip(fields, widths):
        lines = wrap_text(field, 'Helvetica-Bold', 6.8, width-6); c.drawCentredString(x+width/2, y_top-10, lines[0])
        if len(lines) > 1: c.drawCentredString(x+width/2, y_top-19, lines[1])
        x += width
    c.setStrokeColor(LINE); c.setLineWidth(.6); y = y_top-24
    for row in range(11):
        y2 = y-row_h; c.setFillColor(white if row%2 == 0 else HexColor('#F6F8F7')); c.rect(x0, y2, table_w, row_h, stroke=0, fill=1)
        c.setStrokeColor(LINE); c.line(x0, y2, x0+table_w, y2); x = x0
        for width in widths[:-1]: x += width; c.line(x, y2, x, y2+row_h)
        y = y2
    c.rect(x0, y_top-24-row_h*11, table_w, row_h*11+24, stroke=1, fill=0)

def draw_summary(c, items):
    w, h = letter; x0, y = 36, h-135
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 16); c.drawString(x0, y, 'Weekly summary')
    c.setFillColor(MUTED); c.setFont('Helvetica', 8.5); c.drawString(x0, y-18, 'Use patterns and notes to make the next veterinary conversation easier.'); y -= 52
    for index, item in enumerate(items):
        col, row = index%2, index//2; x, yy = x0+col*270, y-row*58
        c.setStrokeColor(BRAND2); c.setLineWidth(1); c.roundRect(x, yy-11, 12, 12, 2, stroke=1, fill=0)
        c.setFillColor(INK); c.setFont('Helvetica-Bold', 8); c.drawString(x+20, yy-3, item); c.setStrokeColor(LINE); c.line(x+20, yy-17, x+245, yy-17); c.line(x+20, yy-30, x+245, yy-30)
    y2 = y-4*58-18; c.setFillColor(INK); c.setFont('Helvetica-Bold', 10); c.drawString(x0, y2, 'Changes since last visit'); c.setStrokeColor(LINE)
    for i in range(3): c.line(x0, y2-18-i*22, w-36, y2-18-i*22)
    y3 = y2-92; c.setFillColor(INK); c.setFont('Helvetica-Bold', 10); c.drawString(x0, y3, 'Questions for the veterinary team')
    for i in range(4): c.line(x0, y3-18-i*22, w-36, y3-18-i*22)
    y4 = y3-118; c.setFillColor(INK); c.setFont('Helvetica-Bold', 10); c.drawString(x0, y4, 'Veterinarian plan / next steps')
    for i in range(3): c.line(x0, y4-18-i*22, w-36, y4-18-i*22)

def make_pdf(spec):
    path = OUT/spec['filename']; c = canvas.Canvas(str(path), pagesize=letter, pageCompression=1); c.setTitle(spec['title']); c.setAuthor('Steady Paws')
    header(c, spec['species'], spec['title'], spec['subtitle'], 1); draw_identity(c); draw_daily_table(c, spec['fields']); disclaimer(c); c.showPage()
    header(c, spec['species'], spec['title'], 'Weekly summary and veterinary appointment prep', 2); draw_summary(c, spec['summary']); disclaimer(c); c.save(); return path

if __name__ == '__main__':
    for spec in TRACKERS: print(make_pdf(spec))
    print('COUNT', len(TRACKERS))
