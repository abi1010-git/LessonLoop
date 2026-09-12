import os
import streamlit as st
from dotenv import load_dotenv
from demo_data import DEMO_DATA
from ai_service import analyze, improve

load_dotenv()
st.set_page_config(page_title="LessonLoop", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container{max-width:1180px;padding-top:2rem}.hero{padding:1.5rem 1.7rem;border-radius:20px;background:linear-gradient(120deg,#172554,#1e3a8a);color:white;margin-bottom:1.4rem}.hero h1{font-size:2.7rem;margin:0}.hero p{color:#c7d2fe;font-size:1.05rem}.card{padding:1.05rem 1.15rem;border:1px solid #e2e8f0;border-radius:14px;background:#fff;min-height:120px}.pill{display:inline-block;padding:3px 9px;border-radius:99px;background:#fee2e2;color:#991b1b;font-size:.78rem;font-weight:700}.stButton>button{border-radius:10px;font-weight:650}
</style>""", unsafe_allow_html=True)

def init():
    defaults = {"grade":"", "subject":"", "topic":"", "objective":"", "notes":"", "questions":"", "responses":[{"student":"", "response":""}], "plan":"", "analysis":None, "improvement":None}
    for k,v in defaults.items(): st.session_state.setdefault(k,v)
init()

def lesson_text():
    return f"Grade {st.session_state.grade} {st.session_state.subject}: {st.session_state.topic}. Objective: {st.session_state.objective}. Notes: {st.session_state.notes}"

with st.sidebar:
    st.markdown("## ✦ LessonLoop")
    st.caption("From today's evidence to tomorrow's action.")
    st.markdown("### Today's Lesson")
    st.session_state.grade = st.text_input("Grade level", st.session_state.grade)
    st.session_state.subject = st.text_input("Subject", st.session_state.subject)
    st.session_state.topic = st.text_input("Lesson topic", st.session_state.topic)
    st.session_state.objective = st.text_area("Learning objective", st.session_state.objective, height=90)
    st.session_state.notes = st.text_area("Teacher notes (optional)", st.session_state.notes, height=70)
    if st.button("Load Demo Data", use_container_width=True):
        for k,v in DEMO_DATA.items(): st.session_state[k] = v.copy() if isinstance(v,list) else v
        st.session_state.analysis = st.session_state.improvement = None
        st.rerun()

st.markdown("<div class='hero'><h1>LessonLoop</h1><p>Turn today's exit-ticket responses into actionable improvements for tomorrow's lesson plan.</p></div>", unsafe_allow_html=True)
st.markdown("## Exit Ticket")
st.session_state.questions = st.text_area("Exit-ticket question(s)", st.session_state.questions, placeholder="Paste the question students answered…")
st.caption("Enter one student response per row. Names are optional for quick analysis.")
st.session_state.responses = st.data_editor(st.session_state.responses, num_rows="dynamic", use_container_width=True, hide_index=True, column_config={"student":"Student", "response":"Response"}, key="response_editor")

if st.button("✦  Analyze Class Understanding", type="primary", use_container_width=True):
    valid = [r for r in st.session_state.responses if str(r.get("response","")).strip()]
    if not st.session_state.objective or not st.session_state.questions or not valid: st.error("Add the learning objective, exit-ticket question, and at least one response first.")
    else:
        with st.spinner("Reading the class evidence…"):
            try: st.session_state.analysis = analyze(lesson_text(), st.session_state.questions, valid); st.session_state.improvement = None
            except Exception as e: st.error(str(e))

a = st.session_state.analysis
if a:
    st.markdown("## Class Understanding")
    support = len(a.get("students_needing_support",[])); misc = len(a.get("misconceptions",[])); score = int(a.get("mastery_score",0))
    c1,c2,c3 = st.columns(3); c1.metric("Class mastery", f"{score}%"); c2.metric("Students needing support", support); c3.metric("Misconceptions found", misc)
    st.progress(max(0,min(100,score))/100)
    st.info(a.get("class_summary",""))
    left,right = st.columns(2)
    with left:
        st.markdown("### Misconceptions")
        for m in a.get("misconceptions",[]): st.markdown(f'<div class="card"><b>{m.get("name","")}</b> &nbsp; <span class="pill">{m.get("severity","medium").upper()}</span><br><small>{m.get("student_count",0)} students · {m.get("description","")}<br><i>Evidence:</i> {m.get("example_evidence","")}<br><i>Try:</i> {m.get("recommended_response","")}</small></div><br>', unsafe_allow_html=True)
    with right:
        st.markdown("### Strengths")
        for s in a.get("strengths",[]): st.success(f"**{s.get('concept','')}** — {s.get('evidence','')}")
        st.markdown("### Focus for tomorrow")
        for x in a.get("recommended_focus_for_tomorrow",[]): st.write("• "+x)
    with st.expander("Differentiated Support", expanded=True):
        groups=a.get("differentiated_support",{}); cols=st.columns(3)
        for col,(key,title) in zip(cols,[("needs_reteaching","Needs Reteaching"),("developing","Developing"),("ready_to_extend","Ready to Extend")]):
            g=groups.get(key,{})
            with col: st.markdown(f"**{title}**\n\n{', '.join(g.get('students',[])) or '—'}\n\n*Action:* {g.get('teacher_action','—')}\n\n*Activity:* {g.get('activity','—')}")

st.markdown("## Tomorrow's Current Lesson Plan")
st.session_state.plan = st.text_area("Paste the plan you were already going to teach", st.session_state.plan, height=145)
if st.button("Improve Tomorrow's Lesson", type="primary", use_container_width=True):
    if not a: st.warning("Analyze the exit ticket before improving tomorrow's plan.")
    elif not st.session_state.plan.strip(): st.error("Add tomorrow's current lesson plan first.")
    else:
        with st.spinner("Adapting the plan to today's evidence…"):
            try: st.session_state.improvement = improve(lesson_text(), a, st.session_state.plan)
            except Exception as e: st.error(str(e))

i=st.session_state.improvement
if i:
    st.markdown("## Tomorrow's Lesson Improvements")
    st.info(i.get("overall_recommendation",""))
    for title,key in [("Keep","keep"),("Change","change"),("Add","add"),("Remove / Shorten","remove_or_shorten")]:
        items=i.get(key,[])
        if items:
            st.markdown(f"### {title}")
            for x in items:
                if isinstance(x,str): st.write("✓ "+x)
                else: st.markdown(f"**{x.get('activity',x.get('original',''))}** — {x.get('suggestion',x.get('reason',''))}  \n<small>{x.get('reason','')}</small>", unsafe_allow_html=True)
    st.markdown("### Recommended Revised Lesson Plan")
    for n,x in enumerate(i.get("revised_plan",[]),1):
        st.markdown(f"**{n} · {x.get('duration','')}**  {x.get('activity','')}  \n<small>{x.get('purpose','')}</small>", unsafe_allow_html=True)
