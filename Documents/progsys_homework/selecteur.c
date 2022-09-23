

int main(void) {



double* choix = NULL; /* On initialise le pointeur sur NULLe part */
switch (demander_nombre(1,3)) {
case 1: choix = &valeur1; /* la valeur de choix est l'adresse de valeur1 */
break;
case 2: choix = &valeur2; /* la valeur de choix est l'adresse de valeur2 */
break;
case 3: choix = &valeur3; /* la valeur de choix est l'adresse de valeur3 */
break;
}
printf("Vous avez choisi %f\n",*choix);
