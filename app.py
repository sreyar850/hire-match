"""
HireMatch AI – AI-Based Resume Screening and Job Matching System
Main Streamlit Application
"""

import os
import json
import glob
import streamlit as st
import pandas as pd

from config import DEFAULT_WEIGHTS, EDUCATION_LEVELS, TIER_THRESHOLDS, THEME_COLORS
from modules.parser import parse_resume
from modules.extractor import parse_and_extract_candidate, extract_skills
from modules.matcher import evaluate_candidate_match
from modules.ranker import (
    rank_candidates,
    create_ranking_dataframe,
    compute_cohort_insights,
    get_tier,
)
from modules.explainer import generate_skill_gap_report, generate_interview_questions
from modules.visualizer import (
    plot_candidate_radar,
    plot_cohort_rankings,
    plot_skills_breakdown_donut,
)
from modules.ai_enricher import generate_llm_candidate_insights, is_gemini_available
from modules.report_generator import export_candidates_csv, export_candidates_json, generate_candidate_html_card


# Page configuration
st.set_page_config(
    page_title="HireMatch AI — Resume Screening & Matching",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Metric card styles */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1E293B;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px 4px;
        border-radius: 14px;
        font-size: 12px;
        font-weight: 600;
    }
    .skill-matched {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .skill-missing {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .skill-preferred {
        background-color: #CFFAFE;
        color: #155E75;
        border: 1px solid #A5F3FC;
    }
    .skill-extra {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
    }
    
    /* Recommendation Card */
    .verdict-box {
        background-color: #F8FAFC;
        border-left: 5px solid #4F46E5;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "job_profile" not in st.session_state:
    # Load default job
    default_job_path = os.path.join("sample_data", "jobs", "senior_data_scientist.json")
    if os.path.exists(default_job_path):
        with open(default_job_path, "r", encoding="utf-8") as f:
            st.session_state["job_profile"] = json.load(f)
    else:
        st.session_state["job_profile"] = {
            "title": "Software Engineer",
            "min_experience_years": 3.0,
            "min_education": "Bachelor's Degree",
            "required_skills": ["python", "sql", "git", "docker"],
            "preferred_skills": ["aws", "fastapi"],
            "description": "Looking for a software engineer to build scalable backend services.",
        }


def load_sample_resumes():
    """Load sample resumes from sample_data/resumes/."""
    resume_files = glob.glob(os.path.join("sample_data", "resumes", "*.txt"))
    loaded = []
    for fpath in resume_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        cand = parse_and_extract_candidate(text, filename=fname)
        loaded.append(cand)
    st.session_state["candidates"] = loaded
    st.toast(f"Loaded {len(loaded)} sample resumes!", icon="✅")


# Sidebar: Job Configuration & Weights
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/recruitment.png", width=64)
    st.title("HireMatch AI")
    st.caption("AI-Powered Resume Screening & Job Matching")
    st.markdown("---")

    st.subheader("🎯 Target Job Profile")
    job_templates = {
        "Senior Data Scientist": "senior_data_scientist.json",
        "Full-Stack Software Engineer": "fullstack_developer.json",
        "AI / Machine Learning Engineer": "ai_ml_engineer.json",
        "Custom Job": None,
    }
    selected_template = st.selectbox("Select Role Template:", list(job_templates.keys()))

    if selected_template != "Custom Job" and job_templates[selected_template]:
        template_file = os.path.join("sample_data", "jobs", job_templates[selected_template])
        if os.path.exists(template_file):
            with open(template_file, "r", encoding="utf-8") as jf:
                st.session_state["job_profile"] = json.load(jf)

    # Job fields
    job_title = st.text_input("Job Title", value=st.session_state["job_profile"].get("title", ""))
    min_exp = st.number_input(
        "Min. Experience (Years)",
        min_value=0.0,
        max_value=20.0,
        value=float(st.session_state["job_profile"].get("min_experience_years", 2.0)),
        step=0.5
    )
    
    degree_options = ["None", "Associate / Diploma", "Bachelor's Degree", "Master's Degree", "PhD"]
    current_deg = st.session_state["job_profile"].get("min_education", "Bachelor's Degree")
    deg_idx = degree_options.index(current_deg) if current_deg in degree_options else 2
    min_edu = st.selectbox("Minimum Education", degree_options, index=deg_idx)

    req_skills_str = st.text_area(
        "Required Skills (comma-separated)",
        value=", ".join(st.session_state["job_profile"].get("required_skills", [])),
        help="Primary skills mandatory for this position."
    )
    pref_skills_str = st.text_area(
        "Preferred Skills (comma-separated)",
        value=", ".join(st.session_state["job_profile"].get("preferred_skills", [])),
        help="Bonus or nice-to-have skills."
    )
    job_desc = st.text_area(
        "Job Description Text",
        value=st.session_state["job_profile"].get("description", ""),
        height=100
    )

    # Update active job
    st.session_state["job_profile"] = {
        "title": job_title,
        "min_experience_years": min_exp,
        "min_education": min_edu,
        "required_skills": [s.strip().lower() for s in req_skills_str.split(",") if s.strip()],
        "preferred_skills": [s.strip().lower() for s in pref_skills_str.split(",") if s.strip()],
        "description": job_desc,
    }

    # Weight Tuning Expander
    with st.expander("⚖️ Match Scoring Weights", expanded=False):
        st.caption("Adjust weight importance for overall score calculation:")
        w_skills = st.slider("Skills Overlap", 0, 100, int(DEFAULT_WEIGHTS["skills"] * 100), step=5)
        w_semantic = st.slider("Semantic Alignment", 0, 100, int(DEFAULT_WEIGHTS["semantic"] * 100), step=5)
        w_exp = st.slider("Experience Match", 0, 100, int(DEFAULT_WEIGHTS["experience"] * 100), step=5)
        w_edu = st.slider("Education Fit", 0, 100, int(DEFAULT_WEIGHTS["education"] * 100), step=5)

        total_w = w_skills + w_semantic + w_exp + w_edu
        if total_w == 0:
            total_w = 1

        active_weights = {
            "skills": w_skills / total_w,
            "semantic": w_semantic / total_w,
            "experience": w_exp / total_w,
            "education": w_edu / total_w,
        }
        st.caption(f"Normalized Weights: Skills: {active_weights['skills']:.2f} | Semantic: {active_weights['semantic']:.2f} | Exp: {active_weights['experience']:.2f} | Edu: {active_weights['education']:.2f}")

    # Optional Gemini AI Settings
    with st.expander("✨ AI Executive Synthesis (Gemini)", expanded=False):
        gemini_key = st.text_input(
            "Gemini API Key (Optional)",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Enter API key for executive summaries and deep interview question synthesis."
        )

    st.markdown("---")
    st.caption("HireMatch AI v1.0 • NLP Resume Screener")


# Main app navigation tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Candidate Leaderboard",
    "👤 Candidate Deep-Dive & Gaps",
    "📤 Batch Resume Ingestion",
    "🧠 Job Studio & Skills Taxa",
])


# Auto-evaluate candidates against current job and weights
evaluations = []
for cand in st.session_state["candidates"]:
    ev = evaluate_candidate_match(cand, st.session_state["job_profile"], active_weights)
    evaluations.append(ev)

# Sort and filter
ranked_candidates = rank_candidates(evaluations)
cohort_metrics = compute_cohort_insights(ranked_candidates)


# TAB 1: CANDIDATE LEADERBOARD
with tab1:
    st.header(f"Candidate Leaderboard: {st.session_state['job_profile'].get('title', 'Role')}")
    st.caption("Automated ranking based on multi-factor NLP & semantic matching.")

    if not ranked_candidates:
        st.info("👋 No resumes evaluated yet! Go to the **Batch Resume Ingestion** tab to upload resumes or click below to load sample candidates.")
        if st.button("🚀 Load 5 Sample Resumes (Instant Demo)", type="primary"):
            load_sample_resumes()
            st.rerun()
    else:
        # Top KPI Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Applicants</div>
                <div class="metric-value">{cohort_metrics['total_candidates']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Matches (🌟)</div>
                <div class="metric-value">{cohort_metrics['top_candidates_count']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cohort Avg Score</div>
                <div class="metric-value">{cohort_metrics['avg_score']}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cohort Avg Exp</div>
                <div class="metric-value">{cohort_metrics['avg_experience']} yrs</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filters Row
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            min_filter_score = st.slider("Filter: Min Overall Score (%)", 0, 100, 0, step=5)
        with col_f2:
            all_req_skills = st.session_state["job_profile"].get("required_skills", [])
            mandatory_filter = st.multiselect("Filter: Must Include Skills", options=all_req_skills)

        filtered_ranked = rank_candidates(
            evaluations,
            min_score=float(min_filter_score),
            required_skill_filter=mandatory_filter
        )

        # Visual Leaderboard Chart
        col_chart, col_skills = st.columns([3, 2])
        with col_chart:
            st.plotly_chart(plot_cohort_rankings(filtered_ranked), use_container_width=True)
        with col_skills:
            st.subheader("Cohort Skill Trends")
            st.markdown("**Top Present Skills:**")
            if cohort_metrics["common_matched_skills"]:
                for s, count in cohort_metrics["common_matched_skills"]:
                    st.write(f"- `{s}`: {count} candidate(s)")
            else:
                st.write("None recorded yet.")

            st.markdown("**Most Common Skill Gaps:**")
            if cohort_metrics["common_missing_skills"]:
                for s, count in cohort_metrics["common_missing_skills"]:
                    st.write(f"- <span style='color: #EF4444;'>`{s}`</span>: missing in {count} applicant(s)", unsafe_allow_html=True)
            else:
                st.write("No skill gaps in cohort.")

        st.markdown("### 📋 Ranked Applicants Table")
        df_rank = create_ranking_dataframe(filtered_ranked)
        st.dataframe(df_rank, use_container_width=True, hide_index=True)

        # Export Actions
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv_data = export_candidates_csv(filtered_ranked)
            st.download_button(
                label="📥 Download Rankings as CSV",
                data=csv_data,
                file_name=f"HireMatch_Rankings_{job_title.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_exp2:
            json_data = export_candidates_json(filtered_ranked, st.session_state["job_profile"])
            st.download_button(
                label="📥 Export Cohort Report (JSON)",
                data=json_data,
                file_name=f"HireMatch_Cohort_{job_title.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )


# TAB 2: CANDIDATE DEEP-DIVE
with tab2:
    st.header("Candidate Fit Deep-Dive & Explainable AI")
    if not ranked_candidates:
        st.warning("Please upload or load candidates first.")
    else:
        candidate_options = {c["candidate_name"]: c for c in ranked_candidates}
        selected_cand_name = st.selectbox("Select Candidate to Inspect:", list(candidate_options.keys()))
        selected_eval = candidate_options[selected_cand_name]
        cand_data = selected_eval["candidate_data"]
        skills_match = selected_eval["skills_match"]
        tier = selected_eval["tier"]

        # Top summary header
        col_hdr1, col_hdr2 = st.columns([3, 1])
        with col_hdr1:
            st.markdown(f"## {selected_eval['candidate_name']} (Rank #{selected_eval['rank']})")
            st.markdown(f"**Email:** `{cand_data.get('email', 'N/A')}` | **Phone:** `{cand_data.get('phone', 'N/A')}` | **File:** `{selected_eval['filename']}`")
            links = cand_data.get("links", {})
            if links.get("linkedin"):
                st.markdown(f"🔗 [LinkedIn Profile]({links['linkedin']})", unsafe_allow_html=True)
            if links.get("github"):
                st.markdown(f"💻 [GitHub Profile]({links['github']})", unsafe_allow_html=True)
        with col_hdr2:
            st.markdown(f"""
            <div style="background-color: {tier['badge_color']}; color: white; border-radius: 10px; padding: 14px; text-align: center;">
                <div style="font-size: 26px; font-weight: 800;">{selected_eval['composite_score']}%</div>
                <div style="font-size: 14px; font-weight: 600;">{tier['icon']} {tier['label']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Visual Radar & Skill Donut Breakdown
        col_radar, col_donut = st.columns([3, 2])
        with col_radar:
            st.subheader("Candidate Fit Multi-Axis Radar")
            st.plotly_chart(plot_candidate_radar(selected_eval), use_container_width=True)
        with col_donut:
            st.subheader("Skills Distribution")
            st.plotly_chart(plot_skills_breakdown_donut(skills_match), use_container_width=True)

        # Skills Overlap Matrix
        st.subheader("Skills Alignment Matrix")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f"**Matched Required Skills ({len(skills_match['matched_required'])}):**")
            if skills_match["matched_required"]:
                badges = "".join([f'<span class="skill-badge skill-matched">✓ {s}</span>' for s in skills_match["matched_required"]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.write("None matched.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Matched Preferred Skills ({len(skills_match['matched_preferred'])}):**")
            if skills_match["matched_preferred"]:
                badges = "".join([f'<span class="skill-badge skill-preferred">★ {s}</span>' for s in skills_match["matched_preferred"]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.write("None.")

        with col_s2:
            st.markdown(f"**Missing Required Skills ({len(skills_match['missing_required'])}):**")
            if skills_match["missing_required"]:
                badges = "".join([f'<span class="skill-badge skill-missing">✗ {s}</span>' for s in skills_match["missing_required"]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.success("All required skills satisfied!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Additional Detected Skills ({len(skills_match['extra_skills'])}):**")
            if skills_match["extra_skills"]:
                badges = "".join([f'<span class="skill-badge skill-extra">{s}</span>' for s in skills_match["extra_skills"][:12]])
                st.markdown(badges, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Explainable AI Gap Analysis Report
        st.subheader("🔍 Explainable AI: Strengths & Skill Gap Analysis")
        gap_report = generate_skill_gap_report(selected_eval)

        st.markdown(f"""
        <div class="verdict-box">
            <strong>Hiring Recommendation:</strong> {gap_report['verdict']}
        </div>
        """, unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### ✅ Candidate Strengths")
            for s in gap_report["strengths"]:
                st.markdown(f"- {s}")
        with col_g2:
            st.markdown("##### ⚠️ Gaps & Attention Areas")
            if gap_report["gaps"]:
                for g in gap_report["gaps"]:
                    st.markdown(f"- {g}")
            else:
                st.markdown("- No critical gaps detected.")

        # Tailored Interview Questions
        st.subheader("🎯 Tailored Technical & Behavioral Interview Questions")
        st.caption("AI-generated questions addressing this candidate's specific background and missing gaps.")
        questions = generate_interview_questions(selected_eval, job_title=st.session_state["job_profile"].get("title", "Role"))
        for idx, q in enumerate(questions, 1):
            with st.expander(f"Question #{idx}: {q['category']} ({q['skill_focus']})", expanded=(idx <= 2)):
                st.markdown(f"**Interviewer Prompt:** {q['question']}")

        # Optional Gemini Executive Summary
        if gemini_key and len(gemini_key.strip()) > 10:
            st.markdown("---")
            st.subheader("🤖 Gemini AI Executive Assessment")
            with st.spinner("Generating qualitative AI synthesis via Gemini..."):
                gemini_res = generate_llm_candidate_insights(
                    candidate=cand_data,
                    job=st.session_state["job_profile"],
                    match_result=selected_eval,
                    api_key=gemini_key
                )
                st.markdown(gemini_res["summary"])

        # Download Candidate Summary Card HTML
        st.markdown("---")
        card_html = generate_candidate_html_card(selected_eval, job_title=st.session_state["job_profile"].get("title", "Role"))
        st.download_button(
            label=f"📄 Download {selected_eval['candidate_name']} Evaluation Card (HTML)",
            data=card_html,
            file_name=f"{selected_eval['candidate_name'].replace(' ', '_')}_Evaluation.html",
            mime="text/html",
        )


# TAB 3: BATCH RESUME INGESTION
with tab3:
    st.header("Batch Resume Ingestion & Parser")
    st.caption("Upload multiple PDF, DOCX, or TXT resumes for automated parsing and entity extraction.")

    col_up, col_demo = st.columns([3, 1])
    with col_up:
        uploaded_files = st.file_uploader(
            "Drop resumes here (PDF, DOCX, TXT):",
            type=["pdf", "docx", "doc", "txt"],
            accept_multiple_files=True
        )
    with col_demo:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Load Sample Resumes", use_container_width=True):
            load_sample_resumes()
            st.rerun()

    if uploaded_files:
        if st.button("⚡ Process & Extract Uploaded Resumes", type="primary"):
            progress_bar = st.progress(0.0)
            parsed_candidates = []
            
            for idx, file_obj in enumerate(uploaded_files):
                text = parse_resume(file_obj, filename=file_obj.name)
                cand = parse_and_extract_candidate(text, filename=file_obj.name)
                parsed_candidates.append(cand)
                progress_bar.progress((idx + 1) / len(uploaded_files))

            st.session_state["candidates"] = parsed_candidates
            st.success(f"Successfully processed {len(parsed_candidates)} resumes!")
            st.rerun()

    if st.session_state["candidates"]:
        st.markdown(f"### Currently Ingested Resumes ({len(st.session_state['candidates'])})")
        summary_rows = []
        for c in st.session_state["candidates"]:
            summary_rows.append({
                "Name": c["name"],
                "Email": c["email"],
                "Phone": c["phone"],
                "Experience": f"{c['experience']['total_years']} yrs",
                "Degree": c["education"]["highest_degree"],
                "Skills Detected": len(c["skills"]),
                "Filename": c["filename"],
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        if st.button("🗑️ Clear All Loaded Resumes"):
            st.session_state["candidates"] = []
            st.rerun()


# TAB 4: JOB STUDIO & SKILLS TAXONOMY
with tab4:
    st.header("Job Description Studio & Skills Taxonomy")
    st.caption("Explore extracted skills and customize the job matching taxonomy.")

    col_j1, col_j2 = st.columns(2)
    with col_j1:
        st.subheader("Job Profile Specification")
        st.json(st.session_state["job_profile"])

    with col_j2:
        st.subheader("Auto-Extracted Skills from Description")
        desc_text = st.session_state["job_profile"].get("description", "")
        detected_in_job = extract_skills(desc_text)
        st.write(f"Detected **{detected_in_job['count']}** technical skills directly in description text:")
        if detected_in_job["all_skills"]:
            badges = "".join([f'<span class="skill-badge skill-matched">{s}</span>' for s in detected_in_job["all_skills"]])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.write("No taxonomy skills detected in raw description text.")

    st.markdown("---")
    st.subheader("Explore HireMatch Skills Taxonomy")
    from modules.skills_database import SKILLS_TAXONOMY
    taxa_cat = st.selectbox("Select Domain:", list(SKILLS_TAXONOMY.keys()))
    st.write(f"Recognized skills in **{taxa_cat}**:")
    badges = "".join([f'<span class="skill-badge skill-extra">{s}</span>' for s in SKILLS_TAXONOMY[taxa_cat]])
    st.markdown(badges, unsafe_allow_html=True)
