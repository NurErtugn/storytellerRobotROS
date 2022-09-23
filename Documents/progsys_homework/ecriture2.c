#include <stdio.h>
#include <string.h>
 
/* on affiche les noms sur 15 caractères, comme spécifié dans la donnée */
#define TAILLE_NOM 15
 
int main(void)
{
  char const nom_fichier[] = "data.dat"; /* le nom du fichier */
  FILE* entree;
  int taille_lue;
 
  char nom[TAILLE_NOM+1]; /* la donnée "nom" à lire depuis le fichier */
  unsigned int age;       /* la donnée "age" à lire depuis le fichier */
 
  /* variables nécessaires aux différents calculs */
  unsigned int nb = 0; 
  unsigned int age_max = 0; 
  unsigned int age_min = (unsigned int) -1; /* truc : -1 sera toujours le plus
                                               grand nombre représentable */
  double total = 0.0;
 
  /* ouverture du fichier en lecture (r=read) */
  entree = fopen(nom_fichier, "r");
 
  /* on teste si l'ouverture du flot s'est bien réalisée */
  if (entree == NULL) {
    fprintf(stderr,
            "Erreur: le fichier %s ne peut etre ouvert en lecture !\n",
            nom_fichier);
    return 1; /* retourne autre chose que 0 car ça s'est mal passé */
  }
 
  /* On commence par l'affichage du cadre */
  printf("+-----------------+-----+\n");
 
  /*
   * Et on boucle directement sur la condition de lecture correcte
   * du couple <nom,age> (en fait, sur la condition de lecture correcte
   * de 'age', mais comme il n'est pas possible de lire 'age' si la
   * lecture de 'nom' à échoué...)
   */
 
  do {
    taille_lue = fscanf(entree, "%15s %u", nom, &age);
 
    if (taille_lue == 2) { /* la lecture s'est bien passée */
      ++nb; /* nombre de personnes + 1 */
      total += age; /* pour faire la moyenne plus tard */
      /* on vérifie si l'âge lu est le plus grand/petit lu jusqu'ici  */
      if (age_min > age) age_min = age; /* */
      if (age_max < age) age_max = age; /**/
 
      /* Affichage */
      /* le signe "-" permet d'aligner à gauche */
      printf("| %-15s | %3d |\n", nom, age);
    }
  } while (! feof(entree));
 
  /* Partie finale */
 
  fclose(entree);  /* ne pas oublier de fermer le  fichier ! */
 
  printf("+-----------------+-----+\n");
  printf("  âge minimum     : %3d\n", age_min);
  printf("  âge maximal     : %3d\n", age_max);
 
  printf("%d personnes, âge moyen : %5.1f ans\n", nb, total/nb);
  /* l'âge moyen est sur 5 positions dont un chiffre après la virgule */
 
  return 0;
}
 