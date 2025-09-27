import re
import nltk
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Lists and Dictionaries for Local AI Functions ---

CONTACT_INFO_REGEX = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
}

STANDARD_SECTIONS = [
    'summary', 'profile', 'objective', 'experience', 'work experience',
    'professional experience', 'education', 'skills', 'technical skills',
    'projects', 'certifications', 'publications', 'references'
]

ACTION_VERBS = [
    'accelerated', 'achieved', 'administered', 'advised', 'analyzed', 'authored', 'automated',
    'built', 'calculated', 'centralized', 'collaborated', 'conceived', 'conducted', 'consolidated',
    'created', 'decreased', 'delegated', 'delivered', 'designed', 'developed', 'directed',
    'engineered', 'enhanced', 'established', 'evaluated', 'executed', 'expanded', 'facilitated',
    'founded', 'generated', 'guided', 'identified', 'implemented', 'improved', 'increased',
    'initiated', 'innovated', 'inspected', 'installed', 'instituted', 'interpreted', 'launched',
    'led', 'managed', 'marketed', 'mentored', 'negotiated', 'operated', 'organized', 'oversaw',
    'pioneered', 'planned', 'prepared', 'presented', 'programmed', 'promoted', 'proposed',
    'recommended', 'redesigned', 'reduced', 'reorganized', 'researched', 'resolved', 'restructured',
    'revamped', 'saved', 'scheduled', 'secured', 'solved', 'spearheaded', 'standardized',
    'streamlined', 'strengthened', 'supervised', 'systematized', 'trained', 'transformed', 'upgraded'
]

WEAK_PHRASES = {
    "responsible for": "Managed, Led, Oversaw",
    "helped with": "Assisted in, Contributed to, Supported",
    "worked on": "Developed, Created, Implemented",
    "assisted with": "Supported, Facilitated, Aided in",
    "was part of": "Collaborated on, Participated in",
    "duties included": "Primary responsibilities were, Key duties involved"
}

GENERATOR_TEMPLATES = {
    "summary": {
        "data analyst": "A results-driven Data Analyst with [NUMBER] years of experience in interpreting complex data to drive business decisions. Proven expertise in [SKILL_1], [SKILL_2], and [SKILL_3]. Seeking to leverage analytical skills to contribute to your team.",
        "software engineer": "A dedicated Software Engineer with [NUMBER] years of experience in building and maintaining scalable software solutions. Proficient in [SKILL_1], [SKILL_2], and [SKILL_3]. Eager to apply problem-solving skills to challenging new projects.",
        "project manager": "An organized and effective Project Manager with [NUMBER] years of experience leading cross-functional teams to deliver projects on time and within budget. Skilled in [SKILL_1], [SKILL_2], and [SKILL_3]."
    },
    "bullet_point": {
        "generic": [
            "Spearheaded [PROJECT] resulting in a [METRIC]% improvement in [AREA].",
            "Developed and implemented a new [SYSTEM] that reduced [PROBLEM] by [METRIC]%.",
            "Collaborated with a team of [NUMBER] to launch [PRODUCT], achieving [RESULT]."
        ]
    }
}

def calculate_match_score(resume_text, jd_text):
    """
    Calculates the similarity score between a resume and a job description
    using TF-IDF and Cosine Similarity.
    """
    text_documents = [resume_text, jd_text]
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform(text_documents)
        match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return match_score * 100
    except ValueError:
        return 0.0

def analyze_ats_friendliness(resume_text):
    """
    Performs a rule-based analysis of a resume's ATS-friendliness.
    """
    report = {
        "ats_score": 0,
        "contact_info_feedback": {"found": [], "missing": []},
        "sections_feedback": {"found": [], "missing": []},
        "action_verbs_feedback": {"good_lines": 0, "total_lines": 0, "feedback": ""},
        "keyword_feedback": {"top_keywords": []}
    }
    score = 0
    
    # 1. Check Contact Info (25 points)
    found_contacts = [info.capitalize() for info, pattern in CONTACT_INFO_REGEX.items() if pattern.search(resume_text)]
    if "Email" in found_contacts: score += 15
    if "Phone" in found_contacts: score += 10
    report["contact_info_feedback"]["found"] = found_contacts
    report["contact_info_feedback"]["missing"] = [info.capitalize() for info in CONTACT_INFO_REGEX if info.capitalize() not in found_contacts]

    # 2. Check Standard Sections (25 points)
    resume_lower = resume_text.lower()
    found_sections = list(set([sec for sec in STANDARD_SECTIONS if re.search(r'\b' + re.escape(sec) + r'\b', resume_lower)]))
    score += min(len(found_sections) * 5, 25)
    report["sections_feedback"]["found"] = found_sections

    # 3. Check Action Verbs (25 points)
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    bullet_lines = [line for line in lines if line.startswith(('*', '-', '•'))]
    if bullet_lines:
        good_lines = sum(1 for line in bullet_lines if line.lstrip('* - •').strip().split(' ')[0].lower() in ACTION_VERBS)
        verb_ratio = good_lines / len(bullet_lines)
        score += verb_ratio * 25
        report["action_verbs_feedback"].update({"good_lines": good_lines, "total_lines": len(bullet_lines)})
        report["action_verbs_feedback"]["feedback"] = "Excellent use of action verbs!" if verb_ratio > 0.8 else "Consider starting more bullet points with strong action verbs."
            
    # 4. Keyword Density (25 points)
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
        vectorizer.fit_transform([resume_text])
        report["keyword_feedback"]["top_keywords"] = list(vectorizer.get_feature_names_out())
        score += 25
    except:
        report["keyword_feedback"]["top_keywords"] = ["Could not extract keywords."]

    report["ats_score"] = int(score)
    return report

def generate_content_local(user_input):
    """
    Generates template-based resume content. Not a creative AI.
    """
    input_lower = user_input.lower()
    if "summary" in input_lower:
        for role, template in GENERATOR_TEMPLATES["summary"].items():
            if role in input_lower:
                return template.replace("[NUMBER]", "X").replace("[SKILL_1]", "key skill 1").replace("[SKILL_2]", "key skill 2").replace("[SKILL_3]", "key skill 3")
        return "Could not identify a role. Please try 'generate a summary for a data analyst'."
    
    if "bullet point" in input_lower:
        return "\n".join(GENERATOR_TEMPLATES["bullet_point"]["generic"])

    return "Sorry, I can only generate a 'professional summary' or 'bullet point' examples."

def get_interactive_suggestions(resume_text):
    """
    Finds weak phrases in the resume and suggests stronger alternatives.
    """
    suggestions = []
    lines = resume_text.split('\n')
    for line in lines:
        for weak_phrase, suggestion in WEAK_PHRASES.items():
            if weak_phrase in line.lower():
                suggestions.append({
                    "original": line.strip(),
                    "suggestion": f"This line uses a weak phrase. Try rephrasing with stronger verbs like: '{suggestion}'."
                })
    return {"improvements": suggestions[:5]}

