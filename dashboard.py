import streamlit as st
import requests
import pandas as pd
import json

# st.set_page_config: Configures the page title and favicon
st.set_page_config(page_title="SENTINEL - AI Code Intelligence", page_icon="🔍")

# st.title: Displays the main header of the application
st.title("🔍 SENTINEL — AI Code Intelligence")

# st.text_input: Creates a text entry field for the user to provide the GitHub URL
repo_url = st.text_input("Enter GitHub Repository URL:", placeholder="https://github.com/user/repo")

# st.button: Creates a clickable button to trigger the analysis
if st.button("Analyze Repository"):
    if not repo_url:
        st.error("Please enter a URL first!")
    else:
        # st.spinner: Shows a loading indicator while the background task (API call) runs
        with st.spinner("5 agents analyzing your repository..."):
            try:
                # API Call to production SENTINEL backend
                response = requests.post(
                    "https://sentinel-production-e06b.up.railway.app/analyze",
                    json={"github_url": repo_url},
                    timeout=300
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. Metric Cards
                    # st.columns: Creates horizontal layout for the metric cards
                    cols = st.columns(len(data["agents"]) + 1)
                    
                    # st.metric: Displays a value with a label (Total Issues)
                    cols[0].metric("Total Issues", data["total_issues"])
                    
                    # Health Score
                    all_findings = []
                    for agent in data.get("agents", []):
                        all_findings.extend(agent.get("findings", []))

                    # Count severities
                    high_count = sum(1 for f in all_findings if f.get("severity") and ("high" in str(f.get("severity", "")).lower() or "critical" in str(f.get("severity", "")).lower()))
                    medium_count = sum(1 for f in all_findings if f.get("severity") and "medium" in str(f.get("severity", "")).lower() and "high" not in str(f.get("severity", "")).lower() and "critical" not in str(f.get("severity", "")).lower())
                    low_count = sum(1 for f in all_findings if f.get("severity") and "low" in str(f.get("severity", "")).lower())

                    total = high_count + medium_count + low_count
                    if total == 0:
                        health_score = 100
                    else:
                        weighted = high_count * 3 + medium_count * 1.5 + low_count * 0.5
                        max_weighted = total * 3
                        health_score = max(0, int(100 * (1 - weighted / max_weighted)))

                    st.subheader("Repository Health")
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric("Health Score", f"{health_score}/100")
                    with col2:
                        if health_score > 70:
                            st.success(f"Score: {health_score}/100 — Good")
                        elif health_score >= 40:
                            st.warning(f"Score: {health_score}/100 — Needs Work")
                        else:
                            st.error(f"Score: {health_score}/100 — Critical")
                        st.progress(health_score / 100)

                    # Findings by Agent (bar chart)
                    st.subheader("Findings by Agent")
                    agents_data = data.get("agents", [])
                    agent_names = [a.get("agent_name", "Unknown") for a in agents_data]
                    agent_counts = [a.get("findings_count", 0) for a in agents_data]

                    import pandas as pd
                    chart_df = pd.DataFrame({"Agent": agent_names, "Issues": agent_counts})
                    st.bar_chart(chart_df.set_index("Agent"))
                    
                    # 4. Findings Table
                    st.divider()
                    st.subheader("All Identified Issues")
                    
                    if all_findings:
                        # Prepare DataFrame for display
                        df = pd.DataFrame(all_findings)
                        
                        # Ensure important columns are first
                        cols_order = ["severity", "agent", "file", "issue", "type", "description", "suggestion", "fix", "recommendation"]
                        df = df[[c for c in cols_order if c in df.columns]]
                        
                        # Sort by severity: Critical > High > Medium > Low
                        severity_map = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
                        df["severity_rank"] = df["severity"].map(lambda x: severity_map.get(x, 4))
                        df = df.sort_values("severity_rank").drop(columns=["severity_rank"])
                        
                        # Color coding logic for the severity column
                        def color_severity(val):
                            if val in ["Critical", "High"]: return "color: red; font-weight: bold"
                            if val == "Medium": return "color: orange"
                            if val == "Low": return "color: gray"
                            return ""

                        # st.dataframe: Displays the findings in an interactive table
                        st.dataframe(df.style.applymap(color_severity, subset=["severity"]), use_container_width=True)
                        
                        # st.markdown: Explaining the color code as requested
                        st.markdown("""
                        **Severity Legend:**
                        - :red[Critical/High]: Immediate attention required.
                        - :orange[Medium]: Recommended improvements.
                        - :gray[Low]: Minor suggestions or documentation gaps.
                        """)
                        
                        # 5. Download as CSV
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Report as CSV",
                            data=csv,
                            file_name=f"sentinel_report_{data['repo_name']}.csv",
                            mime="text/csv",
                        )
                    else:
                        st.success("No issues found! Your repository is in great shape.")
                    
                else:
                    st.error(f"Analysis failed: {response.text}")
                    
            except Exception as e:
                # st.error: Displays an error message to the user
                st.error(f"An error occurred: {e}")

# Detailed explanation of st.* components used:
# - st.set_page_config: Initializes page-wide settings like title and icon.
# - st.title: Renders a large, bold title at the top of the app.
# - st.text_input: Provides a simple box for user text entry.
# - st.button: A standard UI button that returns True when clicked.
# - st.spinner: Wraps a block of code to show a loading animation until finished.
# - st.columns: Splits the layout into multiple vertical columns for side-by-side elements.
# - st.metric: A specialized component for displaying "big numbers" like counts or scores.
# - st.divider: Draws a horizontal line to separate sections.
# - st.subheader: Renders a medium-sized header for section titles.
# - st.markdown: Supports GitHub-flavored Markdown, including custom colors for text.
# - st.progress: Visualizes a numeric value (0.0 to 1.0) as a filled bar.
# - st.bar_chart: A built-in charting tool for quick visualization of categorical data.
# - st.dataframe: A powerful, sortable, and scrollable table for displaying large datasets.
# - st.download_button: Handles file generation and downloading for the user.
# - st.error: Displays a red alert box for exceptions or failures.
