# Combined Numerology Insight

A starter Streamlit application combining:
- Chaldean name-number calculation
- Vedic-style Mulank and Bhagyank calculation
- Personal year and personal month
- Transparent combined profile
- PDF report download

## Requirements
Python 3.11 or newer is recommended.

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run tests
```powershell
pytest
```

## Methodology choices
1. Chaldean mapping: the conventional 1–8 letter mapping included in `calculations.py`.
2. Name compound: sum of mapped A–Z letters; compound is retained.
3. Name root: repeated digit reduction to 1–9.
4. Mulank: reduce the day of birth to 1–9.
5. Bhagyank: add all digits of DDMMYYYY and reduce to 1–9.
6. Personal year: day + month + digit sum of selected year, reduced to 1–9.
7. Personal month: personal year + calendar month, reduced to 1–9.
8. Lucky candidates: transparent product heuristic weighting Mulank 3, Bhagyank 2, name root 2. This is not a universally accepted numerology formula.

## Scope and limitations
- Enter names in Roman spelling. Different transliterations can change the Chaldean result.
- This starter uses one simplified convention; numerology schools differ.
- The included interpretations are starter content and should be reviewed/expanded by a knowledgeable practitioner before commercial release.
- Numerology is not scientifically validated as a predictive method.
- DOB/name are processed in the app session; this starter does not persist user profiles in a database.
