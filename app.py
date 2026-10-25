"""
Requirement-to-Test Traceability Tool (Problem Statement 80)
Unified Modern UI with Home (Dashboard + Interactive Matrix), Managers, and Settings.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db

# Page Configuration
st.set_page_config(
    page_title="ReqTrace • Traceability Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB and ensure sample data exists on first run
db.init_db()
db.seed_sample_data(force=False)

# Modern Custom CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin-bottom: 22px;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(0,0,0,0.06);
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.8rem;
        margin-top: 6px;
        font-weight: 500;
    }
    .pill-green {
        background: #dcfce7;
        color: #15803d;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-red {
        background: #fee2e2;
        color: #b91c1c;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-amber {
        background: #fef3c7;
        color: #b45309;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .pill-slate {
        background: #f1f5f9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 16px;
    }

    /* Alert Boxes */
    .alert-card-danger {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 4px solid #f43f5e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .alert-card-warning {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .alert-card-success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR ----------------- #
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 18px 16px; border-radius: 12px; margin-bottom: 20px; color: white;">
        <div style="font-size: 1.2rem; font-weight: 800; letter-spacing: -0.02em;">🎯 ReqTrace Pro</div>
        <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 4px;">Problem 80 • Traceability Tool</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "📋 Requirements Manager",
            "🧪 Test Cases Manager",
            "🔗 Link & Map Tests",
            "⚙️ Demo Data & Settings"
        ],
        index=0
    )

    st.divider()

    # Dynamic Quick Stats in Sidebar
    metrics = db.get_summary_metrics()
    st.markdown("#### 📈 Health Snapshot")
    
    # Visual Progress Bar
    cov_val = metrics["coverage_pct"]
    st.write(f"**Coverage Rate:** `{cov_val}%`")
    st.progress(min(max(cov_val / 100.0, 0.0), 1.0))
    
    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; font-size: 0.85rem; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #64748b;">Requirements:</span>
            <strong>{metrics['total_reqs']}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #64748b;">Test Cases:</span>
            <strong>{metrics['total_tests']}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #64748b;">Untested Gaps:</span>
            <span class="pill-red">{metrics['untested_reqs']} Gaps</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Test Pass Rate:</span>
            <span class="pill-green">{metrics['pass_rate_pct']}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("College Login System Demo Environment")


# =============================================================
# 1. UNIFIED "HOME" (Dashboard & Interactive Matrix)
# =============================================================
if menu == "🏠 Home":
    # Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); padding: 26px 30px; border-radius: 16px; margin-bottom: 22px; color: white; box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div>
                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #a5b4fc; margin-bottom: 4px;">
                    Problem Statement 80 • Executive Verification Platform
                </div>
                <div style="font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;">
                    Requirement-to-Test Traceability Tool
                </div>
                <div style="font-size: 0.95rem; color: #e0e7ff; margin-top: 6px; max-width: 720px; line-height: 1.4;">
                    Unify business requirements and verification test cases, eliminate blind spots with automatic gap detection, and monitor release readiness in real time.
                </div>
            </div>
            <div>
                <span style="background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); color: #ffffff; padding: 6px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 600;">
                    🟢 Live System Active
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    metrics = db.get_summary_metrics()

    # Modern KPI Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Requirements</div>
            <div class="kpi-value">{metrics['total_reqs']}</div>
            <div class="kpi-sub"><span class="pill-slate">Across All Modules</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Test Cases</div>
            <div class="kpi-value">{metrics['total_tests']}</div>
            <div class="kpi-sub"><span class="pill-slate">{metrics['passed_tests']} Passed • {metrics['failed_tests']} Failed</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col3:
        cov_color = "pill-green" if metrics['coverage_pct'] >= 80 else ("pill-amber" if metrics['coverage_pct'] >= 50 else "pill-red")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Test Coverage</div>
            <div class="kpi-value">{metrics['coverage_pct']}%</div>
            <div class="kpi-sub"><span class="{cov_color}">{metrics['covered_reqs']} of {metrics['total_reqs']} Covered</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col4:
        gap_pill = "pill-red" if metrics['untested_reqs'] > 0 else "pill-green"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Untested Gaps</div>
            <div class="kpi-value" style="color: {'#dc2626' if metrics['untested_reqs'] > 0 else '#16a34a'};">{metrics['untested_reqs']}</div>
            <div class="kpi-sub"><span class="{gap_pill}">{'Action Required' if metrics['untested_reqs'] > 0 else 'All Requirements Tested'}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Test Pass Rate</div>
            <div class="kpi-value" style="color: #16a34a;">{metrics['pass_rate_pct']}%</div>
            <div class="kpi-sub"><span class="pill-green">{metrics['passed_tests']} of {metrics['passed_tests'] + metrics['failed_tests'] + metrics['blocked_tests']} Executed</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Critical Alerts Banner (Only shows when risks exist)
    matrix_df = db.calculate_traceability_matrix()
    untested_critical = matrix_df[(matrix_df["Coverage Status"] == "Untested") & (matrix_df["Priority"] == "High")]
    failed_reqs = matrix_df[matrix_df["Overall Outcome"] == "Failed"]

    if not untested_critical.empty or not failed_reqs.empty:
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            if not untested_critical.empty:
                gap_items = "".join([f"<li><strong>{r['Requirement ID']}</strong> ({r['Requirement Title']}) — <em>{r['Module']}</em></li>" for _, r in untested_critical.iterrows()])
                st.markdown(f"""
                <div class="alert-card-danger">
                    <div style="font-weight: 700; color: #9f1239; font-size: 0.95rem; margin-bottom: 4px;">⚠️ High-Priority Coverage Gaps Detected ({len(untested_critical)})</div>
                    <div style="font-size: 0.85rem; color: #4c0519;">These critical features have zero tests linked and pose immediate release risk:</div>
                    <ul style="margin-top: 6px; margin-bottom: 0px; font-size: 0.85rem; color: #881337; padding-left: 18px;">
                        {gap_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-card-success">
                    <div style="font-weight: 700; color: #166534; font-size: 0.92rem;">✅ Zero High-Priority Coverage Gaps</div>
                    <div style="font-size: 0.82rem; color: #14532d;">All critical tier requirements have at least one test case linked.</div>
                </div>
                """, unsafe_allow_html=True)

        with a_col2:
            if not failed_reqs.empty:
                fail_items = "".join([f"<li><strong>{r['Requirement ID']}</strong> ({r['Requirement Title']}) — Tests: <code>{r['Linked Tests']}</code></li>" for _, r in failed_reqs.iterrows()])
                st.markdown(f"""
                <div class="alert-card-warning">
                    <div style="font-weight: 700; color: #92400e; font-size: 0.95rem; margin-bottom: 4px;">❌ Requirements with Failing Tests ({len(failed_reqs)})</div>
                    <div style="font-size: 0.85rem; color: #78350f;">Features are covered by tests, but test execution produced failures:</div>
                    <ul style="margin-top: 6px; margin-bottom: 0px; font-size: 0.85rem; color: #78350f; padding-left: 18px;">
                        {fail_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-card-success">
                    <div style="font-weight: 700; color: #166534; font-size: 0.92rem;">✅ Zero Failing Requirements</div>
                    <div style="font-size: 0.82rem; color: #14532d;">No executed test cases are currently in a Failed state.</div>
                </div>
                """, unsafe_allow_html=True)

    # Visual Analytics Row
    with st.expander("📊 Quality Distribution Charts", expanded=True):
        c_col1, c_col2 = st.columns(2)

        with c_col1:
            st.markdown("<div style='font-weight: 700; font-size: 0.95rem; color: #1e293b; margin-bottom: 6px;'>Requirements Coverage Distribution</div>", unsafe_allow_html=True)
            if metrics["total_reqs"] > 0:
                cov_df = pd.DataFrame({
                    "Status": ["Covered Requirements", "Untested (Gaps)"],
                    "Count": [metrics["covered_reqs"], metrics["untested_reqs"]]
                })
                fig_cov = px.pie(
                    cov_df,
                    names="Status",
                    values="Count",
                    color="Status",
                    color_discrete_map={
                        "Covered Requirements": "#10b981",
                        "Untested (Gaps)": "#f43f5e"
                    },
                    hole=0.55
                )
                fig_cov.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=240,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_cov, use_container_width=True)
            else:
                st.info("No requirements to chart.")

        with c_col2:
            st.markdown("<div style='font-weight: 700; font-size: 0.95rem; color: #1e293b; margin-bottom: 6px;'>Test Execution Verdicts Breakdown</div>", unsafe_allow_html=True)
            test_df = db.get_all_test_cases()
            if not test_df.empty:
                verdict_counts = test_df["execution_status"].value_counts().reset_index()
                verdict_counts.columns = ["Status", "Count"]
                color_map = {
                    "Passed": "#10b981",
                    "Failed": "#f43f5e",
                    "Blocked": "#f59e0b",
                    "Not Run": "#94a3b8"
                }
                fig_bar = px.bar(
                    verdict_counts,
                    x="Status",
                    y="Count",
                    color="Status",
                    color_discrete_map=color_map,
                    text="Count"
                )
                fig_bar.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=240,
                    showlegend=False,
                    xaxis_title=None,
                    yaxis_title="Count"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No test cases to chart.")

    st.markdown("---")

    # ================= LIVE TRACEABILITY MATRIX SECTION ================= #
    st.markdown("""
    <div class="section-title">
        <span>📑 Interactive Traceability Matrix</span>
    </div>
    <div class="section-desc">
        Explore relationships between requirements and test cases, isolate untested gaps, and inspect verified release health.
    </div>
    """, unsafe_allow_html=True)

    view_col1, view_col2 = st.columns([3, 1])
    with view_col1:
        matrix_direction = st.radio(
            "Matrix Perspective:",
            ["Forward Traceability (Requirements ➔ Tests ➔ Verdict)", "Reverse Traceability (Tests ➔ Requirements / Orphan Audit)"],
            horizontal=True
        )

    if "Forward" in matrix_direction:
        # Forward Matrix View
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            search_query = st.text_input("🔍 Search Requirement", placeholder="ID or Title...").strip().lower()
        with f_col2:
            coverage_filter = st.selectbox("Coverage Filter", ["All", "Covered", "Untested"])
        with f_col3:
            outcome_filter = st.selectbox("Outcome Filter", ["All", "Passed", "Failed", "Blocked", "Partially Run", "Not Run", "No Tests"])
        with f_col4:
            priority_filter = st.selectbox("Priority Filter", ["All", "High", "Medium", "Low"])

        # Filter calculation
        filtered_df = matrix_df.copy()

        if search_query:
            filtered_df = filtered_df[
                filtered_df["Requirement ID"].str.lower().str.contains(search_query) | 
                filtered_df["Requirement Title"].str.lower().str.contains(search_query)
            ]
        if coverage_filter != "All":
            filtered_df = filtered_df[filtered_df["Coverage Status"] == coverage_filter]
        if outcome_filter != "All":
            filtered_df = filtered_df[filtered_df["Overall Outcome"] == outcome_filter]
        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]

        # Table Display with Styling
        st.caption(f"Showing **{len(filtered_df)}** of **{len(matrix_df)}** requirements:")

        def highlight_matrix(val):
            if val in ["Untested", "Failed", "No Tests"]:
                return "color: #b91c1c; font-weight: 700; background-color: #fef2f2;"
            elif val in ["Covered", "Passed"]:
                return "color: #15803d; font-weight: 700; background-color: #f0fdf4;"
            elif val == "Blocked":
                return "color: #b45309; font-weight: 700; background-color: #fffbeb;"
            elif val == "Partially Run":
                return "color: #d97706; font-weight: 700; background-color: #fffbeb;"
            return ""

        styled_df = filtered_df.style.map(highlight_matrix, subset=["Coverage Status", "Overall Outcome"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Action Bar (Download & Insight)
        act_col1, act_col2 = st.columns([2, 5])
        with act_col1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download RTM Report (CSV)",
                data=csv_data,
                file_name="Traceability_Matrix_Report.csv",
                mime="text/csv",
                type="primary"
            )
        with act_col2:
            st.info("💡 **Core Principle:** A requirement can be **Covered** (has test cases) while still **Failing** execution. Both dimensions are evaluated separately.")

    else:
        # Reverse Matrix View
        rev_df = db.calculate_reverse_traceability()
        st.caption("Verifies that every active test case serves an approved requirement and detects orphan tests.")

        if rev_df.empty:
            st.info("No test cases registered.")
        else:
            orphan_count = len(rev_df[rev_df["Traceability Status"] == "Orphan (No Req)"])
            if orphan_count > 0:
                st.warning(f"⚠️ **{orphan_count} Orphan Test Case(s)** detected that are not mapped to any requirement!")
            else:
                st.success("✅ Clean Traceability: All test cases are linked to valid requirements!")

            st.dataframe(rev_df, use_container_width=True, hide_index=True)

            csv_rev = rev_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Reverse Traceability CSV",
                data=csv_rev,
                file_name="Reverse_Traceability_Report.csv",
                mime="text/csv"
            )


# =============================================================
# 2. REQUIREMENTS MANAGER
# =============================================================
elif menu == "📋 Requirements Manager":
    st.markdown("""
    <div class="section-title">📋 Requirements Management</div>
    <div class="section-desc">Define, catalog, and manage business requirements across system modules.</div>
    """, unsafe_allow_html=True)

    tab_add, tab_view = st.tabs(["➕ Add New Requirement", "📑 View & Manage Existing"])

    with tab_add:
        with st.form("add_req_form", clear_on_submit=True):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                new_id = st.text_input("Requirement ID *", placeholder="e.g. R8, REQ-108").strip()
                new_title = st.text_input("Requirement Title *", placeholder="e.g. Multi-Factor Authentication").strip()
                new_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            with r_col2:
                new_module = st.text_input("Module / Category", placeholder="e.g. Security, Auth, Billing", value="General").strip()
                new_desc = st.text_area("Detailed Description", placeholder="Enter functional specification details...")

            submit_req = st.form_submit_button("Save Requirement", type="primary")
            if submit_req:
                if not new_id or not new_title:
                    st.error("Requirement ID and Title are required!")
                else:
                    success = db.add_requirement(new_id, new_title, new_desc, new_priority, new_module)
                    if success:
                        st.success(f"Requirement **{new_id}** added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Requirement ID '{new_id}' already exists!")

    with tab_view:
        req_df = db.get_all_requirements()
        if req_df.empty:
            st.info("No requirements created yet.")
        else:
            st.dataframe(req_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### 🗑️ Delete Requirement")
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                selected_req = st.selectbox("Select Requirement to Delete", req_df["req_id"].tolist())
            with del_col2:
                st.write("")
                st.write("")
                if st.button("Delete Requirement", type="secondary"):
                    db.delete_requirement(selected_req)
                    st.warning(f"Requirement {selected_req} and associated links deleted.")
                    st.rerun()


# =============================================================
# 3. TEST CASES MANAGER
# =============================================================
elif menu == "🧪 Test Cases Manager":
    st.markdown("""
    <div class="section-title">🧪 Test Case Management & Execution Tracker</div>
    <div class="section-desc">Create verification tests and record execution outcomes (Passed, Failed, Blocked, Not Run).</div>
    """, unsafe_allow_html=True)

    tab_add_tc, tab_view_tc = st.tabs(["➕ Add New Test Case", "⚡ Execution & Status Tracker"])

    with tab_add_tc:
        with st.form("add_tc_form", clear_on_submit=True):
            tc_col1, tc_col2 = st.columns(2)
            with tc_col1:
                new_tc_id = st.text_input("Test ID *", placeholder="e.g. TC8, TEST-201").strip()
                new_tc_title = st.text_input("Test Title *", placeholder="e.g. Verify OTP verification timeout").strip()
                new_tc_type = st.selectbox("Test Type", ["Functional", "Integration", "Unit", "UI", "Security", "Performance"])
            with tc_col2:
                new_status = st.selectbox("Initial Execution Status", ["Not Run", "Passed", "Failed", "Blocked"])
                new_tc_desc = st.text_area("Test Steps / Preconditions", placeholder="1. Open login page\n2. Enter expired OTP\n3. Verify error message")
                new_notes = st.text_input("Execution Notes / Bug Ref", placeholder="e.g. Bug #104 filed in Jira")

            submit_tc = st.form_submit_button("Save Test Case", type="primary")
            if submit_tc:
                if not new_tc_id or not new_tc_title:
                    st.error("Test Case ID and Title are required!")
                else:
                    success = db.add_test_case(new_tc_id, new_tc_title, new_tc_desc, new_tc_type, new_status, new_notes)
                    if success:
                        st.success(f"Test Case **{new_tc_id}** added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Test Case ID '{new_tc_id}' already exists!")

    with tab_view_tc:
        tc_df = db.get_all_test_cases()
        if tc_df.empty:
            st.info("No test cases registered yet.")
        else:
            st.dataframe(tc_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ⚡ Quick Update Execution Result")
            up_col1, up_col2, up_col3, up_col4 = st.columns([2, 2, 3, 2])
            with up_col1:
                selected_tc = st.selectbox("Select Test Case", tc_df["test_id"].tolist())
            with up_col2:
                updated_status = st.selectbox("Execution Verdict", ["Passed", "Failed", "Blocked", "Not Run"])
            with up_col3:
                updated_note = st.text_input("Execution Note / Defect ID", placeholder="e.g. Verified in v1.1 or Bug #401")
            with up_col4:
                st.write("")
                st.write("")
                if st.button("💾 Update Verdict", type="primary"):
                    db.update_test_status(selected_tc, updated_status, updated_note)
                    st.success(f"Test {selected_tc} marked as **{updated_status}**")
                    st.rerun()

            st.markdown("---")
            if st.button("🗑️ Delete Selected Test Case", type="secondary"):
                db.delete_test_case(selected_tc)
                st.warning(f"Test Case {selected_tc} deleted.")
                st.rerun()


# =============================================================
# 4. LINK & MAP TESTS
# =============================================================
elif menu == "🔗 Link & Map Tests":
    st.markdown("""
    <div class="section-title">🔗 Requirement-to-Test Mapping</div>
    <div class="section-desc">Establish and audit many-to-many traceability relationships between requirements and test cases.</div>
    """, unsafe_allow_html=True)

    req_df = db.get_all_requirements()
    tc_df = db.get_all_test_cases()

    if req_df.empty or tc_df.empty:
        st.warning("Please add at least one Requirement and one Test Case before establishing links.")
    else:
        st.markdown("#### 🔗 Create New Traceability Link")
        link_col1, link_col2, link_col3 = st.columns([3, 3, 2])
        with link_col1:
            req_options = [f"{r['req_id']} - {r['title']}" for _, r in req_df.iterrows()]
            selected_req_str = st.selectbox("Select Requirement", req_options)
            chosen_req_id = selected_req_str.split(" - ")[0]
        with link_col2:
            tc_options = [f"{t['test_id']} - {t['title']} ({t['execution_status']})" for _, t in tc_df.iterrows()]
            selected_tc_str = st.selectbox("Select Test Case to Link", tc_options)
            chosen_tc_id = selected_tc_str.split(" - ")[0]
        with link_col3:
            st.write("")
            st.write("")
            if st.button("🔗 Link Test to Requirement", type="primary"):
                linked = db.link_requirement_test(chosen_req_id, chosen_tc_id)
                if linked:
                    st.success(f"Linked **{chosen_req_id}** ➔ **{chosen_tc_id}** successfully!")
                    st.rerun()
                else:
                    st.warning(f"Link between {chosen_req_id} and {chosen_tc_id} already exists!")

        st.markdown("---")
        st.markdown("#### 📋 Current Active Mappings")
        links_df = db.get_all_links()

        if links_df.empty:
            st.info("No links established yet. All requirements are currently Untested.")
        else:
            st.dataframe(links_df, use_container_width=True, hide_index=True)

            st.markdown("##### ✂️ Remove Mapping")
            del_link_col1, del_link_col2 = st.columns([4, 2])
            with del_link_col1:
                link_list = [f"{row['req_id']} ➔ {row['test_id']} ({row['req_title']} / {row['test_title']})" for _, row in links_df.iterrows()]
                selected_unlink = st.selectbox("Select Link to Remove", link_list)
            with del_link_col2:
                st.write("")
                st.write("")
                if st.button("Unlink Selected"):
                    parts = selected_unlink.split(" ➔ ")
                    r_id = parts[0]
                    t_id = parts[1].split(" (")[0]
                    db.unlink_requirement_test(r_id, t_id)
                    st.info(f"Unlinked {r_id} and {t_id}")
                    st.rerun()


# =============================================================
# 5. DEMO DATA & SETTINGS
# =============================================================
elif menu == "⚙️ Demo Data & Settings":
    st.markdown("""
    <div class="section-title">⚙️ Demonstration Controls & Scenario Reset</div>
    <div class="section-desc">Easily reset pre-configured evaluation scenarios or clear records for testing presentations.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b; margin-bottom: 8px;">🎓 College Login System Demo Scenario</div>
        <div style="font-size: 0.88rem; color: #475569; line-height: 1.5;">
            The pre-loaded demonstration scenario matches <strong>Problem Statement 80</strong>:
            <ul style="margin-top: 8px; padding-left: 20px;">
                <li><strong>R1 (User Login)</strong>: Linked to <code>TC1</code> (Passed) and <code>TC2</code> (Failed) ➔ Evaluated as <strong>Failed</strong> (Tested).</li>
                <li><strong>R2 (Password Reset)</strong>: Linked to <code>TC3</code> (Passed) ➔ Evaluated as <strong>Passed</strong> (Tested).</li>
                <li><strong>R3 (Logout)</strong>: No linked test cases ➔ Automatically flagged as <strong>Untested</strong> (Coverage Gap!).</li>
                <li><strong>R4 (Course Registration)</strong>: Linked to <code>TC4</code> (Passed) & <code>TC5</code> (Not Run) ➔ Evaluated as <strong>Partially Run</strong>.</li>
                <li><strong>R5 (Grade View)</strong>: No tests ➔ <strong>Untested</strong>.</li>
                <li><strong>R6 (Fee Payment Gateway)</strong>: Linked to <code>TC6</code> (Blocked) ➔ Evaluated as <strong>Blocked</strong>.</li>
                <li><strong>TC7 (Dark Mode Toggle)</strong>: Not linked to any requirement ➔ Detected as an <strong>Orphan Test</strong> in reverse view.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🔄 Reset / Reload College System Sample Data", type="primary"):
            db.seed_sample_data(force=True)
            st.success("Sample data reset successfully! You can now navigate back to 🏠 Home.")
            st.rerun()

    with btn_col2:
        if st.button("⚠️ Clear All Records"):
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM req_test_links")
            cur.execute("DELETE FROM test_cases")
            cur.execute("DELETE FROM requirements")
            conn.commit()
            conn.close()
            st.warning("All records wiped. You now have a clean slate.")
            st.rerun()
