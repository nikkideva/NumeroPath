import datetime
import re
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIG & SESSION STATE
# ---------------------------------------------------------
st.set_page_config(
    page_title="NumeroPath V2.4 | Vehicle & Personal Harmonizer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "purpose" not in st.session_state:
    st.session_state.purpose = "New Vehicle"

if "generated" not in st.session_state:
    st.session_state.generated = False

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "session_reset_counter" not in st.session_state:
    st.session_state.session_reset_counter = 0

if "candidate_text_val" not in st.session_state:
    st.session_state.candidate_text_val = ""

if "logs" not in st.session_state:
    st.session_state.logs = [
        {
            "Time": "10:15 AM",
            "Purpose": "New Vehicle",
            "DOB": "Provided",
            "Name": "Blank",
            "Birth Place": "Blank",
            "Primary No": 7,
            "Name No": "-",
        },
        {
            "Time": "10:42 AM",
            "Purpose": "Mobile Number",
            "DOB": "Provided",
            "Name": "Entered",
            "Birth Place": "Entered",
            "Primary No": 5,
            "Name No": 3,
        },
        {
            "Time": "11:05 AM",
            "Purpose": "Name Check",
            "DOB": "Blank",
            "Name": "Entered",
            "Birth Place": "Blank",
            "Primary No": 6,
            "Name No": 6,
        },
    ]

# ---------------------------------------------------------
# 2. NUMEROLOGY & CANDIDATE RATING LOGIC
# ---------------------------------------------------------
PYTHAGOREAN_MAP = {
    "A": 1, "J": 1, "S": 1,
    "B": 2, "K": 2, "T": 2,
    "C": 3, "L": 3, "U": 3,
    "D": 4, "M": 4, "V": 4,
    "E": 5, "N": 5, "W": 5,
    "F": 6, "O": 6, "X": 6,
    "G": 7, "P": 7, "Y": 7,
    "H": 8, "Q": 8, "Z": 8,
    "I": 9, "R": 9,
}

ARCHETYPES = {
    1: ("The Pioneer", "Sun", "Independent, assertive, and forward-driving."),
    2: ("The Harmonizer", "Moon", "Cooperative, intuitive, and balanced."),
    3: ("The Communicator", "Jupiter", "Expressive, creative, and socially dynamic."),
    4: ("The Master Builder", "Uranus / Rahu", "Practical, disciplined, grounding, and suited for enduring physical systems."),
    5: ("The Catalyst", "Mercury", "Adaptable, swift, and strong for movement and communication."),
    6: ("The Guardian", "Venus", "Comfort-focused, dependable, and harmonious."),
    7: ("The Seeker", "Ketu", "Analytical, steady, and focused on purposeful travel."),
    8: ("The Strategist", "Saturn", "Ambitious, structured, and long-horizon oriented."),
    9: ("The Trailblazer", "Mars", "Energetic, decisive, and resilient."),
}

COMPATIBILITY = {
    1: {"seed": [1, 2, 3, 9], "caution": 8, "affinity": "1 & 3 (96% Match)"},
    2: {"seed": [1, 2, 5, 7], "caution": 4, "affinity": "2 & 5 (94% Match)"},
    3: {"seed": [1, 2, 3, 9], "caution": 6, "affinity": "3 & 9 (95% Match)"},
    4: {"seed": [1, 4, 7, 8], "caution": 2, "affinity": "1 & 4 (98% Match)"},
    5: {"seed": [1, 4, 5, 6], "caution": 2, "affinity": "5 & 1 (96% Match)"},
    6: {"seed": [4, 5, 6, 8], "caution": 3, "affinity": "6 & 5 (95% Match)"},
    7: {"seed": [2, 5, 7, 9], "caution": 8, "affinity": "7 & 2 (97% Match)"},
    8: {"seed": [4, 5, 6, 8], "caution": 1, "affinity": "8 & 6 (95% Match)"},
    9: {"seed": [1, 3, 7, 9], "caution": 4, "affinity": "9 & 3 (96% Match)"},
}


def reduce_to_single_digit(num: int) -> int:
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num


def calculate_dob_details(dob: datetime.date) -> tuple[int, int, str]:
    digits_str = f"{dob.year}{dob.month:02d}{dob.day:02d}"
    raw_sum = sum(int(d) for d in digits_str)
    reduced = reduce_to_single_digit(raw_sum)
    expr = " + ".join(digits_str) + f" = {raw_sum}"
    if raw_sum != reduced:
        expr += f" → {reduced}"
    return reduced, raw_sum, expr


def calculate_name_number(name: str) -> int | None:
    cleaned = [ch for ch in name.upper() if ch in PYTHAGOREAN_MAP]
    if not cleaned:
        return None
    return reduce_to_single_digit(sum(PYTHAGOREAN_MAP[ch] for ch in cleaned))


def build_recommendations(purpose: str, primary: int, seed_nums: list[int], sub_option: str) -> list[tuple[str, str]]:
    n1, n2, n3 = seed_nums[0], seed_nums[1], seed_nums[2]
    if purpose == "New Vehicle":
        return [
            (f"{n1}0{n2 if n2 != n1 else n3}", f"Sum = {reduce_to_single_digit(n1 + n2)} ({sub_option})"),
            (f"{n3}00{n1}", f"Aligned Plate Root {primary}"),
            (f"{n2}{n2}{n3}", f"Sum = {reduce_to_single_digit(n2 + n2 + n3)} (Steady Flow)"),
        ]
    if purpose == "Mobile Number":
        return [
            (f"...{n1}{n2}{primary}", f"Ending Sum = {reduce_to_single_digit(n1 + n2 + primary)} ({sub_option})"),
            (f"...{n3}0{n1}", f"Clear Recall & Resonance"),
            (f"...{n2}{n3}{n3}", f"Balanced Communication Tail"),
        ]
    if purpose == "Name Check":
        return [
            (f"Root {primary}", f"Primary Expression ({sub_option})"),
            (f"Pair {n1} / {n2}", "Harmonious Companion Digits"),
            (f"Alt {n3}", "Secondary Balance Check"),
        ]
    return [
        (f"No. {primary}", f"Core Milestone Digit ({sub_option})"),
        (f"Dates {n1}, {n2}", "Favorable Monthly Dates"),
        (f"Backup {n3}", "Supporting Decision Choice"),
    ]


def parse_candidate_numbers(raw_text: str) -> list[str]:
    tokens = re.split(r"[\s,;|/]+", raw_text.strip())
    candidates: list[str] = []
    for tok in tokens:
        digits_only = re.sub(r"[^0-9]", "", tok)
        if digits_only and digits_only not in candidates:
            candidates.append(digits_only)
    return candidates


def rate_candidate_number(num_str: str, primary: int, seed_nums: list[int], caution: int) -> dict:
    digits = [int(d) for d in num_str]
    digit_sum = sum(digits)
    reduced_root = reduce_to_single_digit(digit_sum)
    last_digit = digits[-1]

    score = 55
    reasons: list[str] = []

    if reduced_root == primary:
        score += 25
        reasons.append(f"Digit sum reduces to Primary {primary}")
    elif reduced_root in seed_nums:
        score += 15
        reasons.append(f"Digit sum matches Seed {reduced_root}")
    elif reduced_root == caution:
        score -= 20
        reasons.append(f"Digit sum hits Caution {caution}")
    else:
        reasons.append(f"Digit sum reduces to {reduced_root}")

    if last_digit == primary:
        score += 15
        reasons.append(f"Ends with Primary {primary}")
    elif last_digit in seed_nums:
        score += 10
        reasons.append(f"Ends with Seed {last_digit}")
    elif last_digit == caution:
        score -= 18
        reasons.append(f"Ends with Caution {caution}")

    score = max(10, min(99, score))
    stars = max(1, min(5, round(score / 20)))
    star_str = "★" * stars + "☆" * (5 - stars)

    if score >= 85:
        tier = "Best Match"
    elif score >= 68:
        tier = "Good Fit"
    elif score >= 50:
        tier = "Neutral"
    else:
        tier = "Low Priority"

    return {
        "Candidate": num_str,
        "Rating Score": f"{score}/100",
        "Stars": star_str,
        "Tier": tier,
        "Digit Sum": f"{digit_sum} → {reduced_root}",
        "Ending Digit": last_digit,
        "Why Rated": "; ".join(reasons),
        "_numeric_score": score,
    }


# ---------------------------------------------------------
# 3. CUSTOM STYLING
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
        }
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
            max-width: 1240px;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        .brand-box {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding-bottom: 0.5rem;
        }
        .brand-icon {
            width: 34px;
            height: 34px;
            border-radius: 9px;
            background: #e11d48;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1rem;
        }
        .brand-name {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.1;
        }
        .brand-ver {
            background: #ffe4e6;
            color: #be123c;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 0.1rem 0.45rem;
            border-radius: 999px;
            margin-left: 0.25rem;
        }
        .brand-sub {
            font-size: 0.72rem;
            color: #64748b;
        }
        .sidebar-section-title {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #94a3b8;
            margin: 1rem 0 0.45rem 0;
        }
        .notes-card {
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 10px;
            padding: 0.85rem 0.9rem;
            font-size: 0.78rem;
            color: #451a03;
            margin-top: 0.75rem;
        }
        .notes-title {
            font-weight: 700;
            color: #92400e;
            margin-bottom: 0.45rem;
            font-size: 0.8rem;
        }
        .notes-card ul {
            margin: 0;
            padding-left: 1rem;
        }
        .notes-card li {
            margin-bottom: 0.4rem;
            line-height: 1.35;
        }
        .status-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.72rem;
            color: #64748b;
            padding-top: 0.75rem;
            margin-top: 0.75rem;
            border-top: 1px solid #f1f5f9;
        }
        .status-online {
            color: #059669;
            font-weight: 700;
        }

        /* Top Header Strip */
        .breadcrumb {
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 0.2rem;
        }
        .page-top-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
        }
        .mode-pill {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.35rem 0.7rem;
            font-size: 0.76rem;
            color: #334155;
            font-weight: 500;
            display: inline-block;
        }

        /* Dark Hero Banner */
        .dark-hero {
            background:
                radial-gradient(circle at 82% 38%, rgba(99, 102, 241, 0.28), transparent 36%),
                radial-gradient(circle at 92% 75%, rgba(225, 29, 72, 0.22), transparent 35%),
                linear-gradient(120deg, #0b1120 0%, #111c3a 55%, #172554 100%);
            color: #f8fafc;
            border-radius: 14px;
            padding: 1.65rem 2rem;
            margin: 0.85rem 0 1.4rem 0;
            border: 1px solid #1e293b;
        }
        .dark-hero-pill {
            display: inline-block;
            background: rgba(56, 189, 248, 0.14);
            color: #7dd3fc;
            border: 1px solid rgba(125, 211, 252, 0.25);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            margin-bottom: 0.65rem;
        }
        .dark-hero-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 0.4rem 0;
        }
        .dark-hero-desc {
            font-size: 0.9rem;
            color: #cbd5e1;
            max-width: 660px;
            line-height: 1.5;
            margin: 0 0 1rem 0;
        }
        .dark-hero-checks {
            display: flex;
            flex-wrap: wrap;
            gap: 1.25rem;
            font-size: 0.78rem;
            color: #e2e8f0;
            padding-top: 0.65rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Step Headers */
        .step-kicker {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #e11d48;
            margin-bottom: 0.15rem;
        }
        .step-heading-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.65rem;
        }
        .step-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
        }
        .step-hint {
            font-size: 0.76rem;
            color: #64748b;
        }

        /* Purpose Selector Cards */
        .purpose-card {
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.95rem 1rem 0.75rem 1rem;
            min-height: 112px;
        }
        .purpose-card-active {
            background: #fffafb;
            border: 1.5px solid #e11d48;
            box-shadow: 0 4px 14px rgba(225, 29, 72, 0.08);
        }
        .purpose-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .purpose-icon {
            width: 30px;
            height: 30px;
            border-radius: 8px;
            background: #f1f5f9;
            color: #334155;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            font-weight: 700;
        }
        .purpose-card-active .purpose-icon {
            background: #ffe4e6;
            color: #e11d48;
        }
        .radio-dot {
            width: 15px;
            height: 15px;
            border-radius: 999px;
            border: 1.5px solid #cbd5e1;
            display: inline-block;
        }
        .radio-dot-active {
            border: 4px solid #e11d48;
        }
        .purpose-name {
            font-size: 0.92rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.2rem;
        }
        .purpose-sub {
            font-size: 0.75rem;
            color: #64748b;
            line-height: 1.35;
        }

        /* Form & Button Styling */
        .field-subnote {
            font-size: 0.72rem;
            color: #64748b;
            margin-top: -0.35rem;
            margin-bottom: 0.35rem;
        }
        div.stButton > button[kind="primary"] {
            background-color: #e11d48;
            border: none;
            border-radius: 10px;
            padding: 0.65rem 1.25rem;
            font-weight: 600;
            font-size: 0.94rem;
            color: #ffffff;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #be123c;
        }

        /* Snapshot / Result Cards */
        .snapshot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1.25rem 0 0.7rem 0;
        }
        .snapshot-title {
            font-size: 0.92rem;
            font-weight: 700;
            color: #0f172a;
        }
        .snapshot-meta {
            font-size: 0.74rem;
            color: #64748b;
        }
        .snap-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.1rem 1.2rem;
            height: 100%;
        }
        .snap-kicker {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 0.45rem;
        }
        .snap-big-num {
            font-size: 1.65rem;
            font-weight: 800;
            color: #0f172a;
            margin-right: 0.4rem;
        }
        .snap-archetype {
            font-size: 0.92rem;
            font-weight: 700;
            color: #1e293b;
        }
        .snap-body {
            font-size: 0.78rem;
            color: #475569;
            line-height: 1.45;
            margin: 0.55rem 0 0.75rem 0;
        }
        .snap-foot {
            border-top: 1px solid #f1f5f9;
            padding-top: 0.5rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.74rem;
            color: #64748b;
        }
        .snap-foot strong {
            color: #0f172a;
        }
        .seed-chip {
            display: inline-block;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            color: #0f172a;
            font-weight: 700;
            font-size: 0.85rem;
            padding: 0.25rem 0.6rem;
            border-radius: 7px;
            margin-right: 0.35rem;
            margin-bottom: 0.4rem;
        }
        .rec-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.38rem 0;
            border-bottom: 1px solid #f1f5f9;
            font-size: 0.82rem;
        }
        .rec-row:last-child {
            border-bottom: none;
        }
        .rec-code {
            font-weight: 700;
            color: #0f172a;
        }
        .rec-tag {
            font-size: 0.72rem;
            font-weight: 600;
            color: #0284c7;
            background: #f0f9ff;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
        }

        /* Best Candidate Banner */
        .best-pick-box {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-top: 0.75rem;
            color: #14532d;
            font-size: 0.86rem;
        }

        /* Bottom Studio Footer */
        .app-footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            font-size: 0.74rem;
            color: #64748b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-box">
            <div class="brand-icon">+</div>
            <div>
                <div><span class="brand-name">NumeroPath</span><span class="brand-ver">V2.4</span></div>
                <div class="brand-sub">Personal & Business Numerology</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-title">Core Modules</div>', unsafe_allow_html=True)
    active_nav = st.radio(
        "Core Modules",
        ["Lucky Number Finder", "Dashboard & Logs", "Numerology Rules Guide"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section-title">Saved Repositories</div>', unsafe_allow_html=True)
    preset_choice = st.selectbox(
        "Calculation Presets",
        ["Standard Pythagorean", "Vehicle Plate Focus", "Mobile VIP Focus", "Name Resonance"],
        label_visibility="collapsed",
    )
    if preset_choice == "Vehicle Plate Focus":
        st.session_state.purpose = "New Vehicle"
    elif preset_choice == "Mobile VIP Focus":
        st.session_state.purpose = "Mobile Number"
    elif preset_choice == "Name Resonance":
        st.session_state.purpose = "Name Check"

    st.caption("🗂️ Saved Profiles (0)")

    st.markdown(
        """
        <div class="notes-card">
            <div class="notes-title">✦ Quick Formulation Notes</div>
            <ul>
                <li><strong>Birth Place</strong> is always optional for standard date/name calculations.</li>
                <li><strong>Name</strong> is evaluated using Pythagorean letter values for resonance checks.</li>
                <li>Available numbers can be pasted or uploaded to rank the best fit by rating.</li>
            </ul>
        </div>
        <div class="status-footer">
            <span>• Pythagorean Core v2.4</span>
            <span class="status-online">ONLINE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 5. VIEW 1: LUCKY NUMBER FINDER (MAIN STUDIO VIEW)
# ---------------------------------------------------------
if active_nav == "Lucky Number Finder":
    top_l, top_r = st.columns([3, 1.4], vertical_alignment="center")
    with top_l:
        st.markdown(
            f"""
            <div class="breadcrumb">Studio Workspace &nbsp;/&nbsp; Calculators &nbsp;/&nbsp; <strong>{st.session_state.purpose}</strong></div>
            <h2 class="page-top-title">Vehicle & Personal Harmonizer</h2>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        r1, r2 = st.columns([1.45, 0.85])
        with r1:
            st.markdown('<div class="mode-pill">System Mode: <strong>Pythagorean (1–9)</strong></div>', unsafe_allow_html=True)
        with r2:
            if st.button("+ New Session", key="new_session_btn"):
                st.session_state.session_reset_counter += 1
                st.session_state.generated = False
                st.session_state.last_result = None
                st.session_state.candidate_text_val = ""
                st.rerun()

    # Dark Hero Banner
    st.markdown(
        """
        <div class="dark-hero">
            <div class="dark-hero-pill">• Pythagorean Numerology Engine</div>
            <h1 class="dark-hero-title">Lucky Number Finder</h1>
            <p class="dark-hero-desc">
                Generate tailored lucky numbers from your Date of Birth, Name, or both — then enter or upload
                available numbers to see which option rates best for you.
            </p>
            <div class="dark-hero-checks">
                <span>✓ Single-digit Destiny Reductions</span>
                <span>✓ Optional Birth Place & Name Support</span>
                <span>✓ Available Number Rating & Ranking</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # STEP 01: Choose Your Purpose
    st.markdown('<div class="step-kicker">Step 01</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <h3 class="step-title">Choose Your Purpose</h3>
            <span class="step-hint">Select intended use case for guidance weighting</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    purpose_items = [
        ("New Vehicle", "🚗", "Registration plate & digit sum harmony"),
        ("Mobile Number", "📱", "VIP digits, SIM frequency & sum balance"),
        ("Name Check", "✦", "Name expression & compatibility check"),
        ("Any Purpose", "☆", "Universal daily fortune & milestone alignment"),
    ]

    p_cols = st.columns(4, gap="medium")
    for idx, (p_title, p_icon, p_desc) in enumerate(purpose_items):
        is_sel = st.session_state.purpose == p_title
        card_cls = "purpose-card purpose-card-active" if is_sel else "purpose-card"
        dot_cls = "radio-dot radio-dot-active" if is_sel else "radio-dot"
        with p_cols[idx]:
            st.markdown(
                f"""
                <div class="{card_cls}">
                    <div class="purpose-top">
                        <div class="purpose-icon">{p_icon}</div>
                        <span class="{dot_cls}"></span>
                    </div>
                    <div class="purpose-name">{p_title}</div>
                    <div class="purpose-sub">{p_desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "Selected" if is_sel else f"Select {p_title}",
                key=f"purpose_btn_{idx}",
                use_container_width=True,
            ):
                st.session_state.purpose = p_title
                st.rerun()

    current_purpose = st.session_state.purpose
    rk = st.session_state.session_reset_counter

    st.write("")

    # STEP 02: Enter Your Details
    st.markdown('<div class="step-kicker">Step 02</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <h3 class="step-title">Enter Your Details</h3>
            <span class="step-hint">Birth Place is always optional</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        use_dob = st.checkbox(
            "Use Date of Birth",
            value=True,
            disabled=(current_purpose != "Name Check"),
            key=f"use_dob_{rk}",
        )
        dob = st.date_input(
            "Date of Birth *" if use_dob else "Date of Birth (Optional)",
            value=datetime.date(1998, 8, 14),
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today(),
            disabled=not use_dob,
            key=f"dob_{rk}",
        )

        # Single Compact Row: Name | Context | Birth Place
        c_name, c_ctx, c_place = st.columns(3, gap="medium")
        with c_name:
            name_lbl = "Name / Brand Name *" if current_purpose == "Name Check" else "Name (Optional)"
            user_name = st.text_input(name_lbl, placeholder="e.g., Rohan Verma", key=f"name_{rk}")
            st.markdown('<div class="field-subnote">Calculates Pythagorean name value</div>', unsafe_allow_html=True)

        with c_ctx:
            if current_purpose == "New Vehicle":
                ctx_label, ctx_opts = "Vehicle Context (Optional)", ["Personal Car / Bike", "Commercial / Fleet"]
            elif current_purpose == "Mobile Number":
                ctx_label, ctx_opts = "Line Context (Optional)", ["Personal SIM", "Business / Client Line"]
            elif current_purpose == "Name Check":
                ctx_label, ctx_opts = "Name Context (Optional)", ["Personal Full Name", "Business / Brand Name"]
            else:
                ctx_label, ctx_opts = "Decision Context (Optional)", ["General Choices", "Dates & Milestones"]
            sub_option = st.selectbox(ctx_label, ctx_opts, key=f"ctx_{rk}_{current_purpose}")
            st.markdown('<div class="field-subnote">Tailors guidance to your use case</div>', unsafe_allow_html=True)

        with c_place:
            birth_place = st.text_input("Birth Place (Optional)", placeholder="e.g., City / State", key=f"place_{rk}")
            st.markdown('<div class="field-subnote">Optional regional/context note</div>', unsafe_allow_html=True)

        st.write("")
        generate_clicked = st.button("+ Generate Lucky Numbers  →", type="primary", use_container_width=True)

    if generate_clicked:
        name_num = calculate_name_number(user_name)
        dob_num, _, dob_expr = calculate_dob_details(dob) if use_dob else (None, 0, "")

        if current_purpose == "Name Check" and name_num is None:
            st.error("Please enter a valid alphabetic name for Name Check.")
        else:
            primary_num = name_num if (current_purpose == "Name Check" and dob_num is None) else dob_num
            comp = COMPATIBILITY[primary_num]
            archetype_title, ruling_planet, archetype_desc = ARCHETYPES[primary_num]
            recs = build_recommendations(current_purpose, primary_num, comp["seed"], sub_option)

            st.session_state.generated = True
            st.session_state.last_result = {
                "purpose": current_purpose,
                "sub_option": sub_option,
                "primary_num": primary_num,
                "dob_num": dob_num,
                "dob_expr": dob_expr,
                "dob_str": dob.strftime("%Y / %m / %d") if use_dob else "Not provided",
                "name_num": name_num,
                "name_str": user_name.strip() if user_name.strip() else "Not provided",
                "place_str": birth_place.strip() if birth_place.strip() else "Optional (Skipped)",
                "archetype_title": archetype_title,
                "ruling_planet": ruling_planet,
                "archetype_desc": archetype_desc,
                "seed_nums": comp["seed"],
                "caution_num": comp["caution"],
                "affinity": comp["affinity"],
                "recs": recs,
            }

            st.session_state.logs.insert(
                0,
                {
                    "Time": datetime.datetime.now().strftime("%I:%M %p"),
                    "Purpose": current_purpose,
                    "DOB": "Provided" if use_dob else "Blank",
                    "Name": "Entered" if name_num is not None else "Blank",
                    "Birth Place": "Entered" if birth_place.strip() else "Blank",
                    "Primary No": primary_num,
                    "Name No": name_num if name_num is not None else "-",
                },
            )

    # SNAPSHOT / RESULTS SECTION
    if st.session_state.generated and st.session_state.last_result:
        res = st.session_state.last_result
        st.markdown(
            f"""
            <div class="snapshot-header">
                <div class="snapshot-title">• Instant Lucky Number Snapshot — {res["purpose"]}</div>
                <div class="snapshot-meta">DOB: {res["dob_str"]} &nbsp;|&nbsp; Name: {res["name_str"]} &nbsp;|&nbsp; Place: {res["place_str"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        s1, s2, s3 = st.columns(3, gap="medium")

        with s1:
            st.markdown(
                f"""
                <div class="snap-card">
                    <div class="snap-kicker">Foundational Root Number</div>
                    <div>
                        <span class="snap-big-num">{res["primary_num"]}</span>
                        <span class="snap-archetype">{res["archetype_title"]}</span>
                    </div>
                    <p class="snap-body">
                        {f'Derived from <strong>{res["dob_expr"]}</strong>. ' if res["dob_expr"] else ''}
                        {res["archetype_desc"]}
                    </p>
                    <div class="snap-foot">
                        <span>Ruling Vibration</span>
                        <strong>{res["ruling_planet"]}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with s2:
            chips_html = "".join(f'<span class="seed-chip">{n}</span>' for n in res["seed_nums"])
            extra_line = (
                f"Name Number: <strong>{res['name_num']}</strong> · "
                if res["name_num"] is not None
                else ""
            )
            st.markdown(
                f"""
                <div class="snap-card">
                    <div class="snap-kicker">Harmonious Seed Digits</div>
                    <div style="margin-top: 0.25rem;">{chips_html}</div>
                    <p class="snap-body">
                        {extra_line}Digits sharing compatibility with Root {res["primary_num"]};
                        keep <strong>{res["caution_num"]}</strong> as lower priority when other options fit.
                    </p>
                    <div class="snap-foot">
                        <span>Highest Affinity</span>
                        <strong style="color:#059669;">{res["affinity"]}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with s3:
            rec_rows_html = "".join(
                f'<div class="rec-row"><span class="rec-code">{code}</span><span class="rec-tag">{tag}</span></div>'
                for code, tag in res["recs"]
            )
            st.markdown(
                f"""
                <div class="snap-card">
                    <div class="snap-kicker">Top {res["purpose"]} Options</div>
                    <div>{rec_rows_html}</div>
                    <div class="snap-foot" style="margin-top:0.65rem;">
                        <span>Context Focus</span>
                        <strong style="color:#059669;">{res["sub_option"]}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # STEP 03: RATE AVAILABLE NUMBERS (TEXTAREA + IMAGE UPLOAD)
        st.write("")
        st.markdown('<div class="step-kicker">Step 03 — Availability Check & Rating</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="step-heading-row">
                <h3 class="step-title">Check & Rate Available Numbers</h3>
                <span class="step-hint">Paste available numbers or upload a photo of the available list</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            up_col, txt_col = st.columns([1.15, 1.85], gap="large")

            with up_col:
                uploaded_img = st.file_uploader(
                    "Upload Photo of Available Numbers",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=f"avail_img_{rk}",
                    help="Upload a snapshot or photo of available vehicle/mobile numbers.",
                )
                if uploaded_img is not None:
                    st.image(uploaded_img, caption=f"Uploaded: {uploaded_img.name}", use_container_width=True)
                    extracted_from_name = re.findall(r"\d{2,}", uploaded_img.name)
                    if extracted_from_name and st.button("Extract Digits from Filename", key=f"ext_btn_{rk}"):
                        st.session_state.candidate_text_val = ", ".join(extracted_from_name)
                        st.rerun()

            with txt_col:
                candidate_input = st.text_area(
                    "Enter / Paste Available Numbers",
                    value=st.session_state.candidate_text_val,
                    height=135,
                    placeholder="e.g., 1044, 4007, 7704, 8888\nOr paste one number per line from your dealership / telecom list",
                    key=f"cand_area_{rk}",
                )
                st.session_state.candidate_text_val = candidate_input

            rate_btn = st.button("★ Rate & Find Best Number", type="primary", use_container_width=True, key=f"rate_btn_{rk}")

            if rate_btn:
                candidates = parse_candidate_numbers(candidate_input)
                if not candidates:
                    st.warning("Please enter at least one valid number in the text area to rate.")
                else:
                    scored = [
                        rate_candidate_number(c, res["primary_num"], res["seed_nums"], res["caution_num"])
                        for c in candidates
                    ]
                    scored.sort(key=lambda x: x["_numeric_score"], reverse=True)
                    best = scored[0]

                    st.markdown(
                        f"""
                        <div class="best-pick-box">
                            <strong>Best Rated Number:</strong> <span style="font-size:1.05rem;">{best["Candidate"]}</span>
                            &nbsp;—&nbsp; <strong>{best["Rating Score"]}</strong> ({best["Stars"]} · {best["Tier"]})<br>
                            <span style="font-size:0.8rem;">Reason: {best["Why Rated"]}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write("")
                    rating_df = pd.DataFrame(
                        [
                            {
                                "Rank": i + 1,
                                "Number": row["Candidate"],
                                "Rating": row["Rating Score"],
                                "Stars": row["Stars"],
                                "Fit Tier": row["Tier"],
                                "Digit Sum": row["Digit Sum"],
                                "Ending": row["Ending Digit"],
                                "Evaluation Notes": row["Why Rated"],
                            }
                            for i, row in enumerate(scored)
                        ]
                    )
                    st.dataframe(rating_df, use_container_width=True, hide_index=True)

    # Bottom Studio Footer
    st.markdown(
        """
        <div class="app-footer">
            <div>© 2026 NumeroPath Studio. Pythagorean number reduction & candidate rating workspace.</div>
            <div>Privacy Policy &nbsp;·&nbsp; Documentation &nbsp;·&nbsp; Rules Reference</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 6. VIEW 2: DASHBOARD & LOGS
# ---------------------------------------------------------
elif active_nav == "Dashboard & Logs":
    st.markdown(
        """
        <div class="dark-hero">
            <div class="dark-hero-pill">• Telemetry & Verification</div>
            <h1 class="dark-hero-title">Activity Dashboard & Logs</h1>
            <p class="dark-hero-desc">
                Inspect purpose demand, optional input usage, generated number distribution, and recent session lookups.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = pd.DataFrame(st.session_state.logs)

    f1, f2 = st.columns(2, gap="large")
    with f1:
        purpose_filter = st.selectbox(
            "Filter by Purpose",
            ["All Purposes", "New Vehicle", "Mobile Number", "Name Check", "Any Purpose"],
        )
    with f2:
        input_filter = st.selectbox(
            "Filter by Input Mode",
            ["All Modes", "With Name Entered", "With Birth Place Entered", "DOB Only"],
        )

    filtered_df = df.copy()
    if purpose_filter != "All Purposes":
        filtered_df = filtered_df[filtered_df["Purpose"] == purpose_filter]
    if input_filter == "With Name Entered":
        filtered_df = filtered_df[filtered_df["Name"] == "Entered"]
    elif input_filter == "With Birth Place Entered":
        filtered_df = filtered_df[filtered_df["Birth Place"] == "Entered"]
    elif input_filter == "DOB Only":
        filtered_df = filtered_df[(filtered_df["DOB"] == "Provided") & (filtered_df["Name"] == "Blank")]

    total_runs = len(filtered_df)
    top_purpose = filtered_df["Purpose"].mode()[0] if total_runs > 0 else "-"
    name_rate = f"{int((filtered_df['Name'] == 'Entered').mean() * 100)}%" if total_runs > 0 else "0%"
    place_rate = f"{int((filtered_df['Birth Place'] == 'Entered').mean() * 100)}%" if total_runs > 0 else "0%"
    top_num = f"#{filtered_df['Primary No'].mode()[0]}" if total_runs > 0 else "-"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Lookups", total_runs)
    k2.metric("Top Purpose", top_purpose)
    k3.metric("Name Used", name_rate)
    k4.metric("Birth Place Used", place_rate)
    k5.metric("Top Lucky No.", top_num)

    st.divider()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("##### Lookups by Purpose")
        if total_runs > 0:
            st.bar_chart(filtered_df["Purpose"].value_counts())
        else:
            st.info("No lookups match the selected filters.")

    with c2:
        st.markdown("##### Primary Numbers Distribution")
        if total_runs > 0:
            st.bar_chart(filtered_df["Primary No"].value_counts().sort_index())
        else:
            st.info("No lookups match the selected filters.")

    st.markdown("##### Recent Lookup Log")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# 7. VIEW 3: NUMEROLOGY RULES GUIDE
# ---------------------------------------------------------
else:
    st.markdown(
        """
        <div class="dark-hero">
            <div class="dark-hero-pill">• Reference Documentation</div>
            <h1 class="dark-hero-title">Numerology Rules Guide</h1>
            <p class="dark-hero-desc">
                Pythagorean letter-to-number table and calculation principles for DOB, Name, and optional Birth Place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([1.1, 1], gap="large")
    with col_l:
        st.markdown("##### Pythagorean Letter Mapping (1–9)")
        mapping_df = pd.DataFrame(
            {
                "Digit": list(range(1, 10)),
                "Letters": [
                    "A, J, S",
                    "B, K, T",
                    "C, L, U",
                    "D, M, V",
                    "E, N, W",
                    "F, O, X",
                    "G, P, Y",
                    "H, Q, Z",
                    "I, R",
                ],
            }
        )
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)

    with col_r:
        st.markdown("##### How Calculations Work")
        with st.container(border=True):
            st.markdown(
                """
                - **Date of Birth:** Digits are summed and reduced to a single digit (`1–9`).
                - **Name:** Alphabetic letters are converted via Pythagorean mapping, summed, and reduced to `1–9`.
                - **Birth Place (Optional):** Never required; leaving it blank runs standard calculations cleanly.
                - **Candidate Rating:** Scores pasted/uploaded numbers based on digit-sum reduction, ending digit alignment, and caution digits.
                """
            )