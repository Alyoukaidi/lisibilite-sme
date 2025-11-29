#!/usr/bin/env python3
"""
Script d'anonymisation de fichiers SRT pour audit CPS
Remplace tous les caractères par 'X' tout en préservant la structure
Le résultat CPS est strictement identique au fichier original
"""

import sys
import os

def anonymize_srt(input_file, output_file=None):
    """
    Anonymise un fichier SRT en remplaçant les caractères par X
    
    Args:
        input_file: chemin du fichier SRT source
        output_file: chemin du fichier SRT anonymisé (optionnel)
    """
    if not os.path.exists(input_file):
        print(f"❌ Erreur : le fichier '{input_file}' n'existe pas.")
        return False
    
    # Générer le nom du fichier de sortie si non fourni
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_anonymise{ext}"
    
    try:
        # Lecture du fichier
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        anonymized_lines = []
        
        for line in lines:
            # Garder les lignes vides
            if line.strip() == '':
                anonymized_lines.append(line)
                continue
            
            # Garder les numéros de sous-titre (lignes contenant uniquement un nombre)
            if line.strip().isdigit():
                anonymized_lines.append(line)
                continue
            
            # Garder les timecodes (lignes contenant '-->')
            if '-->' in line:
                anonymized_lines.append(line)
                continue
            
            # Anonymiser le texte : remplacer chaque caractère par X (sauf espaces et retours à la ligne)
            anonymized_line = ''.join(
                'X' if c not in (' ', '\n', '\r', '\t') else c 
                for c in line
            )
            anonymized_lines.append(anonymized_line)
        
        # Écriture du fichier anonymisé
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(anonymized_lines)
        
        print(f"✅ Fichier anonymisé créé : {output_file}")
        print(f"   Original : {input_file}")
        print(f"   Taille : {len(lines)} lignes")
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de l'anonymisation : {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage : python anonymize_srt.py fichier.srt [fichier_sortie.srt]")
        print("\nExemple :")
        print("  python anonymize_srt.py mon_fichier.srt")
        print("  python anonymize_srt.py mon_fichier.srt fichier_anonyme.srt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = anonymize_srt(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
