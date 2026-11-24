#!/usr/bin/env python3
"""Ninja Tables row data for the clone.

The live site loads every table through wp-admin/admin-ajax.php, which currently answers HTTP 403
(the tables render empty on production too). Rows below are restored from authentic official sources:
  * GATE 2024 Information Brochure (27 Sep 2023)  -> /wp-content/uploads/2023/09/GATE2024InformationBrochureSep27.pdf
  * text/headings published on gate2024.iisc.ac.in itself (homepage important dates, fee-table headers, page text)
Tables whose rows cannot be recovered from any accessible source get a single notice row.
"""
import json, datetime
from pathlib import Path
OUT = Path(__file__).resolve().parent / 'clone' / 'tables'
OUT.mkdir(parents=True, exist_ok=True)
BRO = '/wp-content/uploads/2023/09/GATE2024InformationBrochureSep27.pdf'
SRC_BRO = 'brochure'; SRC_SITE = 'site'

def rows(keys, data):
    return [{'options': {'classes': f'ninja_table_row_{i} nt_row_id_{i+1}'}, 'value': dict(zip(keys, r))} for i, r in enumerate(data)]
K3 = ['degree_program', 'qualifying_degree_examination', 'subject_marks']
K4 = ['degree_program', 'qualifying_degree_examination', 'subject_marks', 'total_marks']
KD = ['degree_program', 'qualifying_degree_examination', 'description_of_eligible_candidates']
def day(y, m, d): return datetime.date(y, m, d).strftime('%A')
T, META = {}, {}

# ---- Important dates (Activity / Day / Date)
T[1734] = rows(K3, [
    ['GATE Online Application Processing System (GOAPS) opens', day(2023,8,30), 'August 30, 2023'],
    ['Closing date of regular online registration/application', day(2023,10,12), 'October 12, 2023'],
    ['End of extended period for online registration/application (with late fee)', day(2023,10,20), 'October 20, 2023'],
    ['Last date for change of Category, Paper and Examination City, adding a new test paper, and change of personal details (additional fee applicable per change)', day(2023,11,11), 'November 11, 2023'],
    ['New two-paper combinations available for registered candidates', 'Saturday – Friday', 'November 11–17, 2023'],
    ['Admit Cards available for download', day(2024,1,3), 'January 3, 2024'],
    ['GATE 2024 Examination (Forenoon: 9:30 AM to 12:30 PM; Afternoon: 2:30 PM to 5:30 PM)', 'Saturday, Sunday, Saturday, Sunday', 'February 3, 4, 10 and 11, 2024'],
    ['Challenges/contests on question papers and answer keys', 'Thursday – Sunday', 'February 22–25, 2024'],
    ['Final answer keys published online', day(2024,3,14), 'March 14, 2024'],
    ['Announcement of results in GOAPS', day(2024,3,16), 'March 16, 2024'],
    ['Score Cards available for free download', '—', 'March 23, 2024 to May 31, 2024'],
    ['Statistical and performance report available', day(2024,5,31), 'May 31, 2024'],
    ['Score Cards available for download by paying a fee of Rs. 500 per test paper', '—', 'June 1, 2024 to December 31, 2024'],
]); META[1734] = SRC_BRO

# ---- Eligibility (brochure Table 2)
T[659] = rows(['degree_program','qualifying_degree_examination','description_of_eligible_candidates','expected_year_of_completion'], [
    ['B.E./B.Tech./B.Pharm.', 'Bachelor’s degree in Engineering / Technology (4 years after 10+2 or 3 years after B.Sc./Diploma in Engineering/Technology)', 'Currently in the 3rd year or higher or already completed', '—'],
    ['B. Arch.', 'Bachelor’s degree of Architecture (5-year course) / Naval Architecture (4-year course) / Planning (4-year course)', 'Currently in the 3rd year or higher or already completed', '—'],
    ['B.Sc. (Research)/B.S.', 'Bachelor’s degree in Science (Post-Diploma/4 years after 10+2)', 'Currently in the 3rd year or higher or already completed', '—'],
    ['Pharm. D. (after 10+2)', '6 years degree program, consisting of internship or residency training, during third year onwards', 'Currently in the 3rd/4th/5th/6th year or already completed', '—'],
    ['M.B.B.S./B.D.S./B.V.Sc.', 'Degree holders of M.B.B.S./B.D.S./B.V.Sc. and those who are in the 5th/6th/7th semester or higher semester of such program', '5th/6th/7th or higher semester or already completed', '—'],
    ['M.Sc./M.A./M.C.A. or equivalent', 'Master’s degree in any branch of Arts/Science/Mathematics/Statistics/Computer Applications or equivalent', 'Currently in the first year or higher or already completed', '—'],
    ['Int. M.E./M.Tech. (Post-B.Sc.)', 'Post-B.Sc Integrated Master’s degree programs in Engineering/Technology (4-year program)', 'Currently in the 1st/2nd/3rd/4th year or already completed', '—'],
    ['Int. M.E./M.Tech./M.Pharm. or Dual Degree (after Diploma or 10+2)', 'Integrated Master’s degree program or Dual Degree program in Engineering/Technology (5-year program)', 'Currently in the 3rd/4th/5th year or already completed', '—'],
    ['B.Sc./B.A./B.Com.', 'Bachelor’s degree in any branch of Science / Arts / Commerce (3-year program)', 'Currently in the 3rd year or already completed', '—'],
    ['Int. M.Sc./Int. B.S./M.S.', 'Integrated M.Sc. or 5-year integrated B.S.-M.S. program', 'Currently in the 3rd year or higher or already completed', '—'],
    ['Professional Society Examinations* (equivalent to B.E./B.Tech./B.Arch.)', 'B.E./B.Tech./B.Arch. equivalent examinations of Professional Societies, recognised by MoE/UPSC/AICTE (e.g. AMIE by Institution of Engineers-India, AMICE by the Institute of Civil Engineers-India and so on)', 'Completed Section A or equivalent of such professional courses', '—'],
    ['B.Sc. (Agriculture, Horticulture, Forestry)', '4-year program', 'Currently in the 3rd/4th year or already completed', '—'],
]); META[659] = SRC_BRO
# (The brochure has no "Expected Year of Completion" column, so that column is left as '—'.)

# ---- Test papers & codes (brochure Table 3); paper names link to the syllabus in the brochure
P = [('Aerospace Engineering','AE'),('Agricultural Engineering','AG'),('Architecture and Planning','AR'),('Biomedical Engineering','BM'),('Biotechnology','BT'),('Civil Engineering','CE'),('Chemical Engineering','CH'),('Computer Science and Information Technology','CS'),('Chemistry','CY'),('Data Science and Artificial Intelligence','DA'),('Electronics and Communication Engineering','EC'),('Electrical Engineering','EE'),('Environmental Science & Engineering','ES'),('Ecology and Evolution','EY'),('Geomatics Engineering','GE')]
Q = [('Geology and Geophysics','GG'),('Instrumentation Engineering','IN'),('Mathematics','MA'),('Mechanical Engineering','ME'),('Mining Engineering','MN'),('Metallurgical Engineering','MT'),('Naval Architecture and Marine Engineering','NM'),('Petroleum Engineering','PE'),('Physics','PH'),('Production and Industrial Engineering','PI'),('Statistics','ST'),('Textile Engineering and Fibre Science','TF'),('Engineering Sciences','XE'),('Humanities & Social Sciences','XH'),('Life Sciences','XL')]
def syl(name, code):
    href = '/wp-content/uploads/2023/08/GATE2024DataScienceAIsyllabus.pdf' if code == 'DA' else BRO
    return f'<a href="/{href.lstrip("/")}" target="_blank" rel="noopener">{name}</a>', f'<a href="/{href.lstrip("/")}" target="_blank" rel="noopener">{code}</a>'
T[933] = rows(K4, [list(syl(*a)) + list(syl(*b)) for a, b in zip(P, Q)]); META[933] = SRC_BRO
T[935] = rows(K4 + ['xe_paper_sections', 'code'], [
    ['Engineering Mathematics (Compulsory)', 'A', 'Reasoning and Comprehension (Compulsory)', 'B1', 'Chemistry (Compulsory)', 'P'],
    ['Fluid Mechanics', 'B', 'Economics', 'C1', 'Biochemistry', 'Q'],
    ['Materials Science', 'C', 'English', 'C2', 'Botany', 'R'],
    ['Solid Mechanics', 'D', 'Linguistics', 'C3', 'Microbiology', 'S'],
    ['Thermodynamics', 'E', 'Philosophy', 'C4', 'Zoology', 'T'],
    ['Polymer Science and Engineering', 'F', 'Psychology', 'C5', 'Food Technology', 'U'],
    ['Food Technology', 'G', 'Sociology', 'C6', '', ''],
    ['Atmospheric and Oceanic Sciences', 'H', '', '', '', ''],
]); META[935] = SRC_BRO

# ---- Two-paper combinations (brochure Table 4) -> table 860 (original combinations)
L = [('AE','CE, ME, XE'),('AG','CE'),('AR','CE, GE'),('BM','BT, IN'),('BT','BM, XL'),('CE','AE, AG, AR, ES, GE, NM, XE'),('CH','ES, PE, XE'),('CS','DA, EC, GE, MA, PH, ST'),('CY','XE, XL'),('DA','CS, EC, EE, MA, ME, PH, ST, XE'),('EC','CS, DA, EE, IN, PH'),('EE','DA, EC, IN, PH'),('ES','CE, CH, GE'),('EY','XL')]
R = [('GE','AR, CE, CS, ES, GG'),('GG','GE'),('IN','BM, EC, EE, ME'),('MA','CS, DA, PH, ST'),('ME','AE, DA, IN, NM, PI, XE'),('MT','XE'),('NM','CE, ME'),('PE','CH'),('PH','CS, DA, EC, EE, MA, XE'),('PI','ME, XE'),('ST','CS, DA, MA, XH'),('XE','AE, CE, CH, CY, DA, ME, MT, PH, PI'),('XH','ST'),('XL','BT, CY, EY')]
T[860] = rows(['degree_program','qualifying_degree_examination','description_of_eligible_candidates','codes_of_papers_allowed_as_the_second_paper'], [[a[0],a[1],b[0],b[1]] for a,b in zip(L,R)]); META[860] = SRC_BRO

# ---- Question paper pattern (brochure section 4 and Table 5)
T[901] = rows(['degree_program','qualifying_degree_examination'], [
    ['Mode of examination', 'Computer Based Test (CBT)'],
    ['Duration', '3 hours*'],
    ['Number of papers', '30 test papers'],
    ['Sections', 'General Aptitude (GA) + Candidate’s Selected Subject(s)'],
    ['Types of questions', '(a) Multiple Choice Questions (MCQ)<br>(b) Multiple Select Questions (MSQ)<br>(c) Numerical Answer Type (NAT)'],
    ['Test of abilities', '(a) Recall<br>(b) Comprehension<br>(c) Application<br>(d) Analysis and Synthesis'],
    ['Number of questions', '10 (General Aptitude) + 55 (Subject) = 65 Questions'],
    ['Distribution of marks in all papers except AR, CY, DA, EY, GG, MA, PH, ST, XH and XL', 'General Aptitude: 15 marks<br>Engineering Mathematics**: 13 marks<br>Subject Questions: 72 marks<br>Total: 100 marks<br>(**XE includes an Engineering Mathematics section XE-A of 15 marks)'],
    ['Distribution of marks in papers AR, CY, DA, EY, GG, MA, PH, ST, XH and XL', 'General Aptitude: 15 marks<br>Subject Questions: 85 marks<br>Total: 100 marks'],
    ['Marking scheme', 'Questions carry either 1 mark or 2 marks'],
    ['Negative marking', 'For a wrong answer to an MCQ, there will be negative marking. For a 1-mark MCQ, 1/3 will be deducted for a wrong answer. Likewise, for 2-mark MCQ, 2/3 will be deducted for a wrong answer.<br>There is no negative marking for wrong answers to MSQ and NAT questions.<br>There is no partial marking for any question.'],
]); META[901] = SRC_BRO
T[908] = rows(['degree_program','qualifying_degree_examination','compulsory_section','subject_marks','total_marks','total_time_minutes'], [
    ['AE, AG, BM, BT, CE, CH, CS, EC, EE, ES, IN, ME, MN, MT, NM, PE, PI, TF (subject marks include Engineering Mathematics, 13 marks)', '15', '85', '—', '100', '180'],
    ['CY, DA, EY, MA, PH, ST', '15', '85', '—', '100', '180'],
    ['AR: Part A common and compulsory; Part B1 (Architecture) / B2 (Planning) selected during the exam', '15', '60', '25', '100', '180'],
    ['GE: Part A common and compulsory; Part B1 (Surveying and Mapping) / B2 (Image Processing and Analysis) selected during the exam', '15', '55', '30', '100', '180'],
    ['GG: Part A common and compulsory; Part B1 (Geology) / B2 (Geophysics) chosen at the time of application', '15', '25', '60', '100', '180'],
    ['XE: Section A (Engineering Mathematics) compulsory; any TWO other sections chosen during the exam', '15', '15', '2 x 35', '100', '180'],
    ['XH: Section B1 (Reasoning and Comprehension) compulsory; any ONE other section chosen at the time of application', '15', '25', '60', '100', '180'],
    ['XL: Section P (Chemistry) compulsory; any TWO other sections chosen during the exam', '15', '25', '2 x 30', '100', '180'],
]); META[908] = SRC_BRO

# ---- Application fee (brochure Table 6 amounts; period headings are the site's own column titles)
T[876] = rows(KD, [
    ['Female / SC / ST / PwD* candidates', '₹ 900', '₹ 1400'],
    ['All other candidates including foreign nationals', '₹ 1800', '₹ 2300'],
]); META[876] = SRC_BRO

# ---- Zonal contacts (brochure Table 1)
T[691] = rows(['degree_program','qualifying_degree_examination','description_of_eligible_candidates','expected_year_of_completion'], [
    ['Zone-1 (Organising Institute)', 'IISc Bengaluru, Bengaluru - 560 012', '080-22932644<br>080-22933333', '<a href="mailto:helpdesk.gate@iisc.ac.in">helpdesk.gate@iisc.ac.in</a>'],
    ['Zone-2', 'IIT Bombay, Powai, Mumbai - 400 076', '022-25767068', '<a href="mailto:gateoffice@iitb.ac.in">gateoffice@iitb.ac.in</a>'],
    ['Zone-3', 'IIT Delhi, Hauz Khas, New Delhi - 110 016', '011-26591749', '<a href="mailto:gate@admin.iitd.ac.in">gate@admin.iitd.ac.in</a>'],
    ['Zone-4', 'IIT Guwahati, Guwahati - 781 039', '0361-2582751/2582755', '<a href="mailto:gate@iitg.ac.in">gate@iitg.ac.in</a>'],
    ['Zone-5', 'IIT Kanpur, Kanpur - 208 016', '0512-2597412/2596962/2596963', '<a href="mailto:gate@iitk.ac.in">gate@iitk.ac.in</a>'],
    ['Zone-6', 'IIT Kharagpur, Kharagpur - 721 302', '03222-282091/282095', '<a href="mailto:gateonline@adm.iitkgp.ac.in">gateonline@adm.iitkgp.ac.in</a>'],
    ['Zone-7', 'IIT Madras, Chennai - 600 036', '044-22578200', '<a href="mailto:gate@iitm.ac.in">gate@iitm.ac.in</a>'],
    ['Zone-8', 'IIT Roorkee, Roorkee - 247 667', '01332-284531', '<a href="mailto:gate@iitr.ac.in">gate@iitr.ac.in</a>'],
]); META[691] = SRC_BRO

# ---- Not recoverable: single notice row
NOTICE = ('Table data is not available: the original site loads this table from its table service, which currently '
          'returns HTTP 403 (it is empty on gate2024.iisc.ac.in as well). Please refer to the '
          '<a href="/download/">Download</a> page and the official '
          f'<a href="/{BRO.lstrip("/")}" target="_blank" rel="noopener">GATE 2024 Information Brochure (PDF)</a>.')
for tid in [716, 885, 2397, 2372, 2577, 1197, 1199, 1292, 1368, 1398, 1431, 1432, 1433, 1708, 1710, 1711, 1712, 1713, 1714, 1715, 1716, 1717]:
    T[tid] = rows(['degree_program'], [[NOTICE]]); META[tid] = 'unavailable'

for tid, data in T.items():
    (OUT / f'table-{tid}.json').write_text(json.dumps(data, ensure_ascii=False))
(OUT / 'meta.json').write_text(json.dumps({str(k): v for k, v in META.items()}))
print('tables written:', len(T), '| restored:', sum(v != 'unavailable' for v in META.values()))
