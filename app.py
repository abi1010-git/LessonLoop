import html
import os

import streamlit as st
from dotenv import load_dotenv

from ai_service import analyze, improve
from demo_data import DEMO_DATA

load_dotenv()
st.set_page_config(page_title="LessonLoop", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{max-width:1180px;padding-top:1.6rem;padding-bottom:4rem}[data-testid="stSidebar"]{background:#f8fafc;border-right:1px solid #e2e8f0}.hero{padding:1.65rem 1.8rem;border-radius:22px;background:linear-gradient(125deg,#172554,#1d4ed8);color:white;margin-bottom:1.4rem;box-shadow:0 14px 35px rgba(30,64,175,.18)}.hero h1{font-size:2.65rem;margin:0 0 .25rem;letter-spacing:-.04em}.hero p{color:#dbeafe;font-size:1.08rem;margin:0}.eyebrow{text-transform:uppercase;letter-spacing:.11em;font-size:.72rem;font-weight:800;color:#2563eb;margin-bottom:.25rem}.section-copy{color:#64748b;margin-top:-.5rem;margin-bottom:1rem}.insight{padding:1.05rem 1.15rem;border:1px solid #e2e8f0;border-radius:15px;background:white;margin-bottom:.7rem;box-shadow:0 3px 12px rgba(15,23,42,.04)}.insight h4{margin:0 0 .35rem;color:#0f172a}.muted{color:#64748b;font-size:.9rem}.evidence{margin-top:.55rem;padding:.55rem .7rem;background:#f8fafc;border-radius:9px;color:#475569;font-size:.88rem}.severity{display:inline-block;padding:3px 8px;border-radius:99px;font-size:.68rem;font-weight:800;letter-spacing:.05em;margin-left:.4rem}.high{background:#fee2e2;color:#991b1b}.medium{background:#fef3c7;color:#92400e}.low{background:#dcfce7;color:#166534}.action{border-left:4px solid #2563eb;padding:.85rem 1rem;background:#eff6ff;border-radius:0 12px 12px 0;margin-bottom:.6rem}.action strong{color:#1e3a8a}.group{padding:1rem;border-radius:14px;border:1px solid #e2e8f0;background:#fff;min-height:220px}.group-title{font-weight:800;font-size:1rem;margin-bottom:.25rem}.student-list{font-size:.86rem;color:#475569;margin-bottom:.8rem}.timeline{position:relative;padding-left:2rem;margin-left:.5rem;border-left:2px solid #bfdbfe}.timeline-item{position:relative;padding:0 0 1.2rem .7rem}.timeline-dot{position:absolute;left:-2.47rem;top:.1rem;width:14px;height:14px;border-radius:50%;background:#2563eb;border:3px solid #dbeafe}.time{font-size:.75rem;font-weight:800;color:#2563eb;text-transform:uppercase}.purpose{font-size:.88rem;color:#64748b;margin-top:.2rem}div[data-testid="stMetric"]{background:white;border:1px solid #e2e8f0;padding:1rem;border-radius:15px;box-shadow:0 3px 12px rgba(15,23,42,.04)}.stButton button{border-radius:11px;font-weight:700;min-height:2.8rem}
</style>
""", unsafe_allow_html=True)


def esc(value):
    return html.escape(str(value or ""))


def lesson_text(data=None):
    d = data or st.session_state
    return f"Grade {d['grade']} {d['subject']}: {d['topic']}. Objective: {d['objective']}. Notes: {d['notes']}"


def load_demo():
    for key, value in DEMO_DATA.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value
    st.session_state.analysis = None
    st.session_state.improvement = None


def run_demo():
    load_demo()
    lesson = lesson_text(DEMO_DATA)
    st.session_state.analysis = analyze(lesson, DEMO_DATA["questions"], DEMO_DATA["responses"])
    st.session_state.improvement = improve(lesson, st.session_state.analysis, DEMO_DATA["plan"])
    st.session_state.demo_complete = True


defaults = {"grade":"","subject":"","topic":"","objective":"","notes":"","questions":"","responses":[{"student":"","response":""}],"plan":"","analysis":None,"improvement":None,"demo_complete":False}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

with st.sidebar:
    st.markdown("## ✦ LessonLoop")
    st.caption("Close the loop between student evidence and tomorrow's teaching.")
    if st.button("Run 1-Click Demo", type="primary", use_container_width=True):
        with st.spinner("Building your complete demo…"):
            try:
                run_demo()
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    st.caption("Loads 10 responses, analyzes the class, and adapts tomorrow's plan.")
    st.divider()
    st.markdown("### Today's Lesson")
    st.session_state.grade = st.text_input("Grade level", st.session_state.grade)
    st.session_state.subject = st.text_input("Subject", st.session_state.subject)
    st.session_state.topic = st.text_input("Lesson topic", st.session_state.topic)
    st.session_state.objective = st.text_area("Learning objective", st.session_state.objective, height=95)
    st.session_state.notes = st.text_area("Teacher notes (optional)", st.session_state.notes, height=75)
    if st.button("Load demo inputs only", use_container_width=True):
        load_demo()
        st.rerun()
    st.caption("● Gemini connected" if os.getenv("GEMINI_API_KEY") else "○ Gemini key not found")

st.markdown('<div class="hero"><div style="font-size:.78rem;font-weight:800;letter-spacing:.12em;color:#93c5fd">TODAY → INSIGHT → TOMORROW</div><h1>LessonLoop</h1><p>See what students understood, then make the right changes for tomorrow.</p></div>', unsafe_allow_html=True)
if st.session_state.demo_complete:
    st.success("Demo complete — review the class evidence and tomorrow's adapted lesson below.")

st.markdown('<div class="eyebrow">Step 1 · Gather evidence</div>', unsafe_allow_html=True)
st.markdown("## Exit Ticket Responses")
st.markdown('<div class="section-copy">Paste the prompt and student answers. LessonLoop looks for class-wide patterns, not labels.</div>', unsafe_allow_html=True)
st.session_state.questions = st.text_area("Exit-ticket question(s)", st.session_state.questions, placeholder="What did students answer?")
st.session_state.responses = st.data_editor(st.session_state.responses, num_rows="dynamic", use_container_width=True, hide_index=True, column_config={"student":st.column_config.TextColumn("Student",width="small"),"response":st.column_config.TextColumn("Response",width="large")}, key="response_editor")
if st.button("Analyze Class Understanding", type="primary", use_container_width=True):
    valid = [row for row in st.session_state.responses if str(row.get("response", "")).strip()]
    if not st.session_state.objective or not st.session_state.questions or not valid:
        st.error("Add the learning objective, exit-ticket question, and at least one student response.")
    else:
        with st.spinner("Finding patterns in student thinking…"):
            try:
                st.session_state.analysis = analyze(lesson_text(), st.session_state.questions, valid)
                st.session_state.improvement = None
                st.session_state.demo_complete = False
            except Exception as exc:
                st.error(str(exc))

analysis_result = st.session_state.analysis
if analysis_result:
    st.divider()
    st.markdown('<div class="eyebrow">Step 2 · Understand the class</div>', unsafe_allow_html=True)
    st.markdown("## What Today's Responses Tell You")
    score = max(0, min(100, int(analysis_result.get("mastery_score", 0))))
    m1, m2, m3 = st.columns(3)
    m1.metric("Class mastery", f"{score}%", help="Evidence-based estimate from these responses")
    m2.metric("Need targeted support", len(analysis_result.get("students_needing_support", [])))
    m3.metric("Learning gaps found", len(analysis_result.get("misconceptions", [])))
    st.progress(score / 100, text=f"{score}% demonstrated the learning objective")
    st.info(analysis_result.get("class_summary", ""), icon="ℹ️")
    st.markdown("### Start Here Tomorrow")
    focus_items = analysis_result.get("recommended_focus_for_tomorrow", [])
    focus_cols = st.columns(min(3, max(1, len(focus_items))))
    for index, item in enumerate(focus_items):
        with focus_cols[index % len(focus_cols)]:
            st.markdown(f'<div class="action"><strong>Priority {index+1}</strong><br>{esc(item)}</div>', unsafe_allow_html=True)

    gap_tab, strength_tab, groups_tab, students_tab = st.tabs(["Learning gaps", "What students know", "Small groups", "Student check-in"])
    with gap_tab:
        for gap in analysis_result.get("misconceptions", []):
            severity = str(gap.get("severity", "medium")).lower()
            severity = severity if severity in {"high","medium","low"} else "medium"
            st.markdown(f'<div class="insight"><h4>{esc(gap.get("name"))}<span class="severity {severity}">{severity.upper()}</span></h4><div class="muted"><b>{esc(gap.get("student_count",0))} students</b> · {esc(gap.get("description"))}</div><div class="evidence"><b>Evidence:</b> {esc(gap.get("example_evidence"))}</div><div style="margin-top:.6rem"><b>Teaching response:</b> {esc(gap.get("recommended_response"))}</div></div>', unsafe_allow_html=True)
    with strength_tab:
        for strength in analysis_result.get("strengths", []):
            st.markdown(f'<div class="insight"><h4>✓ {esc(strength.get("concept"))}</h4><div class="muted">{esc(strength.get("evidence"))}</div></div>', unsafe_allow_html=True)
    with groups_tab:
        groups = analysis_result.get("differentiated_support", {})
        columns = st.columns(3)
        for column, (key, title, color) in zip(columns, [("needs_reteaching","Needs Reteaching","#dc2626"),("developing","Developing","#d97706"),("ready_to_extend","Ready to Extend","#16a34a")]):
            group = groups.get(key, {})
            with column:
                st.markdown(f'<div class="group"><div class="group-title" style="color:{color}">{title}</div><div class="student-list">{esc(", ".join(group.get("students",[])) or "No students assigned")}</div><b>Teacher move</b><br><span class="muted">{esc(group.get("teacher_action","—"))}</span><br><br><b>Try tomorrow</b><br><span class="muted">{esc(group.get("activity","—"))}</span></div>', unsafe_allow_html=True)
    with students_tab:
        left, right = st.columns(2)
        with left:
            st.markdown("#### Check in with")
            for student in analysis_result.get("students_needing_support", []):
                st.warning(f"**{student.get('student','Student')}** — {student.get('issue','')}")
        with right:
            st.markdown("#### Showing mastery")
            for student in analysis_result.get("students_showing_mastery", []):
                st.success(str(student))

st.divider()
st.markdown('<div class="eyebrow">Step 3 · Adapt tomorrow</div>', unsafe_allow_html=True)
st.markdown("## Tomorrow's Current Lesson Plan")
st.markdown('<div class="section-copy">Keep your original plan. LessonLoop suggests only the changes supported by today\'s evidence.</div>', unsafe_allow_html=True)
st.session_state.plan = st.text_area("Paste the plan you were already going to teach", st.session_state.plan, height=150)
if st.button("Improve Tomorrow's Lesson", type="primary", use_container_width=True):
    if not analysis_result:
        st.warning("Analyze the exit ticket first so recommendations are grounded in student evidence.")
    elif not st.session_state.plan.strip():
        st.error("Add tomorrow's current lesson plan first.")
    else:
        with st.spinner("Matching tomorrow's plan to today's learning…"):
            try:
                st.session_state.improvement = improve(lesson_text(), analysis_result, st.session_state.plan)
            except Exception as exc:
                st.error(str(exc))

improvement_result = st.session_state.improvement
if improvement_result:
    st.divider()
    st.markdown('<div class="eyebrow">Step 4 · Your teaching brief</div>', unsafe_allow_html=True)
    st.markdown("## Recommended Changes for Tomorrow")
    st.success(improvement_result.get("overall_recommendation", ""), icon="✅")
    keep_tab, change_tab, add_tab, trim_tab = st.tabs(["Keep", "Change", "Add", "Shorten / Remove"])
    with keep_tab:
        for item in improvement_result.get("keep", []):
            st.markdown(f'<div class="insight"><h4>Keep this</h4>{esc(item)}</div>', unsafe_allow_html=True)
    with change_tab:
        for item in improvement_result.get("change", []):
            st.markdown(f'<div class="insight"><div class="muted">CURRENT</div><s>{esc(item.get("original"))}</s><h4 style="margin-top:.65rem">Change to: {esc(item.get("suggestion"))}</h4><div class="evidence"><b>Why:</b> {esc(item.get("reason"))}</div></div>', unsafe_allow_html=True)
    with add_tab:
        for item in improvement_result.get("add", []):
            duration = f'{esc(item.get("duration_minutes"))} min · ' if item.get("duration_minutes") else ""
            st.markdown(f'<div class="insight"><h4>+ {esc(item.get("activity"))}</h4><div class="muted">{duration}{esc(item.get("reason"))}</div></div>', unsafe_allow_html=True)
    with trim_tab:
        for item in improvement_result.get("remove_or_shorten", []):
            st.markdown(f'<div class="insight"><h4>{esc(item.get("activity"))}</h4><div class="evidence"><b>Why:</b> {esc(item.get("reason"))}</div></div>', unsafe_allow_html=True)
    st.markdown("### Recommended Revised Lesson Plan")
    st.caption("A ready-to-teach sequence that keeps the strongest parts of your original plan.")
    timeline = '<div class="timeline">'
    for item in improvement_result.get("revised_plan", []):
        timeline += f'<div class="timeline-item"><span class="timeline-dot"></span><div class="time">{esc(item.get("duration"))}</div><b>{esc(item.get("activity"))}</b><div class="purpose">{esc(item.get("purpose"))}</div></div>'
    timeline += "</div>"
    st.markdown(timeline, unsafe_allow_html=True)
