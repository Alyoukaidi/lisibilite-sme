#!/usr/bin/env python3
"""
Script d'anonymisation de fichiers SRT/VTT pour audit CPS
Remplace tous les caractères par 'X' tout en préservant la structure
Le résultat CPS est strictement identique au fichier original

Supporte :
- Fichiers .srt et .vtt
- Traitement par batch (plusieurs fichiers à la fois)
- Drag & drop sous Windows
"""
import sys
import os
import re


def convert_vtt_to_srt(vtt_content):
    """
    Convertit le contenu VTT en format SRT
    
    Args:
        vtt_content: contenu du fichier VTT (string)
    
    Returns:
        string: contenu converti en format SRT
    """
    lines = vtt_content.split('\n')
    srt_lines = []
    subtitle_num = 1
    in_subtitle = False
    skip_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Ignorer l'en-tête WEBVTT
        if line.startswith('WEBVTT'):
            i += 1
            continue
        
        # Ignorer les blocs STYLE et NOTE
        if line.startswith('STYLE') or line.startswith('NOTE'):
            skip_block = True
            i += 1
            continue
        
        # Fin de bloc à ignorer
        if skip_block and line == '':
            skip_block = False
            i += 1
            continue
        
        if skip_block:
            i += 1
            continue
        
        # Ligne vide : fin de sous-titre
        if line == '' and in_subtitle:
            srt_lines.append('')
            in_subtitle = False
            i += 1
            continue
        
        # Timecode VTT (peut avoir un identifiant avant)
        if '-->' in line:
            # Ajouter le numéro de séquence
            srt_lines.append(str(subtitle_num))
            subtitle_num += 1
            
            # Convertir le timecode (point → virgule)
            timecode = re.sub(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', r'\1:\2:\3,\4', line)
            # Supprimer les éventuelles infos de positionnement VTT
            timecode = re.sub(r'\s+align:.*$', '', timecode)
            timecode = re.sub(r'\s+position:.*$', '', timecode)
            timecode = re.sub(r'\s+line:.*$', '', timecode)
            srt_lines.append(timecode)
            
            in_subtitle = True
            i += 1
            continue
        
        # Texte du sous-titre
        if in_subtitle and line:
            # Nettoyer les balises VTT
            clean_line = re.sub(r'<v\s+[^>]+>', '', line)  # <v Speaker>
            clean_line = re.sub(r'</v>', '', clean_line)
            clean_line = re.sub(r'<c[^>]*>', '', clean_line)  # <c.classname>
            clean_line = re.sub(r'</c>', '', clean_line)
            srt_lines.append(clean_line)
        
        i += 1
    
    return '\n'.join(srt_lines)


def anonymize_content(content):
    """
    Anonymise le contenu d'un fichier SRT
    
    Args:
        content: contenu du fichier (string)
    
    Returns:
        string: contenu anonymisé
    """
    lines = content.split('\n')
    anonymized_lines = []
    
    for line in lines:
        # Garder les lignes vides
        if line.strip() == '':
            anonymized_lines.append(line)
            continue
        
        # Garder les numéros de sous-titre
        if line.strip().isdigit():
            anonymized_lines.append(line)
            continue
        
        # Garder les timecodes
        if '-->' in line:
            anonymized_lines.append(line)
            continue
        
        # Anonymiser le texte : remplacer chaque caractère par X (sauf espaces)
        anonymized_line = ''.join(
            'X' if c not in (' ', '\n', '\r', '\t') else c 
            for c in line
        )
        anonymized_lines.append(anonymized_line)
    
    return '\n'.join(anonymized_lines)


def anonymize_file(input_file):
    """
    Anonymise un fichier SRT ou VTT
    
    Args:
        input_file: chemin du fichier source
    
    Returns:
        bool: True si succès, False sinon
    """
    if not os.path.exists(input_file):
        print(f"❌ Erreur : le fichier '{input_file}' n'existe pas.")
        return False
    
    # Vérifier l'extension
    _, ext = os.path.splitext(input_file)
    ext = ext.lower()
    
    if ext not in ['.srt', '.vtt']:
        print(f"⚠️  Ignoré : '{input_file}' (format non supporté, .srt ou .vtt uniquement)")
        return False
    
    # Générer le nom du fichier de sortie
    base = os.path.splitext(input_file)[0]
    output_file = f"{base}_ANONYME.srt"
    
    try:
        # Lecture du fichier
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Conversion VTT → SRT si nécessaire
        if ext == '.vtt':
            print(f"🔄 Conversion VTT → SRT : {os.path.basename(input_file)}")
            content = convert_vtt_to_srt(content)
        
        # Anonymisation
        anonymized_content = anonymize_content(content)
        
        # Écriture du fichier anonymisé
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(anonymized_content)
        
        print(f"✅ Fichier anonymisé : {os.path.basename(output_file)}")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement de '{input_file}' : {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Script d'anonymisation SRT/VTT pour audit CPS")
        print("=" * 60)
        print("\n📋 Usage :")
        print("  python anonymize_srt.py fichier1.srt [fichier2.vtt ...]")
        print("\n💡 Exemples :")
        print("  python anonymize_srt.py mon_fichier.srt")
        print("  python anonymize_srt.py fichier1.srt fichier2.vtt fichier3.srt")
        print("\n🖱️  Ou glissez-déposez un ou plusieurs fichiers sur le script")
        print("\n📤 Sortie : fichier_ANONYME.srt")
        print("=" * 60)
        
        # Attendre une entrée pour ne pas fermer la fenêtre
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    input_files = sys.argv[1:]
    
    print("\n" + "=" * 60)
    print(f"🔒 Anonymisation de {len(input_files)} fichier(s)")
    print("=" * 60 + "\n")
    
    success_count = 0
    for input_file in input_files:
        if anonymize_file(input_file):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ {success_count}/{len(input_files)} fichier(s) traité(s) avec succès")
    print("=" * 60 + "\n")
    
    # Attendre une entrée pour ne pas fermer la fenêtre
    input("Appuyez sur Entrée pour quitter...")
    sys.exit(0 if success_count == len(input_files) else 1)


if __name__ == "__main__":
    main()
