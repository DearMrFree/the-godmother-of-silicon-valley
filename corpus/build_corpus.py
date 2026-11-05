#!/usr/bin/env python3
"""Merge hand-compiled records and recovered HuffPost columns into corpus.json and corpus.csv."""
import csv, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {}
exec(open(os.path.join(HERE, "entries_manual.py"), encoding="utf8").read(), ns)
E = ns["E"]
hp = json.load(open(os.path.join(HERE, "huffpost_raw.json"), encoding="utf8"))
# id: (date, topics, summary). Summaries are written for this archive from each column's title and standfirst.
S = {
"45158":("2007-04-21","journalism education,student press","The earliest column found: an alarm about shrinking high school journalism programs."),
"45577":("2007-04-29","aging,women","A reflection on the challenges of each stage of life, in HuffPost's Fearless Voices section."),
"64299":("2007-09-13","Google,space,innovation","Reports the launch of the Google Lunar XPrize, a precursor to her later moonshot language."),
"65381":("2007-09-21","teachers,TeachersCount","How designer Zac Posen and DHL backed a campaign to raise respect for teachers."),
"78842":("2007-12-31","science,policy,Stanford","Warns about cuts to American scientific research funding."),
"94031":("2008-03-29","open education,Creative Commons","Reports the push for free educational resources worldwide."),
"94418":("2008-04-03","open education,Wikipedia","Reports Wikipedia founder Jimmy Wales's support for open textbooks."),
"110039":("2008-07","school leadership,dropouts","Asks parents and teachers to press principals over the summer, citing high school dropout numbers."),
"111341":("2008-07-11","teachers,professional development","On a teacher gathering aimed at school transformation."),
"115144":("2008-07-26","startups,Stanford,Silicon Valley","Notes from the AlwaysOn summit at Stanford on promising digital companies."),
"121206":("2008-08-25","elections,student voice","What young people thought of the 2008 presidential candidates."),
"133927":("2008-10-12","student press,free speech,California law","Reports the signing of California's law protecting journalism teachers from retaliation."),
"138961":("2008-10-29","science,Silicon Valley","A lighter report on an airship's first US flight in San Francisco."),
"140106":("2008-11-06","youth,elections","What was worrying American teenagers at the moment of the 2008 election."),
"151244":("2008-12-15","testing,holidays","A holiday pick for students preparing for the SAT."),
"169793":("2009-02-25","science,open access,policy","Warns that a bill could restrict public access to medical research."),
"222071":("2009-06-28","failure,teaching","An early statement of an idea she keeps returning to: students need room to fail."),
"331257":("2009-10-23","teachers,No Child Left Behind","Argues that supporting teachers matters more than testing mandates."),
"333028":("2009-10-25","literacy,Sesame Workshop,Google","On a Sesame Workshop and Google forum about early literacy."),
"334111":("2009-10-26","dropouts,education policy","On urban dropout rates and what might solve them."),
"336221":("2009-10-27","Sesame Workshop,Google,education policy","A live forum on changing the system, with federal officials on the panel."),
"360382":("2009-11-19","teachers,open education","Weighs whether teachers should sell their lesson plans online."),
"366548":("2009-11-21","Creative Commons,open education","A year-end account of Creative Commons in 2009, from her position on the board."),
"371595":("2009-11-26","girls,global education,former students","On a former student's work to change girls' lives in Mozambique."),
"372111":("2009-11-27","economy,Silicon Valley","A first-person report from pre-dawn Black Friday shopping."),
"444680":("2010-02-04","Creative Commons,open education","Reports Catherine Casserly's election to the Creative Commons board."),
"539818":("2010-04-15","University of the People,higher education","Introduces a tuition-free online university."),
"577886":("2010-05-16","teachers,merit pay,research","Uses new research to argue against merit pay for teachers."),
"635630":("2010-07-09","digital literacy,education policy","Calls for schools to bring digital culture into literacy teaching."),
"654744":("2010-07-21","cyberbullying,safety","On protecting kids from around-the-clock online bullying."),
"706504":("2010-09-07","global education,teachers","Argues American students need a more global education."),
"748731":("2010-10-08","teachers unions,documentary,education policy","Her response to Waiting for Superman and its framing of teachers' unions."),
"773025":("2010-10-24","computational thinking,math,science","New teaching resources for computational thinking in math and science."),
"783105":("2010-11-13","global education,conference","Invites educators to a global online education conference."),
"835783":("2011-03-15","writing,National Writing Project,education policy","A plea to spare the National Writing Project from federal cuts."),
"858656":("2011-05-12","Google,reading,teachers","Shows teachers a new Google search filter by reading level."),
"871440":("2011-06","parenting,fathers","A Father's Day piece on the case for midlife fatherhood, drawing on author Len Filppu."),
"889559":("2011-07","teachers,American Dream","Connects the teacher-student relationship to economic opportunity."),
"977414":("2011-09-28","Lawrence Summers,education policy,conference","Reports Lawrence Summers's keynote at the New York Times Schools for Tomorrow conference."),
"1111905":("2011-11-24","gratitude,civic life","A Thanksgiving column urging a more optimistic national outlook."),
"1126931":("2011-12","White House,teachers","An account of attending a White House holiday party. The snapshot shows a January 2012 date."),
"1164430":("2011-12-22","documentary,education policy","Previews two new education documentaries coming in 2012."),
"1165072":("2011-12-22","Learning Matters,education reporting","On the value of Learning Matters and John Merrow's education reporting. She chaired its board."),
"1168585":("2011-12-24","University of the People,higher education","Recommends tuition-free university study as a holiday gift."),
"1246719":("2012-02-01","digital learning,technology","A guide to Digital Learning Day."),
"1320168":("2012-03-05","open education,OER","Invites readers to join Open Education Week."),
"1322948":("2012-03","open education,OER,search","New ways for teachers to search for open courseware."),
"1529499":("2012-05-19","TEDx,Stanford,design","Announces the free livestream of TEDxStanford."),
"1655925":("2012-07-07","Google,search literacy,online courses","Recommends a free Google course on searching the web."),
"1713477":("2012-07-28","open education,video","Reports the winners of the Why Open Education Matters video contest."),
"1742362":("2012-08-04","teachers,professional development","Calls educators to Connected Educators Month."),
"1905375":("2012-09-22","elections,civic education,student voice","Encourages K-12 teachers to involve students in the 2012 election."),
"3544951":("2013-07-04","student press,free speech,censorship","Compares restrictions on American high school journalists with censorship in China."),
"4161318":("2013-10-25","TRICK,teaching,trust","The earliest column found that spells out TRICK, about six years before her parenting book."),
"4475397":("2013-12-19","PISA,education policy,testing","Asks how US policymakers will respond to falling PISA scores."),
"4885097":("2014-03-02","data literacy,online courses","Recommends a self-paced course on making sense of data."),
"5697964":("2014-08-23","writing,teaching","Why writing is hard to teach and how to engage students in it."),
"6081316":("2014-10-31","teachers,tenure,education policy","A response to the Time magazine cover story on teacher tenure."),
"6125682":("2014-11-08","parenting,Amy Chua,debate","Announces her debate as Teacher Mom against Tiger Mom author Amy Chua."),
"6406728":("2015-01-02","computational thinking,toys","Recommends robots Dash and Dot for teaching computational thinking."),
"6554674":("2015-01-27","student mental health,corrections","A column on a student suicide, later retitled An Apology and Clarification."),
"6861346":("2015-03-13","digital learning,technology","A notice for Digital Learning Day 2015."),
"7796822":("2015-07-14","computational thinking,coding,parenting","Answers the parent's question of whether their child should learn to code."),
"8028052":("2015-08-23","moonshots,THNK,Amsterdam","On a bottom-up education innovation effort in Amsterdam."),
"8693100":("2015-12-01","empathy,global education,Global Lives Project","Argues that education systems must build empathy to break cycles of terror."),
"8811806":("2015-12-15","teachers,gratitude","A holiday reminder to thank teachers."),
"8812072":("2015-12-15","empathy,media arts,Global Lives Project","How media arts and the Global Lives Project can teach empathy."),
"9389674":("2016-03","women,girls,global education","Five actions for improving the lives of women and girls in 2016."),
}
seen=set()
for r in hp:
    i=r["slug"].split("_b_")[-1]
    if i in seen or not r["size"]: continue
    seen.add(i)
    d,t,su=S[i]
    title=re.sub(r"\s+-\s+(Business|Living|Politics|Media)\s+on\s+The Huffington Post$","",r["title"])
    title=re.sub(r"^(Fearless Voices|The Blog) \| Esther Wojcicki: ","",title).strip()
    E.append(dict(date=d,relation="by",type="Column",title=title,venue="The Huffington Post",
      url=f"https://web.archive.org/web/{r['capture']}/http://www.huffingtonpost.com/esther-wojcicki/{r['slug']}.html",
      status="listed",topics=t.split(","),summary=su))
later=[("2017-01-11","imagine-the-impossible-trust-in-the-classroom-the_b_5875fae8e4b065be6909907d","Imagine the Impossible: TRUST in the Classroom, the Key to Effective Teaching","trust,teaching","Argues that trust is the working foundation of effective teaching."),
("2017-01-11","to-all-students-learning-computational-thinking-will_b_57a15f7ee4b004301c522b7c","To All Students: Learning Computational Thinking Will Change Your Life","computational thinking,youth","Addressed to students, on why computational thinking is worth learning."),
("2017-09-12","how-to-give-all-students-moonshot-thinking-skills_b_59b7e984e4b0678066213e79","How to Give All Students Moonshot Thinking Skills","moonshots,student agency","On teaching every student to attempt ambitious, self-directed work."),
("2018-01-13","education-is-changing-reasons-to-be-optimistic-in_b_5a5a16ede4b0a233482e0b9e","Education is CHANGING, Reasons to be Optimistic in 2018","education policy,optimism","The most recent HuffPost column found.")]
for d,sl,ti,t,su in later:
    E.append(dict(date=d,relation="by",type="Column",title=ti,venue="The Huffington Post",url="https://www.huffpost.com/entry/"+sl,status="listed",topics=t.split(","),summary=su))
# Apply the source check. A record it covers counts as read unless the entry says otherwise.
vns = {}
exec(open(os.path.join(HERE, "verification.py"), encoding="utf8").read(), vns)
V = vns["V"]
pending = [e["url"] for e in E if e["status"] == "search" and e["url"] not in V]
assert not pending, pending
missing = [u for u in V if not any(e["url"] == u for e in E)]
assert not missing, missing
for e in E:
    e["note"] = ""; e["archive"] = ""
    if e["status"] == "search":
        change = {k: v for k, v in V[e["url"]].items() if v is not None}
        e["status"] = "opened"
        e.update(change)
E.sort(key=lambda e:(e["date"] or "0000",e["title"]),reverse=True)
for n,e in enumerate(sorted(E,key=lambda e:(e["date"] or "9999",e["title"])),1):
    e["id"]=f"WOJ-{n:04d}"
# Links that failed an automated check on 2026-11-04. Some may fail only for scripts.
BROKEN={"https://educators.brainpop.com/?p=19007","https://conf.nis.edu.kz/nis-conference/xii-conference/speakers/esther-wojcicki/?lang=en","http://time.com/superfamilies/","https://live.worldgovernmentsummit.org/events/2023/speaker-detail/0139e198-ac81-445f-ab16-09a516e73515esther-wojcicki","https://schedule.sxsw.com/2018/speakers/1937459","https://sxswedu.com/news/2019/featured-speakers-jessica-lahey-christopher-emdin-esther-wojcicki-more-announced/","https://symposium.org/speaker/50-st-gallen-symposium/william-stampfli-15/","https://www.edsurge.com/news/2013-02-20-the-trick-to-great-teaching","https://www.penguin.com.au/books/how-to-raise-successful-people-9781786331274"}
for e in E: e["link_failed"]=e["url"] in BROKEN
json.dump(E,open(os.path.join(HERE,"corpus.json"),"w",encoding="utf8"),ensure_ascii=False,indent=1)
with open(os.path.join(HERE,"corpus.csv"),"w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow("id date relation type title venue url archive status link_failed topics summary note".split())
    for e in E: w.writerow([e["id"],e["date"],e["relation"],e["type"],e["title"],e["venue"],e["url"],e["archive"],e["status"],e["link_failed"],"; ".join(e["topics"]),e["summary"],e["note"]])
from collections import Counter
print(len(E),Counter(e["relation"] for e in E),Counter(e["status"] for e in E),Counter(e["type"] for e in E),sum(1 for e in E if not e["date"]))
