import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import webbrowser


# ============================================
# CONFIGURATION DES 8 AXES NYOTA
# ============================================

AXES_CONFIG = {
    "Ouverture & Curiosité": {
        "bloc1": list(range(1, 7)),
        "bloc2": [14],
        "bloc3": [3, 6],
        "invert": []
    },
    
    "Discipline & Fiabilité": {
        "bloc1": list(range(7, 13)),
        "bloc3": [7, 11, 12],
        "invert": []
    },
    
    "Influence & Présence": {
        "bloc1": list(range(13, 19)),
        "bloc2": [15],
        "invert": []
    },
    
    "Coopération": {
        "bloc1": list(range(19, 25)),
        "bloc2": [16],
        "invert": []
    },
    
    "Résilience & Stress": {
        "bloc1": list(range(25, 31)),
        "bloc2": list(range(1, 9)),
        "invert": [("bloc2", q) for q in range(1, 9)]
    },
    
    "Drive & Motivation": {
        "bloc2": [9, 10, 11, 12, 13, 15, 16],
        "invert": []
    },
    
    "Style d'action": {
        "bloc3": list(range(1, 13)),
        "invert": []
    },
    
    "Alignement stratégique": {
        "bloc4": list(range(1, 15)),
        "invert": []
    }
}


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def invert_score(value: int) -> int:
    """Inverse un item à risque (1→5, 5→1)"""
    return 6 - value


def normalize_to_100(score: float) -> float:
    """Normalise une moyenne 1-5 vers 0-100"""
    return round(((score - 1) / 4) * 100, 2)


# ============================================
# CONVERSION JSON → STRUCTURE PAR BLOCS
# ============================================

def parse_responses(json_data: Dict[int, int]) -> Dict[str, Dict[int, int]]:
    """
    Convertit les réponses JSON plates en structure par blocs.
    """
    responses = {
        "bloc1": {},
        "bloc2": {},
        "bloc3": {},
        "bloc4": {}
    }
    
    for i in range(1, 31):
        if i in json_data:
            responses["bloc1"][i] = json_data[i]
    
    for i in range(31, 47):
        if i in json_data:
            responses["bloc2"][i - 30] = json_data[i]
    
    for i in range(47, 59):
        if i in json_data:
            responses["bloc3"][i - 46] = json_data[i]
    
    for i in range(59, 73):
        if i in json_data:
            responses["bloc4"][i - 58] = json_data[i]
    
    return responses


# ============================================
# CALCUL DES SCORES PAR AXE
# ============================================

def compute_axis_score(axis_name: str, config: dict, responses: dict) -> float:
    """Calcule le score d'un axe en agrégeant les items configurés"""
    
    values = []
    
    for bloc_name in ["bloc1", "bloc2", "bloc3", "bloc4"]:
        if bloc_name not in config:
            continue
        
        for item_num in config[bloc_name]:
            if item_num not in responses[bloc_name]:
                raise ValueError(f"❌ [{axis_name}] Item manquant : {bloc_name} Q{item_num}")
            
            value = responses[bloc_name][item_num]
            
            if (bloc_name, item_num) in config["invert"]:
                value = invert_score(value)
            
            values.append(value)
    
    if not values:
        return 0.0
    
    mean_score = sum(values) / len(values)
    return normalize_to_100(mean_score)


def compute_all_scores(json_responses: Dict[int, int]) -> Dict[str, float]:
    """Calcule les 8 scores NYOTA"""
    
    responses = parse_responses(json_responses)
    scores = {}
    
    for axis_name, config in AXES_CONFIG.items():
        scores[axis_name] = compute_axis_score(axis_name, config, responses)
    
    return scores


# ============================================
# GÉNÉRATION DU RAPPORT ÉCRIT (CONSOLE/TXT)
# ============================================

def generate_written_report(scores: Dict[str, float]) -> str:
    """
    Génère un rapport écrit complet avec points forts, points faibles et recommandations
    """
    
    # Trier les scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_scores[:3]
    bottom_3 = sorted_scores[-3:]
    
    report = []
    
    # ===== EN-TÊTE =====
    report.append("\n" + "="*80)
    report.append("                    RAPPORT D'ANALYSE NYOTA PERSONALITY")
    report.append("="*80 + "\n")
    
    # ===== SYNTHÈSE GLOBALE =====
    avg_score = sum(scores.values()) / len(scores)
    report.append("📊 SYNTHÈSE GLOBALE")
    report.append("-" * 80)
    report.append(f"Score moyen général : {avg_score:.1f}/100")
    
    if avg_score >= 70:
        report.append("✅ Profil équilibré avec des aptitudes marquées dans plusieurs domaines.")
    elif avg_score >= 50:
        report.append("⚠️  Profil en développement avec des axes de force identifiés.")
    else:
        report.append("📈 Profil en construction avec un fort potentiel d'évolution.")
    
    report.append("")
    
    # ===== POINTS FORTS =====
    report.append("✅ POINTS FORTS (Top 3)")
    report.append("-" * 80)
    
    for i, (axis, score) in enumerate(top_3, 1):
        report.append(f"\n{i}. {axis.upper()} - Score: {score:.1f}/100")
        
        # Descriptions personnalisées par axe
        if "Ouverture" in axis:
            report.append("   → Vous excellez dans l'exploration intellectuelle et l'innovation.")
            report.append("   → Capacité à remettre en question les méthodes établies.")
            report.append("   → Curiosité naturelle et goût pour l'apprentissage continu.")
            
        elif "Discipline" in axis:
            report.append("   → Excellente rigueur et organisation dans le travail.")
            report.append("   → Fiabilité exemplaire dans le respect des engagements.")
            report.append("   → Attention aux détails et méthodologie structurée.")
            
        elif "Influence" in axis:
            report.append("   → Grande aisance relationnelle et capacité à convaincre.")
            report.append("   → Présence naturelle dans les interactions de groupe.")
            report.append("   → Leadership assertif et visibilité sociale marquée.")
            
        elif "Coopération" in axis:
            report.append("   → Intelligence relationnelle développée et empathie naturelle.")
            report.append("   → Facilité à collaborer et à créer du consensus.")
            report.append("   → Approche gagnant-gagnant dans les interactions.")
            
        elif "Résilience" in axis:
            report.append("   → Excellente stabilité émotionnelle sous pression.")
            report.append("   → Capacité à maintenir son calme dans l'adversité.")
            report.append("   → Récupération rapide après les échecs.")
            
        elif "Drive" in axis:
            report.append("   → Motivation intrinsèque puissante et ambition affirmée.")
            report.append("   → Besoin fort de défis et de reconnaissance.")
            report.append("   → Engagement élevé dans les projets porteurs de sens.")
            
        elif "Style" in axis:
            report.append("   → Approche de l'action adaptée et efficace.")
            report.append("   → Bon équilibre entre initiative et cadre structuré.")
            report.append("   → Capacité à ajuster son rythme selon le contexte.")
            
        elif "Alignement" in axis:
            report.append("   → Vision stratégique claire et cohérence décisionnelle.")
            report.append("   → Excellente projection dans le futur.")
            report.append("   → Alignement fort entre actions présentes et objectifs futurs.")
    
    report.append("")
    
    # ===== AXES DE DÉVELOPPEMENT =====
    report.append("📈 AXES DE DÉVELOPPEMENT (Bottom 3)")
    report.append("-" * 80)
    
    for i, (axis, score) in enumerate(bottom_3, 1):
        report.append(f"\n{i}. {axis.upper()} - Score: {score:.1f}/100")
        
        if "Ouverture" in axis:
            report.append("   → Développer la curiosité intellectuelle et l'ouverture au changement.")
            report.append("   💡 Actions : Lire régulièrement, suivre des formations, s'exposer à de nouvelles idées.")
            
        elif "Discipline" in axis:
            report.append("   → Renforcer la rigueur et la méthodologie de travail.")
            report.append("   💡 Actions : Utiliser des outils de gestion du temps, établir des routines claires.")
            
        elif "Influence" in axis:
            report.append("   → Développer l'aisance relationnelle et la prise de parole.")
            report.append("   💡 Actions : Participer à des clubs de parole, s'entraîner aux présentations publiques.")
            
        elif "Coopération" in axis:
            report.append("   → Travailler l'empathie et la capacité à collaborer.")
            report.append("   💡 Actions : Pratiquer l'écoute active, rechercher activement les feedbacks.")
            
        elif "Résilience" in axis:
            report.append("   → Renforcer la gestion du stress et la stabilité émotionnelle.")
            report.append("   💡 Actions : Techniques de relaxation, sport régulier, accompagnement si besoin.")
            
        elif "Drive" in axis:
            report.append("   → Clarifier ses sources de motivation et d'engagement.")
            report.append("   💡 Actions : Identifier ses valeurs profondes, fixer des objectifs alignés.")
            
        elif "Style" in axis:
            report.append("   → Ajuster son rapport au cadre et à l'autonomie.")
            report.append("   💡 Actions : Expérimenter différents modes de travail, demander du feedback.")
            
        elif "Alignement" in axis:
            report.append("   → Développer une vision stratégique plus claire.")
            report.append("   💡 Actions : Coaching de carrière, exercices de projection à 3-5 ans.")
    
    report.append("")
    
    # ===== RECOMMANDATIONS DE POSTES =====
    report.append("🎯 RECOMMANDATIONS DE POSTES / RÔLES ADAPTÉS")
    report.append("-" * 80)
    
    # Logique de recommandation basée sur le profil
    recommendations = []
    top_axes = [axis for axis, _ in top_3]
    
    if "Ouverture & Curiosité" in top_axes and "Discipline & Fiabilité" in top_axes:
        recommendations.append("• CHEF DE PROJET INNOVATION / R&D MANAGER")
        recommendations.append("  Combinez curiosité intellectuelle et rigueur d'exécution.")
        
    if "Influence & Présence" in top_axes and scores["Coopération"] >= 60:
        recommendations.append("\n• RESPONSABLE COMMERCIAL / BUSINESS DEVELOPER")
        recommendations.append("  Votre aisance relationnelle et capacité à convaincre sont des atouts majeurs.")
        
    if "Drive & Motivation" in top_axes and "Alignement stratégique" in top_axes:
        recommendations.append("\n• ENTREPRENEUR / INTRAPRENEUR")
        recommendations.append("  Votre vision claire et motivation intrinsèque favorisent l'entrepreneuriat.")
        
    if "Coopération" in top_axes and "Résilience & Stress" in top_axes:
        recommendations.append("\n• RESPONSABLE RH / PEOPLE MANAGER")
        recommendations.append("  Intelligence relationnelle et stabilité émotionnelle idéales pour gérer des équipes.")
        
    if "Discipline & Fiabilité" in top_axes and scores["Alignement stratégique"] >= 65:
        recommendations.append("\n• CHEF DE PROJET / PROJECT MANAGER")
        recommendations.append("  Rigueur, organisation et vision permettent de piloter des projets complexes.")
        
    if "Ouverture & Curiosité" in top_axes and "Influence & Présence" in top_axes:
        recommendations.append("\n• CONSULTANT / COACH")
        recommendations.append("  Capacité à explorer, innover et influencer positivement les autres.")
        
    if scores["Drive & Motivation"] >= 70 and scores["Style d'action"] >= 65:
        recommendations.append("\n• DIRECTEUR OPÉRATIONNEL / COO")
        recommendations.append("  Motivation élevée et style d'action adapté pour diriger les opérations.")
    
    # Postes génériques si aucune correspondance
    if not recommendations:
        recommendations.append("• POSTES À EXPLORER :")
        if avg_score >= 60:
            recommendations.append("  Rôles nécessitant polyvalence et adaptabilité.")
            recommendations.append("  Postes en développement de compétences transversales.")
        else:
            recommendations.append("  Postes d'apprentissage en environnement structuré.")
            recommendations.append("  Missions avec accompagnement et mentorat.")
    
    report.extend(recommendations)
    report.append("")
    
    # ===== CONSEILS GÉNÉRAUX =====
    report.append("\n💼 CONSEILS POUR VALORISER VOTRE PROFIL")
    report.append("-" * 80)
    report.append("1. 🎯 Mettez en avant vos 3 points forts dans vos candidatures et entretiens")
    report.append("2. 📚 Travaillez activement vos axes de développement (formations, coaching)")
    report.append("3. 🏢 Recherchez des environnements alignés avec votre profil naturel")
    report.append("4. 🔄 Demandez régulièrement du feedback pour progresser continuellement")
    report.append("5. 💎 Restez authentique : votre profil unique est votre plus grande force")
    
    report.append("\n" + "="*80)
    report.append("                           FIN DU RAPPORT")
    report.append("="*80 + "\n")
    
    return "\n".join(report)


# ============================================
# GÉNÉRATION DU RAPPORT ÉCRIT EN HTML
# ============================================

def generate_html_report(scores: Dict[str, float]) -> str:
    """
    Génère un rapport HTML élégant avec les forces, faiblesses et recommandations
    """
    
    # Trier les scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_scores[:3]
    bottom_3 = sorted_scores[-3:]
    avg_score = sum(scores.values()) / len(scores)
    
    # Générer le HTML
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport NYOTA Personality</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #0066FF 0%, #00BFFF 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 42px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{
            font-size: 18px;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 50px 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 28px;
            color: #0066FF;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #0066FF;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .icon {{
            font-size: 32px;
        }}
        
        .synthese {{
            background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #0066FF;
            margin-bottom: 30px;
        }}
        
        .score-global {{
            font-size: 48px;
            font-weight: 700;
            color: #0066FF;
            margin: 15px 0;
        }}
        
        .card {{
            background: #F9FAFB;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 5px solid #10B981;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .card-weak {{
            border-left-color: #EF4444;
        }}
        
        .card-title {{
            font-size: 22px;
            font-weight: 700;
            color: #1F2937;
            margin-bottom: 10px;
        }}
        
        .card-score {{
            font-size: 32px;
            font-weight: 700;
            color: #0066FF;
            margin-bottom: 15px;
        }}
        
        .card-description {{
            color: #4B5563;
            line-height: 1.8;
            margin-bottom: 8px;
        }}
        
        .card-description strong {{
            color: #1F2937;
        }}
        
        .recommendation {{
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 15px;
            border-left: 5px solid #F59E0B;
        }}
        
        .recommendation-title {{
            font-size: 20px;
            font-weight: 700;
            color: #92400E;
            margin-bottom: 10px;
        }}
        
        .recommendation-text {{
            color: #78350F;
            line-height: 1.7;
        }}
        
        .tips {{
            background: #DBEAFE;
            border-radius: 12px;
            padding: 25px;
            margin-top: 30px;
        }}
        
        .tips-title {{
            font-size: 22px;
            font-weight: 700;
            color: #1E40AF;
            margin-bottom: 20px;
        }}
        
        .tips ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .tips li {{
            padding: 12px 0;
            color: #1E3A8A;
            font-size: 16px;
            line-height: 1.6;
        }}
        
        .tips li:before {{
            content: "✓";
            color: #10B981;
            font-weight: bold;
            display: inline-block;
            width: 1.5em;
            font-size: 20px;
        }}
        
        .footer {{
            background: #1F2937;
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 14px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 30px 20px;
            }}
            .header h1 {{
                font-size: 32px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .section-title {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 RAPPORT NYOTA PERSONALITY</h1>
            <p>Analyse Complète de Votre Profil de Personnalité</p>
        </div>
        
        <div class="content">
            <!-- SYNTHÈSE GLOBALE -->
            <div class="section">
                <div class="synthese">
                    <h2 style="color: #0066FF; margin-bottom: 15px;">Synthèse Globale</h2>
                    <div class="score-global">{avg_score:.1f}<span style="font-size: 24px;">/100</span></div>
                    <p style="font-size: 18px; color: #1F2937; line-height: 1.8;">
"""
    
    if avg_score >= 70:
        html += "✅ <strong>Profil équilibré</strong> avec des aptitudes marquées dans plusieurs domaines."
    elif avg_score >= 50:
        html += "⚠️ <strong>Profil en développement</strong> avec des axes de force identifiés."
    else:
        html += "📈 <strong>Profil en construction</strong> avec un fort potentiel d'évolution."
    
    html += """
                    </p>
                </div>
            </div>
            
            <!-- POINTS FORTS -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">✅</span>
                    Vos Points Forts
                </h2>
"""
    
    for i, (axis, score) in enumerate(top_3, 1):
        html += f"""
                <div class="card">
                    <div class="card-title">{i}. {axis}</div>
                    <div class="card-score">{score:.1f}/100</div>
"""
        
        if "Ouverture" in axis:
            html += """
                    <p class="card-description">→ Vous excellez dans l'exploration intellectuelle et l'innovation.</p>
                    <p class="card-description">→ Capacité à remettre en question les méthodes établies.</p>
                    <p class="card-description">→ Curiosité naturelle et goût pour l'apprentissage continu.</p>
"""
        elif "Discipline" in axis:
            html += """
                    <p class="card-description">→ Excellente rigueur et organisation dans le travail.</p>
                    <p class="card-description">→ Fiabilité exemplaire dans le respect des engagements.</p>
                    <p class="card-description">→ Attention aux détails et méthodologie structurée.</p>
"""
        elif "Influence" in axis:
            html += """
                    <p class="card-description">→ Grande aisance relationnelle et capacité à convaincre.</p>
                    <p class="card-description">→ Présence naturelle dans les interactions de groupe.</p>
                    <p class="card-description">→ Leadership assertif et visibilité sociale marquée.</p>
"""
        elif "Coopération" in axis:
            html += """
                    <p class="card-description">→ Intelligence relationnelle développée et empathie naturelle.</p>
                    <p class="card-description">→ Facilité à collaborer et à créer du consensus.</p>
                    <p class="card-description">→ Approche gagnant-gagnant dans les interactions.</p>
"""
        elif "Résilience" in axis:
            html += """
                    <p class="card-description">→ Excellente stabilité émotionnelle sous pression.</p>
                    <p class="card-description">→ Capacité à maintenir son calme dans l'adversité.</p>
                    <p class="card-description">→ Récupération rapide après les échecs.</p>
"""
        elif "Drive" in axis:
            html += """
                    <p class="card-description">→ Motivation intrinsèque puissante et ambition affirmée.</p>
                    <p class="card-description">→ Besoin fort de défis et de reconnaissance.</p>
                    <p class="card-description">→ Engagement élevé dans les projets porteurs de sens.</p>
"""
        elif "Style" in axis:
            html += """
                    <p class="card-description">→ Approche de l'action adaptée et efficace.</p>
                    <p class="card-description">→ Bon équilibre entre initiative et cadre structuré.</p>
                    <p class="card-description">→ Capacité à ajuster son rythme selon le contexte.</p>
"""
        elif "Alignement" in axis:
            html += """
                    <p class="card-description">→ Vision stratégique claire et cohérence décisionnelle.</p>
                    <p class="card-description">→ Excellente projection dans le futur.</p>
                    <p class="card-description">→ Alignement fort entre actions présentes et objectifs futurs.</p>
"""
        
        html += """
                </div>
"""
    
    html += """
            </div>
            
            <!-- AXES DE DÉVELOPPEMENT -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">📈</span>
                    Axes de Développement
                </h2>
"""
    
    for i, (axis, score) in enumerate(bottom_3, 1):
        html += f"""
                <div class="card card-weak">
                    <div class="card-title">{i}. {axis}</div>
                    <div class="card-score">{score:.1f}/100</div>
"""
        
        if "Ouverture" in axis:
            html += """
                    <p class="card-description">→ Développer la curiosité intellectuelle et l'ouverture au changement.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Lire régulièrement, suivre des formations, s'exposer à de nouvelles idées.</p>
"""
        elif "Discipline" in axis:
            html += """
                    <p class="card-description">→ Renforcer la rigueur et la méthodologie de travail.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Utiliser des outils de gestion du temps, établir des routines claires.</p>
"""
        elif "Influence" in axis:
            html += """
                    <p class="card-description">→ Développer l'aisance relationnelle et la prise de parole.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Participer à des clubs de parole, s'entraîner aux présentations publiques.</p>
"""
        elif "Coopération" in axis:
            html += """
                    <p class="card-description">→ Travailler l'empathie et la capacité à collaborer.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Pratiquer l'écoute active, rechercher activement les feedbacks.</p>
"""
        elif "Résilience" in axis:
            html += """
                    <p class="card-description">→ Renforcer la gestion du stress et la stabilité émotionnelle.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Techniques de relaxation, sport régulier, accompagnement si besoin.</p>
"""
        elif "Drive" in axis:
            html += """
                    <p class="card-description">→ Clarifier ses sources de motivation et d'engagement.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Identifier ses valeurs profondes, fixer des objectifs alignés.</p>
"""
        elif "Style" in axis:
            html += """
                    <p class="card-description">→ Ajuster son rapport au cadre et à l'autonomie.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Expérimenter différents modes de travail, demander du feedback.</p>
"""
        elif "Alignement" in axis:
            html += """
                    <p class="card-description">→ Développer une vision stratégique plus claire.</p>
                    <p class="card-description"><strong>💡 Actions :</strong> Coaching de carrière, exercices de projection à 3-5 ans.</p>
"""
        
        html += """
                </div>
"""
    
    html += """
            </div>
            
            <!-- RECOMMANDATIONS DE POSTES -->
            <div class="section">
                <h2 class="section-title">
                    <span class="icon">🎯</span>
                    Recommandations de Postes
                </h2>
"""
    
    top_axes = [axis for axis, _ in top_3]
    
    if "Ouverture & Curiosité" in top_axes and "Discipline & Fiabilité" in top_axes:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• CHEF DE PROJET INNOVATION / R&D MANAGER</div>
                    <div class="recommendation-text">Combinez curiosité intellectuelle et rigueur d'exécution.</div>
                </div>
"""
    
    if "Influence & Présence" in top_axes and scores["Coopération"] >= 60:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• RESPONSABLE COMMERCIAL / BUSINESS DEVELOPER</div>
                    <div class="recommendation-text">Votre aisance relationnelle et capacité à convaincre sont des atouts majeurs.</div>
                </div>
"""
    
    if "Drive & Motivation" in top_axes and "Alignement stratégique" in top_axes:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• ENTREPRENEUR / INTRAPRENEUR</div>
                    <div class="recommendation-text">Votre vision claire et motivation intrinsèque favorisent l'entrepreneuriat.</div>
                </div>
"""
    
    if "Coopération" in top_axes and "Résilience & Stress" in top_axes:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• RESPONSABLE RH / PEOPLE MANAGER</div>
                    <div class="recommendation-text">Intelligence relationnelle et stabilité émotionnelle idéales pour gérer des équipes.</div>
                </div>
"""
    
    if "Discipline & Fiabilité" in top_axes and scores["Alignement stratégique"] >= 65:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• CHEF DE PROJET / PROJECT MANAGER</div>
                    <div class="recommendation-text">Rigueur, organisation et vision permettent de piloter des projets complexes.</div>
                </div>
"""
    
    if "Ouverture & Curiosité" in top_axes and "Influence & Présence" in top_axes:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• CONSULTANT / COACH</div>
                    <div class="recommendation-text">Capacité à explorer, innover et influencer positivement les autres.</div>
                </div>
"""
    
    if scores["Drive & Motivation"] >= 70 and scores["Style d'action"] >= 65:
        html += """
                <div class="recommendation">
                    <div class="recommendation-title">• DIRECTEUR OPÉRATIONNEL / COO</div>
                    <div class="recommendation-text">Motivation élevée et style d'action adapté pour diriger les opérations.</div>
                </div>
"""
    
    html += """
            </div>
            
            <!-- CONSEILS -->
            <div class="tips">
                <div class="tips-title">💼 Conseils pour Valoriser Votre Profil</div>
                <ul>
                    <li>Mettez en avant vos 3 points forts dans vos candidatures et entretiens</li>
                    <li>Travaillez activement vos axes de développement (formations, coaching)</li>
                    <li>Recherchez des environnements alignés avec votre profil naturel</li>
                    <li>Demandez régulièrement du feedback pour progresser continuellement</li>
                    <li>Restez authentique : votre profil unique est votre plus grande force</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2026 NYOTA Personality - Tous droits réservés</p>
            <p style="margin-top: 10px; opacity: 0.8;">Rapport généré automatiquement</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


# ============================================
# VISUALISATION KIVIAT (MATPLOTLIB)
# ============================================

def plot_kiviat(scores: Dict[str, float], save_path: str = None):
    """Génère le diagramme radar à 8 axes avec matplotlib"""
    
    if len(scores) != 8:
        raise ValueError(f"⚠️ Le diagramme nécessite 8 axes, trouvé : {len(scores)}")
    
    labels = list(scores.keys())
    values = list(scores.values())
    
    num_axes = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_axes, endpoint=False).tolist()
    
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold', color='#1F2937')
    
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='gray')
    
    ax.plot(angles, values, 'o-', linewidth=3, color='#0066FF', label='Profil', markersize=8)
    ax.fill(angles, values, alpha=0.3, color='#0066FF')
    
    ax.grid(True, linestyle='--', alpha=0.7, color='#E5E7EB')
    
    ax.set_title("NYOTA Personality – Profil à 8 dimensions", 
                 pad=30, fontsize=18, fontweight='bold', color='#1F2937')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Diagramme Kiviat sauvegardé : {save_path}")
    
    plt.show()


# ============================================
# DASHBOARD PLOTLY UNIFIÉ AMÉLIORÉ (2x4)
# ============================================

def create_unified_dashboard(scores: Dict[str, float]):
    """
    Crée un dashboard unique avec tous les graphiques en grille 2×4
    VERSION AMÉLIORÉE avec couleurs harmonieuses et tailles optimisées
    """
    
    # Créer la grille de subplots
    fig = make_subplots(
        rows=2, cols=4,
        subplot_titles=(
            "<b>Ouverture & Curiosité</b>",
            "<b>Discipline & Fiabilité</b>", 
            "<b>Influence & Présence</b>",
            "<b>Coopération</b>",
            "<b>Résilience & Stress</b>",
            "<b>Drive & Motivation</b>",
            "<b>Style d'action</b>",
            "<b>Alignement stratégique</b>"
        ),
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "polar"}],
            [{"type": "indicator"}, {"type": "xy"}, {"type": "indicator"}, {"type": "indicator"}]
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.07
    )
    
    # ========================================
    # LIGNE 1, COLONNE 1 : Ouverture & Curiosité (Bullet amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="number+gauge",
            value=scores["Ouverture & Curiosité"],
            number={'font': {'size': 42, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#F59E0B"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=1, col=1
    )
    fig.add_annotation(
        dict(
            x=-0.03, y=0.66,
            xref="paper", yref="paper",
            text="Faible Curiosité",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    fig.add_annotation(
        dict(
            x=0.15, y=0.66,
            xref="paper", yref="paper",
            text="Curiosité élevée",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    
    # ========================================
    # LIGNE 1, COLONNE 2 : Discipline & Fiabilité (Gauge amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=scores["Discipline & Fiabilité"],
            number={'font': {'size': 38, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#9CA3AF"},
                'bar': {'color': "#F59E0B", 'thickness': 0.6},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "#E5E7EB",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=1, col=2
    )
    fig.add_annotation(
        x=0.26, y=0.66, 
        xref="paper", yref="paper",
        text="Faible", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )
    fig.add_annotation(
        x=0.36, y=0.83, 
        xref="paper", yref="paper",
        text="Moyen", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )   
    fig.add_annotation(
        x=0.45, y=0.66,
        xref="paper", yref="paper",
        text="Elevé", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )
    
    # ========================================
    # LIGNE 1, COLONNE 3 : Influence & Présence (Gauge amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=scores["Influence & Présence"],
            number={'font': {'size': 38, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#9CA3AF"},
                'bar': {'color': "#F59E0B", 'thickness': 0.6},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "#E5E7EB",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=1, col=3
    )
    fig.add_annotation(
        x=0.55, y=0.66, 
        xref="paper", yref="paper",
        text="Sous-exposition", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )
    fig.add_annotation(
        x=0.63, y=0.83, 
        xref="paper", yref="paper",
        text="Zone optimale", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )   
    fig.add_annotation(
        x=0.75, y=0.66,
        xref="paper", yref="paper",
        text="Sur-dominance", showarrow=False, font=dict(size=13, color="#0E0E0E")
    )
    
    # ========================================
    # LIGNE 1, COLONNE 4 : Coopération (Radar amélioré)
    # ========================================
    categories = ['Collaboration', 'Empathie', 'Relation']
    values_coop = [
        scores["Coopération"],
        scores["Ouverture & Curiosité"] * 0.8,
        scores["Influence & Présence"] * 0.7
    ]
    
    fig.add_trace(
        go.Scatterpolar(
            r=values_coop,
            theta=categories,
            fill='toself',
            name='Coopération',
            line=dict(color='#10B981', width=3),                                                                                            
            fillcolor='rgba(16, 185, 129, 0.4)',
            marker=dict(size=8, color='#10B981')
        ),
        row=1, col=4
    )
    
    # ========================================
    # LIGNE 2, COLONNE 1 : Résilience & Stress (Bullet amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="number+gauge",
            value=scores["Résilience & Stress"],
            number={'font': {'size': 42, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#9CA3AF"},
                'bar': {'color': "#F59E0B", 'thickness': 0.6},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E5E7EB",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=2, col=1
    )
    fig.add_annotation(
        dict(
            x=-0.01, y=0.05,
            xref="paper", yref="paper",
            text="Fragile",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    fig.add_annotation(
        dict(
            x=0.17, y=0.05,
            xref="paper", yref="paper",
            text="Solide",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    
    # ========================================
    # LIGNE 2, COLONNE 2 : Drive & Motivation (Bar Chart amélioré)
    # ========================================
    leviers = ['Motivation<br>intrinsèque', 'Reconnaissance', 'Ambition']
    valeurs_drive = [
        scores["Drive & Motivation"],
        scores["Drive & Motivation"] * 0.88,
        scores["Drive & Motivation"] * 0.82
    ]
    
    fig.add_trace(
        go.Bar(
            x=leviers,
            y=valeurs_drive,
            marker=dict(
                color=["#8B5CF6", "#EF4444", "#F59E0B"],
                line=dict(color='#1F2937', width=1.5)
            ),
            text=[f'{v:.0f}%' for v in valeurs_drive],
            textposition='outside',
            textfont=dict(size=13, color='#1F2937', family='Arial'),
            showlegend=False
        ),
        row=2, col=2
    )
    
    # ========================================
    # LIGNE 2, COLONNE 3 : Style d'action (Bullet amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="number+gauge",
            value=scores["Style d'action"],
            number={'font': {'size': 42, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#9CA3AF"},
                'bar': {'color': "#F59E0B", 'thickness': 0.6},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E5E7EB",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=2, col=3
    )
    fig.add_annotation(
        dict(
            x=0.55, y=0.05,
            xref="paper", yref="paper",
            text="Conformité",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    fig.add_annotation(
        dict(
            x=0.74, y=0.05,
            xref="paper", yref="paper",
            text="Autonomie",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    
    # ========================================
    # LIGNE 2, COLONNE 4 : Alignement stratégique (Gauge amélioré)
    # ========================================
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=scores["Alignement stratégique"],
            number={'font': {'size': 38, 'color': '#0066FF', 'family': 'Arial'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#9CA3AF"},
                'bar': {'color': "#F59E0B", 'thickness': 0.6},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "#E5E7EB",
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=2, col=4
    )
    fig.add_annotation(
        dict(
            x=0.83, y=0.05,
            xref="paper", yref="paper",
            text="Passé",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    fig.add_annotation(
        dict(
            x=0.91, y=0.22,
            xref="paper", yref="paper",
            text="Présent",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    fig.add_annotation(
        dict(
            x=1, y=0.05,
            xref="paper", yref="paper",
            text="Futur",
            showarrow=False,
            font=dict(size=13, color="#0E0E0E")
        )
    )
    
    # ========================================
    # MISE EN PAGE GLOBALE AMÉLIORÉE
    # ========================================
    fig.update_layout(
        title={
            'text': "<b>NYOTA Personality - Dashboard Complet des 8 Dimensions</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 26, 'color': '#1F2937', 'family': 'Arial'}
        },
        height=950,
        width=1900,
        showlegend=False,
        paper_bgcolor="#F9FAFB",
        plot_bgcolor="white",
        font=dict(size=12, family="Arial", color='#374151')
    )
    
    # Ajuster le radar (row 1, col 4)
    fig.update_polars(
        radialaxis=dict(
            range=[0, 100],
            showticklabels=True,
            tickfont=dict(size=10, color='#6B7280'),
            gridcolor='#E5E7EB'
        ),
        bgcolor="rgba(249, 250, 251, 0.5)",
        row=1, col=4
    )
    
    # Ajuster le bar chart (row 2, col 2)
    fig.update_xaxes(
        tickfont=dict(size=11, color='#374151'),
        row=2, col=2
    )
    fig.update_yaxes(
        range=[0, 110],
        title_text="Score (%)",
        title_font=dict(size=11, color='#374151'),
        tickfont=dict(size=10, color='#6B7280'),
        showgrid=True,
        gridcolor='#E5E7EB',
        row=2, col=2
    )
    
    # Sauvegarder et afficher
    fig.write_html("nyota_dashboard_complet.html")
    print("✅ Dashboard sauvegardé : nyota_dashboard_complet.html")
    
    fig.show()


# ============================================
# FONCTION PRINCIPALE
# ============================================

def generate_nyota_report(json_file: str, save_diagram: str = None):
    """
    Génère le rapport NYOTA complet à partir d'un fichier JSON.
    ORDRE : Kiviat → Dashboard → Rapport écrit (console + TXT + HTML)
    """
    
    print("=" * 80)
    print("🔍 NYOTA PERSONALITY - ANALYSE EN COURS")
    print("=" * 80)
    
    # Chargement des réponses
    with open(json_file, 'r', encoding='utf-8') as f:
        responses = json.load(f)
    
    responses = {int(k): v for k, v in responses.items()}
    
    print(f"✅ {len(responses)} réponses chargées")
    
    # Calcul des scores
    scores = compute_all_scores(responses)
    
    # Affichage console des scores
    print("\n📊 SCORES PAR AXE (sur 100)")
    print("-" * 80)
    for axis, score in scores.items():
        bar = "█" * int(score / 5)
        print(f"{axis:.<40} {score:>6.2f} {bar}")
    
    print("\n" + "=" * 80)
    
    # 1️⃣ Génération du diagramme Kiviat (matplotlib)
    print("\n🎨 Étape 1/3 : Génération du diagramme Kiviat...")
    plot_kiviat(scores, save_diagram)
    
    # 2️⃣ Génération du dashboard unifié Plotly
    print("\n📊 Étape 2/3 : Génération du dashboard interactif...")
    create_unified_dashboard(scores)
    
    # 3️⃣ Génération du rapport écrit
    print("\n📝 Étape 3/3 : Génération du rapport écrit...\n")
    
    # Rapport console
    written_report = generate_written_report(scores)
    print(written_report)
    
    # Sauvegarder le rapport texte
    with open("nyota_rapport_ecrit.txt", "w", encoding="utf-8") as f:
        f.write(written_report)
    print("✅ Rapport texte sauvegardé : nyota_rapport_ecrit.txt")
    
    # ✨✨✨ NOUVEAU : Générer le rapport HTML ✨✨✨
    html_report = generate_html_report(scores)
    with open("nyota_rapport_complet.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("✅ Rapport HTML sauvegardé : nyota_rapport_complet.html")
    
    # Ouvrir automatiquement le rapport HTML dans le navigateur
    webbrowser.open("nyota_rapport_complet.html")
    print("🌐 Rapport HTML ouvert dans le navigateur")
    
    return scores


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    
    scores = generate_nyota_report(
        json_file="reponse_per1.json",
        save_diagram="nyota_profile.png"
    )
    
    print("\n" + "="*80)
    print("✅ ANALYSE NYOTA TERMINÉE AVEC SUCCÈS !")
    print("="*80)
    print("\n📁 Fichiers générés :")
    print("   1. nyota_profile.png - Diagramme Kiviat")
    print("   2. nyota_dashboard_complet.html - Dashboard interactif")
    print("   3. nyota_rapport_ecrit.txt - Rapport texte")
    print("   4. nyota_rapport_complet.html - Rapport HTML élégant")
    print("\n🎯 Ordre de consultation recommandé :")
    print("   1️⃣  Diagramme Kiviat (vue d'ensemble)")
    print("   2️⃣  Dashboard (analyse détaillée par axe)")
    print("   3️⃣  Rapport HTML (synthèse et recommandations)")
    print("="*80 + "\n")