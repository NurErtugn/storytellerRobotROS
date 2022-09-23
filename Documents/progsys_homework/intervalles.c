// This file requires at least C99 to compile

/**
 * @file   intervalles.c
 * @author Nur Ertug <nur.ertug@epfl.ch>
 *
 * @copyright EPFL March 2022
 **/
/**
 * @section DESCRIPTION
 *
 * Template du homework du cours CS-207, année 2022.
 **/

#include <stdio.h>
#include <stdlib.h> // EXIT_SUCCESS/FAILURE
#include <stdbool.h>
#include <math.h>
/**
 * @brief seuil à partir duquel deux doubles sont considérés comme égaux
 */
#define DBL_EPSILON 1e-10

// ----------------------------------------------------------------------
/**
 * @brief Type pour décrire un intervalle
 */
typedef struct
{
    double start;
    double end;
    bool b_start;
    bool b_end;
} Interval;
// ----------------------------------------------------------------------
#define MAX_INTERVALS 25

/**
 * @brief Type pour décrire une réunion d'intervalles
 */
typedef struct
{
    int size;
    Interval intervals[MAX_INTERVALS];

} Interval_union;
//-------------------------------------------------------------------
//---------------------LES PROTOTYPES--------------------------------
void print_interval(const Interval *intrv);
void print_union(const Interval_union *intervals);
bool are_equal(double x, double y);
bool is_empty(const Interval *intrv);
bool contains(const Interval *intrv, double valeur);
bool can_be_joined(const Interval *intrv1, const Interval *intrv2);
Interval join(const Interval *intrv1, const Interval *intrv2);
Interval_union remove_interval(Interval_union ints, int i);
int add(Interval_union *ints, const Interval *intrv);
Interval_union merge(Interval_union lhs, Interval_union rhs);
// ----------------------------------------------------------------------
/**
 * @brief Affiche un intervalle
 *
 * @param intrv l'intervalle à afficher
 */
void print_interval(const Interval *intrv)
{
    if (is_empty(intrv))
    {
        printf("VIDE");
    }
    else
    {
        char bound_start = intrv->b_start ? '[' : ']';
        char bound_end = intrv->b_end ? ']' : '[';
        printf("%c%g%s %g%c", bound_start, intrv->start, ",", intrv->end, bound_end);
    }
}

// ----------------------------------------------------------------------
/**
 * @brief Affiche une réunion d'intervalles
 *
 * @param ints la réunion d'intervalles à afficher
 */

void print_union(const Interval_union *ints)
{
    if (ints->size)
    {
        for (int i = 0; i < ints->size; ++i)
        {
            print_interval(&ints->intervals[i]);
            if ((ints->size != 1) && (i != ints->size - 1))
            {
                printf(" U ");
            }
        }
    }
    else
    {
        printf("REUNION VIDE");
    }
}

// ----------------------------------------------------------------------
/**
 * @brief Teste si deux valeurs double sont égales à DBL_EPSILON près
 *
 * @param x première valeur à comparer
 * @param y seconde valeur à comparer
 * @return true x et y sont à moins de DBL_EPSILON
 */
bool are_equal(double x, double y) { return fabs(x - y) < DBL_EPSILON; }

// ----------------------------------------------------------------------
/**
 * @brief Teste si un intervalle est vide
 *
 * @param intrv l'intervalle à tester
 * @return true si l'intervalle est vide et false sinonx
 */
// Prototypez (ou définissez) ici la fonction is_empty() -- et supprimez ce commentaire

bool is_empty(const Interval *intrv)
{
    bool inf = intrv->end < intrv->start;
    bool eql = (are_equal(intrv->end, intrv->start)) && ((intrv->b_end == false) && (intrv->b_start == false));
    return (inf || eql) ? true : false;
}

// ----------------------------------------------------------------------
/**
 * @brief Teste si un intervalle contient une valeur
 *
 * @param intrv l'intervalle concerné
 * @param valeur la valeur à tester
 * @return true x est contenu dans l'intervalle
 */
bool contains(const Interval *intrv, double valeur)
{
    bool res = false;
    if (!is_empty(intrv))
    {
        if (intrv->b_start)
        {
            res = intrv->b_end ? ((valeur >= intrv->start && valeur <= intrv->end) ? true : false) : ((valeur >= intrv->start && valeur < intrv->end) ? true : false);
        }
        else
        {
            res = intrv->b_end ? ((valeur > intrv->start && valeur <= intrv->end) ? true : false) : ((valeur > intrv->start && valeur < intrv->end) ? true : false);
        }
    }
    return res;
}

// ----------------------------------------------------------------------
/**
 * @brief Teste si deux intervalles peuvent être fusionnés
 *
 * @param intrv1 le premier intervalle à tester
 * @param intrv2 le second  intervalle à tester
 * @return true les deux intervalles peuvent être fusionnés
 */
bool can_be_joined(const Interval *intrv1, const Interval *intrv2)
{
    bool res = true;
    if (is_empty(intrv1) || is_empty(intrv2))
    {
        return true;
    }
    if (contains(intrv1, intrv2->start) || contains(intrv1, intrv2->end) || contains(intrv2, intrv1->start) ||
        contains(intrv2, intrv1->end))
    {
        res = true;
    }
    else
    {
        res = false;
    }
    return res;
}

// ----------------------------------------------------------------------
/**
 * @brief Fusionne deux intervalles
 *
 * @param intrv1 le premier intervalle à fusionner
 * @param intrv2 le second  intervalle à fusionner
 * @return le nouvel intervalle, fusion de interv1 et intrv2
 */
Interval join(const Interval *intrv1, const Interval *intrv2)
{
    Interval i_new = {0, 0, true, true};
    if (!can_be_joined(intrv1, intrv2))
    {
        i_new.start = intrv1->start;
        i_new.end = intrv1->end;
        i_new.b_start = intrv1->b_start;
        i_new.b_end = intrv1->end;
    }
    else
    {
        i_new.start = fmin(intrv1->start, intrv2->start);
        i_new.end = fmax(intrv1->end, intrv2->end);
        i_new.b_start = i_new.start == intrv1->start ? intrv1->b_start : intrv2->b_start;
        i_new.b_end = i_new.end == intrv1->end ? intrv1->b_end : intrv2->b_end;
    }
    return i_new;
}
// ----------------------------------------------------------------------
/**
 * @brief Supprime le i-ième intervalle de la réunion
 *
 * @param ints la réunion d'intervalles
 * @param i l'index de l'intervalle à supprimer
 */
Interval_union remove_interval(Interval_union ints, int i)
{
    if (i < 0 || i >= ints.size)
    {
        return ints;
    }
    else
    {
        for (int k = i; k < ints.size; k++)
        {
            ints.intervals[k] = ints.intervals[k + 1];
        }
        ints.size--;
    }
}

// ----------------------------------------------------------------------
/**
 * @brief Ajoute un intervalle à une réunion
 *
 * @param ints la réunion d'intervalles
 * @param intrv l'intervalle à ajouter
 * @return un code d'erreur strictement positif si l'ajout n'a pas pu se faire ;
 *         et 0 si l'ajout s'est fait correctement
 */
int add(Interval_union *ints, const Interval *intrv)
{
    if (is_empty(intrv))
    {
        return 1;
    }
    else
    {
        int source = -1;
        int tab[ints->size];
        int r = 0;
        int check = 0;
        for (int k = 0; k < ints->size; ++k)
        {
            if (can_be_joined(&ints->intervals[k], intrv))
            {
                tab[r] = k;
                ++r;
                check += 1;
                ints->intervals[k] = join(&ints->intervals[k], intrv);
            }
        }
        if (check == 0)
        {
            (ints->intervals[ints->size]).start = intrv->start;
            (ints->intervals[ints->size]).end = intrv->end;
            (ints->intervals[ints->size]).b_start = intrv->b_start;
            (ints->intervals[ints->size]).b_end = intrv->b_end;
            ++ints->size;
            source = -1;
            return 0;
        }
        int b = 1;
        source = tab[0];
        while (b + source < ints->size)
        {
            if (can_be_joined(&(ints->intervals)[source], &(ints->intervals)[source + b]))
            {
                ints->intervals[source] = join(&(ints->intervals[source]), &(ints->intervals[source + b]));
                remove_interval(*ints, source + b);
                b++;
            }
            else
            {
                b++;
            }
        }
    }
}

// ----------------------------------------------------------------------
/**
 * @brief Ajoute une réunion d'intervalles à une autre réunion d'intervalles
 *
 * @param lhs la première réunion d'intervalles à fusionner ;
 *            elle est modifiée et reçoit les intervalles de la
 *            seconde réunion d'intervalles qu'elle n'a pas déjà
 *
 * @param rhs la réunion d'intervalles à ajouter à la première
 *
 * @return un code d'erreur strictement positif si la fusion n'a pas pu se faire totalement ;
 *         et 0 si elle s'est faite correctement
 */
// Prototypez (ou définissez) ici la fonction merge() -- et supprimez ce commentaire
Interval_union merge(Interval_union lhs, Interval_union rhs)
{
    int TAILLE_1 = lhs.size;
    int TAILLE_2 = rhs.size;
    int TAILLE_12 = TAILLE_1 + TAILLE_2;

    size_t k = 0;
    if (TAILLE_1 < MAX_INTERVALS)
    {
        if (TAILLE_12 >= MAX_INTERVALS)
        {
            for (int t = TAILLE_1; t < MAX_INTERVALS; ++t)
            {
                lhs.intervals[t] = rhs.intervals[k];
                ++k;
                ++TAILLE_1;
            }
        }
        else
        {

            for (int t = TAILLE_1; t < TAILLE_12; ++t)
            {
                lhs.intervals[t] = rhs.intervals[k];
                ++k;
                ++TAILLE_1;
            }
        }
    }
    return lhs;
}

/* ======================================================================
 * CODE FOURNI
 */

// ======================================================================
#define println_bool(x)            \
    do                             \
    {                              \
        puts(x ? "vrai" : "faux"); \
    } while (0)

// ======================================================================
void test_is_empty(const Interval *p_intrv)
{
    if (p_intrv == NULL)
        return;

    print_interval(p_intrv);
    printf(" est vide ? --> ");
    println_bool(is_empty(p_intrv));
}

// ======================================================================
void test_contains(const Interval *p_intrv, double x)
{
    if (p_intrv == NULL)
        return;

    print_interval(p_intrv);
    printf(" contient %g ? --> ", x);
    println_bool(contains(p_intrv, x));
}

// ======================================================================
void test_can_be_joined(const Interval *p_intrv1, const Interval *p_intrv2)
{
    if ((p_intrv1 == NULL) || (p_intrv2 == NULL))
        return;

    printf("Peut-on joindre ");
    print_interval(p_intrv1);
    printf(" et ");
    print_interval(p_intrv2);
    printf(" ? --> ");
    println_bool(can_be_joined(p_intrv1, p_intrv2));
}

// ======================================================================
void test_join(const Interval *p_intrv1, const Interval *p_intrv2)
{
    if ((p_intrv1 == NULL) || (p_intrv2 == NULL))
        return;

    if (!can_be_joined(p_intrv1, p_intrv2))
    {
        puts("TEST (join) INVALIDE :");
        print_interval(p_intrv1);
        printf(" et ");
        print_interval(p_intrv2);
        puts(" ne peuvent pas être joints ==> undefined behaviour !");
        return;
    }

    printf("La fusion de ");
    print_interval(p_intrv1);
    printf(" et ");
    print_interval(p_intrv2);
    printf(" donne ");
    const Interval new = join(p_intrv1, p_intrv2);
    print_interval(&new);
    putchar('\n');
}

#define SIZE(T) (sizeof(T) / sizeof((T)[0]))

// ======================================================================
int main()
{

    const double bound = DBL_EPSILON / 100.0;
    const Interval tests[] = {
        {0.0, 4.0, true, true},
        {2.0, 6.0, true, true},
        {4.0, 6.0, true, true},
        {0.0, 4.0, true, false},
        {5.0, 6.0, true, true},
        {4.0, 4.0, false, false},            // intervalle vide
        {bound, 10.0 * bound, false, false}, // aussi intervalle vide, à la précision près
    };

    // test d'affichage
    for (size_t i = 0; i < SIZE(tests); ++i)
    {
        printf("%zu) ", i + 1);
        print_interval(tests + i);
        putchar('\n');
    }
    puts("--------------------");

    // test de is_empty
    test_is_empty(tests + 4);
    test_is_empty(tests + 5);
    test_is_empty(tests + 6);
    puts("--------------------");

    // test de contains
    test_contains(tests, 0.0);
    test_contains(tests, 2.0);
    test_contains(tests, 4.0);
    test_contains(tests + 3, 4.0);
    test_contains(tests + 6, bound);
    test_contains(tests + 6, 5.0 * bound);
    puts("--------------------");

    // test de can_be_joined
    test_can_be_joined(tests, tests + 1);
    test_can_be_joined(tests + 2, tests + 3);
    test_can_be_joined(tests, tests + 4);
    puts("--------------------");

    // test de join
    test_join(tests, tests + 1);
    test_join(tests + 2, tests + 3);
    test_join(tests + 3, tests + 5);
    puts("--------------------");

    // tests de réunions d'intervalles
    const Interval more_tests[] = {
        {0.0, 3.0, true, true},
        {5.0, 7.0, true, true},
        {8.0, 9.0, true, true},
        {-5.0, -3.0, true, true},
        {10.0, 15.0, true, true},
        {1.0, 11.0, true, true},
        {-6.0, -4.0, true, true},
        {-3.0, -2.0, true, true},
        {100.0, 150.0, true, true},
        {120.0, 130.0, true, true},
        {200.0, 300.0, true, true},
        {140.0, 200.0, true, true}};
    Interval_union ints = {.size = 0};
    for (size_t i = 0; i < SIZE(more_tests); ++i)
    {
        add(&ints, more_tests + i);
    }

    printf("Réunion d'intervalles 1 : ");
    print_union(&ints);
    putchar('\n');

    // Vide la réunion d'intervalles
    ints.size = 0;

    const Interval even_more_tests[] = {
        {0.0, 3.0, true, false},
        {3.0, 4.0, false, false},
        {4.0, 4.0, true, true},
        {4.0, 5.0, false, false},
        {5.0, 5.0, false, false}};
    for (size_t i = 0; i < SIZE(even_more_tests); ++i)
    {
        add(&ints, even_more_tests + i);
    }

    printf("Réunion d'intervalles 2 : ");
    print_union(&ints);
    putchar('\n');
    puts("Fin.");
    return EXIT_SUCCESS;
}