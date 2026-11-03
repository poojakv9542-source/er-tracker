import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# ---------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ---------------------------------
# 2. LOAD CSV FILES
# ---------------------------------

def load_data(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        st.warning(f"{filename} is missing.")
        return pd.DataFrame()

    try:
        if file_path.stat().st_size == 0:
            st.warning(f"{filename} is empty.")
            return pd.DataFrame()

        return pd.read_csv(file_path)

    except pd.errors.EmptyDataError:
        st.warning(f"{filename} has no data.")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return pd.DataFrame()


semesters = load_data("semesters.csv")
courses = load_data("courses.csv")
calendar = load_data("academic_calendar.csv")
assessments = load_data("assessments.csv")
scores = load_data("scores.csv")


# ---------------------------------
# 3. PREPARE DATA
# ---------------------------------

if not assessments.empty and "date" in assessments.columns:
    assessments["date"] = pd.to_datetime(
        assessments["date"], errors="coerce"
    )

if not calendar.empty and "date" in calendar.columns:
    calendar["date"] = pd.to_datetime(
        calendar["date"], errors="coerce"
    )

total_credits = (
    semesters["total_credits"].sum()
    if "total_credits" in semesters.columns else 0
)

completed_credits = (
    semesters["completed_credits"].sum()
    if "completed_credits" in semesters.columns else 0
)

degree_progress = (
    completed_credits / total_credits * 100
    if total_credits > 0 else 0
)

current_semester = "Not set"

if not semesters.empty and "status" in semesters.columns:
    current = semesters[
        semesters["status"].astype(str).str.lower() == "in progress"
    ]

    if not current.empty:
        current_semester = int(current.iloc[0]["semester"])


# ---------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------

st.sidebar.title("🎓 Degree OS")
st.sidebar.caption("Your Engineering Companion")

pages = [
    "Dashboard",
    "Semester 1",
    "Semester 2",
    "Semester 3",
    "Semester 4",
    "Semester 5",
    "Semester 6",
    "Semester 7",
    "Semester 8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin"
]

selected_page = st.sidebar.radio(
    "Navigate",
    pages
)

st.sidebar.divider()
st.sidebar.write("**My Engineering Degree OS**")
st.sidebar.caption("Track • Plan • Achieve")


# ---------------------------------
# 5. DASHBOARD
# ---------------------------------

if selected_page == "Dashboard":

    st.title("🎓 My Engineering Degree OS")
    st.write("Your personal engineering academic dashboard.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Semester",
        current_semester
    )

    col2.metric(
        "Degree Completion",
        f"{degree_progress:.1f}%"
    )

    col3.metric(
        "Completed Credits",
        int(completed_credits)
    )

    col4.metric(
        "Total Credits",
        int(total_credits)
    )

    st.divider()

    # Degree progress
    st.subheader("📊 Overall Degree Progress")

    st.progress(min(max(degree_progress / 100, 0.0), 1.0))

    st.write(
        f"You have completed {completed_credits} "
        f"out of {total_credits} credits."
    )

    st.divider()

    # Upcoming events
    left, right = st.columns(2)

    with left:
        st.subheader("📝 Next Assessment")

        if not assessments.empty:
            upcoming = assessments[
                assessments["date"].notna()
                & (assessments["date"].dt.date >= date.today())
            ].sort_values("date")

            if not upcoming.empty:
                item = upcoming.iloc[0]

                st.info(
                    f"**{item['assessment_type']}**\n\n"
                    f"Course: {item['course_code']}\n\n"
                    f"Date: {item['date'].strftime('%d %B %Y')}\n\n"
                    f"Maximum Marks: {item['max_marks']}"
                )
            else:
                st.success("No upcoming assessments found.")
        else:
            st.info("Assessment data is not available.")

    with right:
        st.subheader("🎉 Next Holiday")

        if not calendar.empty:
            holidays = calendar[
                (calendar["event_type"].astype(str).str.lower() == "holiday")
                & calendar["date"].notna()
                & (calendar["date"].dt.date >= date.today())
            ].sort_values("date")

            if not holidays.empty:
                item = holidays.iloc[0]

                st.success(
                    f"**{item['title']}**\n\n"
                    f"Date: {item['date'].strftime('%d %B %Y')}"
                )
            else:
                st.info("No upcoming holidays found.")
        else:
            st.info("Calendar data is not available.")

    st.divider()

    # Semester progress chart
    st.subheader("📚 Semester-wise Credit Progress")

    if not semesters.empty:
        chart_data = semesters.set_index("semester")[
            ["completed_credits", "total_credits"]
        ]

        st.bar_chart(chart_data)

    else:
        st.info("Semester data is not available.")

    st.divider()

    # Score summary
    st.subheader("🏆 Score Summary")

    if not scores.empty and {"score", "max_marks"}.issubset(scores.columns):
        total_marks = scores["score"].sum()
        maximum_marks = scores["max_marks"].sum()

        percentage = (
            total_marks / maximum_marks * 100
            if maximum_marks > 0 else 0
        )

        st.metric("Overall Recorded Score", f"{percentage:.1f}%")

    else:
        st.info("No score records available yet.")

# ---------------------------------
# 6. SEMESTER PAGES
# ---------------------------------

elif selected_page.startswith("Semester"):

    semester_number = int(selected_page.split(" ")[1])

    st.title(f"📚 Semester {semester_number}")

    if not semesters.empty:

        semester_info = semesters[
            semesters["semester"] == semester_number
        ]

        if not semester_info.empty:

            info = semester_info.iloc[0]

            col1, col2, col3 = st.columns(3)

            col1.metric("Status", info["status"])
            col2.metric("Total Credits", info["total_credits"])
            col3.metric("Completed Credits", info["completed_credits"])

            progress = (
                info["completed_credits"] / info["total_credits"]
                if info["total_credits"] > 0 else 0
            )

            st.subheader("Semester Progress")
            st.progress(min(max(float(progress), 0.0), 1.0))

            st.write(f"{progress * 100:.1f}% completed")

    st.divider()

    st.subheader("📖 Subjects and Syllabus")

    if not courses.empty:

        semester_courses = courses[
            courses["semester"] == semester_number
        ]

        if not semester_courses.empty:

            for _, course in semester_courses.iterrows():

                with st.expander(
                    f"{course['course_code']} - {course['course_name']}"
                ):

                    st.write(f"**Credits:** {course['credits']}")

                    st.write(f"**Status:** {course['status']}")

                    st.write("**Syllabus:**")

                    topics = str(course["syllabus"]).split(";")

                    for topic in topics:
                        st.write(f"• {topic.strip()}")

        else:
            st.info("No subjects added for this semester.")

    else:
        st.warning("Course data is unavailable.")

# ---------------------------------
# 7. COURSES AND SYLLABUS
# ---------------------------------

elif selected_page == "Courses & Syllabus":

    st.title("📖 Courses & Syllabus")

    if not courses.empty:

        # Search
        search = st.text_input(
            "🔍 Search course",
            placeholder="Enter course name or course code"
        )

        # Semester filter
        semester_options = ["All"] + sorted(
            courses["semester"].dropna().unique().tolist()
        )

        selected_semester = st.selectbox(
            "Filter by Semester",
            semester_options
        )

        filtered_courses = courses.copy()

        if selected_semester != "All":
            filtered_courses = filtered_courses[
                filtered_courses["semester"] == selected_semester
            ]

        if search:
            filtered_courses = filtered_courses[
                filtered_courses["course_name"].str.contains(
                    search, case=False, na=False
                )
                | filtered_courses["course_code"].str.contains(
                    search, case=False, na=False
                )
            ]

        st.write(f"Total subjects found: {len(filtered_courses)}")

        st.divider()

        for _, course in filtered_courses.iterrows():

            with st.expander(
                f"📘 {course['course_code']} - {course['course_name']}"
            ):

                col1, col2 = st.columns(2)

                col1.write(f"**Semester:** {course['semester']}")
                col2.write(f"**Credits:** {course['credits']}")

                st.write(f"**Status:** {course['status']}")

                st.write("**Syllabus Topics:**")

                topics = str(course["syllabus"]).split(";")

                for topic in topics:
                    st.write(f"• {topic.strip()}")

    else:
        st.warning("No courses available.")
# ---------------------------------
# 8. UNIVERSITY SYLLABUS
# ---------------------------------

elif selected_page == "University Syllabus":

    st.title("🏛️ University Syllabus")

    st.write(
        "Upload and manage your official university syllabus "
        "semester by semester."
    )

    SYLLABUS_DIR = DATA_DIR / "university_syllabus"
    SYLLABUS_DIR.mkdir(parents=True, exist_ok=True)

    semester = st.selectbox(
        "Select Semester",
        [1, 2, 3, 4, 5, 6, 7, 8]
    )

    st.subheader("📤 Upload Syllabus")

    uploaded_file = st.file_uploader(
        "Upload your university syllabus PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Save Syllabus"):

            file_name = (
                f"Semester_{semester}_{Path(uploaded_file.name).name}"
            )

            file_path = SYLLABUS_DIR / file_name

            file_path.write_bytes(uploaded_file.getvalue())

            st.success("Syllabus uploaded successfully!")

    st.divider()

    st.subheader("📚 Uploaded Syllabus Documents")

    files = sorted(
        SYLLABUS_DIR.glob("Semester_*.pdf")
    )

    semester_files = [
        file for file in files
        if file.name.startswith(f"Semester_{semester}_")
    ]

    if semester_files:

        for file in semester_files:

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"📄 {file.name}")

            with col2:
                with open(file, "rb") as pdf_file:
                    st.download_button(
                        "Download",
                        data=pdf_file.read(),
                        file_name=file.name,
                        mime="application/pdf",
                        key=file.name
                    )

    else:
        st.info(
            f"No syllabus uploaded for Semester {semester} yet."
        )
# ---------------------------------
# 9. ACADEMIC / LEAVE CALENDAR
# ---------------------------------

elif selected_page == "Academic / Leave Calendar":

    st.title("📅 Academic / Leave Calendar")

    st.write(
        "Manage your academic events, examinations, "
        "assignments and holidays."
    )

    # Add new event
    st.subheader("➕ Add New Event")

    with st.form("add_calendar_event"):

        academic_year = st.text_input(
            "Academic Year",
            value="2026-27"
        )

        semester = st.selectbox(
            "Semester",
            [1, 2, 3, 4, 5, 6, 8]
        )

        event_date = st.date_input(
            "Event Date"
        )

        event_type = st.selectbox(
            "Event Type",
            [
                "Academic",
                "Holiday",
                "Examination",
                "Assignment",
                "Personal"
            ]
        )

        event_title = st.text_input(
            "Event Title",
            placeholder="Example: Internal Assessment 1"
        )

        submitted = st.form_submit_button("Save Event")

        if submitted:

            if event_title.strip():

                new_event = pd.DataFrame([{
                    "academic_year": academic_year,
                    "semester": semester,
                    "date": event_date.strftime("%Y-%m-%d"),
                    "event_type": event_type,
                    "title": event_title.strip()
                }])

                calendar_file = DATA_DIR / "academic_calendar.csv"

                if calendar_file.exists() and calendar_file.stat().st_size > 0:
                    existing_calendar = pd.read_csv(calendar_file)
                    updated_calendar = pd.concat(
                        [existing_calendar, new_event],
                        ignore_index=True
                    )
                else:
                    updated_calendar = new_event

                updated_calendar.to_csv(
                    calendar_file,
                    index=False
                )

                st.success("Event saved successfully!")

                st.rerun()

            else:
                st.error("Please enter an event title.")

    st.divider()

    # Display calendar events
    st.subheader("📚 Academic Events")

    calendar_file = DATA_DIR / "academic_calendar.csv"

    if calendar_file.exists() and calendar_file.stat().st_size > 0:

        calendar_display = pd.read_csv(calendar_file)

        calendar_display["date"] = pd.to_datetime(
            calendar_display["date"],
            errors="coerce"
        )

        calendar_display = calendar_display.sort_values("date")

        st.dataframe(
            calendar_display,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🔍 Filter Events")

        event_filter = st.selectbox(
            "Select Event Type",
            ["All", "Academic", "Holiday", "Examination",
             "Assignment", "Personal"]
        )

        if event_filter != "All":

            filtered_events = calendar_display[
                calendar_display["event_type"] == event_filter
            ]

        else:
            filtered_events = calendar_display

        st.dataframe(
            filtered_events,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No academic events available yet.")

# ---------------------------------
# 10. INTERNAL ASSESSMENTS
# ---------------------------------

elif selected_page == "Internal Assessments":

    st.title("📝 Internal Assessments")

    st.write(
        "Manage your internal exams, assignments, "
        "lab evaluations and assessment marks."
    )

    assessments_file = DATA_DIR / "assessments.csv"

    # Add assessment
    st.subheader("➕ Add New Assessment")

    with st.form("add_assessment"):

        col1, col2 = st.columns(2)

        with col1:
            semester = st.selectbox(
                "Semester",
                [1, 2, 3, 4, 5, 6, 8]
            )

            course_code = st.text_input(
                "Course Code",
                placeholder="Example: CS301"
            )

            assessment_type = st.selectbox(
                "Assessment Type",
                [
                    "IA1",
                    "IA2",
                    "IA3",
                    "Assignment",
                    "Lab Evaluation",
                    "Project Review",
                    "End Semester"
                ]
            )

        with col2:
            assessment_date = st.date_input(
                "Assessment Date"
            )

            max_marks = st.number_input(
                "Maximum Marks",
                min_value=1,
                max_value=1000,
                value=30
            )

            status = st.selectbox(
                "Status",
                ["Planned", "Completed", "Cancelled"]
            )

        submitted = st.form_submit_button(
            "Save Assessment"
        )

        if submitted:

            if course_code.strip():

                new_assessment = pd.DataFrame([{
                    "semester": semester,
                    "course_code": course_code.strip().upper(),
                    "assessment_type": assessment_type,
                    "date": assessment_date.strftime("%Y-%m-%d"),
                    "max_marks": max_marks,
                    "status": status
                }])

                if assessments_file.exists() and assessments_file.stat().st_size > 0:

                    existing = pd.read_csv(assessments_file)

                    updated = pd.concat(
                        [existing, new_assessment],
                        ignore_index=True
                    )

                else:
                    updated = new_assessment

                updated.to_csv(
                    assessments_file,
                    index=False
                )

                st.success("Assessment saved successfully!")

                st.rerun()

            else:
                st.error("Please enter a course code.")

    st.divider()

    # Display assessments
    st.subheader("📚 Assessment Records")

    if assessments_file.exists() and assessments_file.stat().st_size > 0:

        assessment_data = pd.read_csv(assessments_file)

        assessment_data["date"] = pd.to_datetime(
            assessment_data["date"],
            errors="coerce"
        )

        col1, col2 = st.columns(2)

        with col1:
            semester_filter = st.selectbox(
                "Filter by Semester",
                ["All", 1, 2, 3, 4, 5, 6, 8]
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Planned", "Completed", "Cancelled"]
            )

        filtered = assessment_data.copy()

        if semester_filter != "All":
            filtered = filtered[
                filtered["semester"] == semester_filter
            ]

        if status_filter != "All":
            filtered = filtered[
                filtered["status"] == status_filter
            ]

        filtered = filtered.sort_values("date")

        st.write(f"Total assessments displayed: {len(filtered)}")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No assessment records available yet.")


# ---------------------------------
# 11. STATUS TRACKER
# ---------------------------------

elif selected_page == "Status Tracker":

    st.title("📊 Academic Status Tracker")

    st.write(
        "Track your subject completion and update your academic progress."
    )

    courses_file = DATA_DIR / "courses.csv"

    if courses_file.exists() and courses_file.stat().st_size > 0:

        course_data = pd.read_csv(courses_file)

        # Status summary
        st.subheader("📈 Subject Progress")

        completed = (
            course_data["status"] == "Completed"
        ).sum()

        in_progress = (
            course_data["status"] == "In Progress"
        ).sum()

        not_started = (
            course_data["status"] == "Not Started"
        ).sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Completed", int(completed))
        col2.metric("In Progress", int(in_progress))
        col3.metric("Not Started", int(not_started))

        st.divider()

        # Semester filter
        st.subheader("📚 Subject Status")

        semester_options = ["All"] + sorted(
            course_data["semester"].dropna().unique().tolist()
        )

        selected_semester = st.selectbox(
            "Filter by Semester",
            semester_options
        )

        filtered_courses = course_data.copy()

        if selected_semester != "All":
            filtered_courses = filtered_courses[
                filtered_courses["semester"] == selected_semester
            ]

        st.dataframe(
            filtered_courses[
                ["semester", "course_code", "course_name", "status"]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Update subject status
        st.subheader("✏️ Update Subject Status")

        course_options = {
            f"{row['course_code']} - {row['course_name']} (Semester {row['semester']})": index
            for index, row in course_data.iterrows()
        }

        selected_course = st.selectbox(
            "Select Subject",
            list(course_options.keys())
        )

        selected_index = course_options[selected_course]

        current_status = course_data.loc[
            selected_index, "status"
        ]

        status_options = [
            "Not Started",
            "In Progress",
            "Completed"
        ]

        new_status = st.selectbox(
            "Choose New Status",
            status_options,
            index=(
                status_options.index(current_status)
                if current_status in status_options else 0
            )
        )

        if st.button("Save Status"):

            course_data.loc[
                selected_index, "status"
            ] = new_status

            course_data.to_csv(
                courses_file,
                index=False
            )

            st.success("Subject status updated successfully!")

            st.rerun()

    else:
        st.warning("Course data is missing or empty.")



# ---------------------------------
# 12. SCORECARD
# ---------------------------------

elif selected_page == "Scorecard":

    st.title("🏆 Academic Scorecard")

    st.write(
        "Record your academic marks and monitor your performance."
    )

    scores_file = DATA_DIR / "scores.csv"

    # Load score records
    if scores_file.exists() and scores_file.stat().st_size > 0:
        score_data = pd.read_csv(scores_file)
    else:
        score_data = pd.DataFrame(columns=[
            "semester",
            "course_code",
            "assessment_type",
            "score",
            "max_marks",
            "grade"
        ])

    # Add new marks
    st.subheader("➕ Add New Marks")

    with st.form("add_score"):

        col1, col2 = st.columns(2)

        with col1:

            semester = st.selectbox(
                "Semester",
                [1, 2, 3, 4, 5, 6, 8]
            )

            course_code = st.text_input(
                "Course Code",
                placeholder="Example: CS301"
            )

            assessment_type = st.selectbox(
                "Assessment Type",
                [
                    "IA1",
                    "IA2",
                    "IA3",
                    "Assignment",
                    "Lab Evaluation",
                    "End Semester"
                ]
            )

        with col2:

            score = st.number_input(
                "Marks Obtained",
                min_value=0.0,
                value=0.0
            )

            max_marks = st.number_input(
                "Maximum Marks",
                min_value=1.0,
                value=30.0
            )

        submitted = st.form_submit_button("Save Marks")

        if submitted:

            if not course_code.strip():
                st.error("Please enter a course code.")

            elif score > max_marks:
                st.error("Marks obtained cannot exceed maximum marks.")

            else:

                percentage = (score / max_marks) * 100

                if percentage >= 90:
                    grade = "A+"
                elif percentage >= 80:
                    grade = "A"
                elif percentage >= 70:
                    grade = "B+"
                elif percentage >= 60:
                    grade = "B"
                elif percentage >= 50:
                    grade = "C"
                else:
                    grade = "Needs Improvement"

                new_score = pd.DataFrame([{
                    "semester": semester,
                    "course_code": course_code.strip().upper(),
                    "assessment_type": assessment_type,
                    "score": score,
                    "max_marks": max_marks,
                    "grade": grade
                }])

                score_data = pd.concat(
                    [score_data, new_score],
                    ignore_index=True
                )

                score_data.to_csv(
                    scores_file,
                    index=False
                )

                st.success("Marks saved successfully!")

                st.rerun()

    st.divider()

    # Performance summary
    st.subheader("📊 Performance Summary")

    if not score_data.empty:

        total_marks = pd.to_numeric(
            score_data["score"], errors="coerce"
        ).fillna(0).sum()

        maximum_marks = pd.to_numeric(
            score_data["max_marks"], errors="coerce"
        ).fillna(0).sum()

        percentage = (
            total_marks / maximum_marks * 100
            if maximum_marks > 0 else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Marks Obtained", f"{total_marks:g}")
        col2.metric("Maximum Marks", f"{maximum_marks:g}")
        col3.metric("Overall Percentage", f"{percentage:.2f}%")

        st.progress(min(max(percentage / 100, 0.0), 1.0))

        st.divider()

        # Semester filter
        st.subheader("📚 Semester-wise Scorecard")

        semester_filter = st.selectbox(
            "Select Semester",
            ["All", 1, 2, 3, 4, 5, 6, 8]
        )

        filtered_scores = score_data.copy()

        if semester_filter != "All":
            filtered_scores = filtered_scores[
                pd.to_numeric(
                    filtered_scores["semester"],
                    errors="coerce"
                ) == semester_filter
            ]

        st.dataframe(
            filtered_scores,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No marks recorded yet. Add your first score above.")




# ---------------------------------
# 13. PLAN AND CHECKLIST
# ---------------------------------

elif selected_page == "Plan & Checklist":

    st.title("✅ Plan & Checklist")

    st.write(
        "Organize your assignments, study plans, "
        "projects and academic deadlines."
    )

    plan_file = DATA_DIR / "plan_checklist.csv"

    # Load tasks
    columns = [
        "task_id",
        "task_name",
        "category",
        "semester",
        "due_date",
        "priority",
        "status"
    ]

    if plan_file.exists() and plan_file.stat().st_size > 0:
        tasks = pd.read_csv(plan_file)
    else:
        tasks = pd.DataFrame(columns=columns)

    # Add new task
    st.subheader("➕ Add New Task")

    with st.form("add_task"):

        task_name = st.text_input(
            "Task Name",
            placeholder="Example: Complete DBMS assignment"
        )

        col1, col2 = st.columns(2)

        with col1:

            category = st.selectbox(
                "Category",
                [
                    "Assignment",
                    "Study",
                    "Project",
                    "Exam Preparation",
                    "Personal"
                ]
            )

            semester = st.selectbox(
                "Semester",
                [1, 2, 3, 4, 5, 6, 8]
            )

        with col2:

            due_date = st.date_input("Due Date")

            priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"]
            )

        submitted = st.form_submit_button("Add Task")

        if submitted:

            if task_name.strip():

                new_task = pd.DataFrame([{
                    "task_id": (
                        int(pd.to_numeric(
                            tasks["task_id"], errors="coerce"
                        ).max()) + 1
                        if not tasks.empty else 1
                    ),
                    "task_name": task_name.strip(),
                    "category": category,
                    "semester": semester,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "priority": priority,
                    "status": "Pending"
                }])

                tasks = pd.concat(
                    [tasks, new_task],
                    ignore_index=True
                )

                tasks.to_csv(plan_file, index=False)

                st.success("Task added successfully!")
                st.rerun()

            else:
                st.error("Please enter a task name.")

    st.divider()

    # Task summary
    st.subheader("📊 Task Summary")

    if not tasks.empty:

        completed = (tasks["status"] == "Completed").sum()
        pending = (tasks["status"] == "Pending").sum()
        in_progress = (tasks["status"] == "In Progress").sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Completed", int(completed))
        col2.metric("Pending", int(pending))
        col3.metric("In Progress", int(in_progress))

        st.divider()

        # Display tasks
        st.subheader("📋 My Tasks")

        tasks["due_date"] = pd.to_datetime(
            tasks["due_date"], errors="coerce"
        )

        st.dataframe(
            tasks.sort_values("due_date"),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Update task
        st.subheader("✏️ Update Task Status")

        task_options = {
            f"{row['task_id']} - {row['task_name']}": index
            for index, row in tasks.iterrows()
        }

        selected_task = st.selectbox(
            "Select Task",
            list(task_options.keys())
        )

        selected_index = task_options[selected_task]

        status_options = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        current_status = tasks.loc[
            selected_index, "status"
        ]

        new_status = st.selectbox(
            "New Status",
            status_options,
            index=(
                status_options.index(current_status)
                if current_status in status_options else 0
            )
        )

        if st.button("Update Task"):

            tasks.loc[
                selected_index, "status"
            ] = new_status

            tasks.to_csv(
                plan_file,
                index=False
            )

            st.success("Task status updated!")
            st.rerun()

    else:
        st.info("No tasks added yet. Create your first task above.")
  


# ---------------------------------
# 14. ASK DEGREE AI
# ---------------------------------

elif selected_page == "Ask Degree AI":

    st.title("🤖 Ask Degree AI")

    st.write(
        "Your personal academic assistant. "
        "Ask questions about your engineering degree."
    )

    st.divider()

    question = st.text_input(
        "Ask your academic question",
        placeholder="Example: What subjects do I have in Semester 3?"
    )

    if st.button("Ask Degree AI"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            q = question.lower()

            st.subheader("💬 Degree AI Response")

            # Semester and credit questions
            if any(word in q for word in [
                "credit", "degree progress", "completed"
            ]):

                st.write(
                    f"You have completed {completed_credits} "
                    f"out of {total_credits} credits."
                )

                st.write(
                    f"Your degree completion is "
                    f"{degree_progress:.1f}%."
                )

                st.write(
                    f"Your current semester is {current_semester}."
                )

            # Course and syllabus questions
            elif any(word in q for word in [
                "subject", "course", "syllabus", "topic"
            ]):

                if not courses.empty:

                    semester_number = None

                    for number in [1, 2, 3, 4, 5, 6, 8]:
                        if f"semester {number}" in q or f"sem {number}" in q:
                            semester_number = number
                            break

                    if semester_number is not None:

                        result = courses[
                            courses["semester"] == semester_number
                        ]

                        if not result.empty:

                            for _, course in result.iterrows():

                                st.markdown(
                                    f"**{course['course_code']} - "
                                    f"{course['course_name']}**"
                                )

                                st.write(
                                    f"Credits: {course['credits']}"
                                )

                                st.write(
                                    f"Syllabus: {course['syllabus']}"
                                )

                                st.write(
                                    f"Status: {course['status']}"
                                )

                        else:
                            st.info(
                                "No subjects found for this semester."
                            )

                    else:

                        matching = courses[
                            courses["course_name"].astype(str).str.contains(
                                question, case=False, na=False
                            )
                            |
                            courses["course_code"].astype(str).str.contains(
                                question, case=False, na=False
                            )
                        ]

                        if not matching.empty:
                            st.dataframe(
                                matching,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info(
                                "Try asking about a specific semester, "
                                "course name or course code."
                            )

                else:
                    st.info("Course information is unavailable.")

            # Assessment questions
            elif any(word in q for word in [
                "assessment", "exam", "test", "ia"
            ]):

                if not assessments.empty:

                    st.write("Here are your assessment records:")

                    st.dataframe(
                        assessments,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info("No assessment records are available.")

            # Marks and grades
            elif any(word in q for word in [
                "mark", "score", "grade", "percentage", "result"
            ]):

                if not scores.empty:

                    st.write("Your recorded academic scores:")

                    st.dataframe(
                        scores,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info("No marks have been recorded yet.")

            # Task and assignment questions
            elif any(word in q for word in [
                "task", "assignment", "checklist", "deadline"
            ]):

                plan_file = DATA_DIR / "plan_checklist.csv"

                if plan_file.exists() and plan_file.stat().st_size > 0:

                    tasks = pd.read_csv(plan_file)

                    st.write("Your academic tasks:")

                    st.dataframe(
                        tasks,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info("No academic tasks are available.")

            else:

                st.info(
                    "I couldn't identify that question from your "
                    "academic records. Try asking about courses, "
                    "credits, assessments, marks or assignments."
                )

    st.divider()

    st.subheader("💡 Example Questions")

    examples = [
        "What is my degree completion percentage?",
        "What subjects do I have in Semester 3?",
        "Show my assessment records",
        "What are my recorded marks?",
        "Show my pending assignments"
    ]

    for example in examples:
        st.write(f"• {example}")


elif selected_page == "Data Admin":
    st.title("🗂️ Data Admin")
    st.write("Check and preview the CSV files used by your Engineering Degree OS.")

    data_files = {
        "Semesters": "semesters.csv",
        "Courses": "courses.csv",
        "Academic Calendar": "academic_calendar.csv",
        "Assessments": "assessments.csv",
        "Scores": "scores.csv",
        "Plan & Checklist": "plan_checklist.csv"
    }

    st.subheader("CSV File Status")

    for label, filename in data_files.items():
        file_path = DATA_DIR / filename

        if not file_path.exists():
            st.error(f"❌ {label}: File is missing")
        elif file_path.stat().st_size == 0:
            st.warning(f"⚠️ {label}: File is empty")
        else:
            st.success(f"✅ {label}: File available")

    st.divider()

    st.subheader("Preview CSV Data")

    selected_file = st.selectbox(
        "Choose a file to preview",
        list(data_files.keys())
    )

    filename = data_files[selected_file]
    file_path = DATA_DIR / filename

    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            preview_data = pd.read_csv(file_path)

            st.write(f"**File:** {filename}")
            st.write(f"**Total rows:** {len(preview_data)}")

            st.dataframe(
                preview_data,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Could not read this file: {e}")
    else:
        st.warning("This file is missing or empty.")