
double demander_nombre();
int main(void){
    double val1=1.;
    double val2=2.;
    double val3=3.;
    demander_nombre();
    
    double* choix=NULL;
    switch (demander_nombre(1,3))
    {
    case /* constant-expression */:
        /* code */
        break;
    
    default:
        break;
    }




    return 0;
}

int demander_nombre(int a, int b){
    int res =0.;    
    do{
        printf("demander un nombre entre %d et %d ", &a,&b);
        scanf("%lf", res);
    }while( (res<1) || (res>3) );
    return res;
}