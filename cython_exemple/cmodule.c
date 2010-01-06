/*
 * =====================================================================================
 *
 *       Filename:  cmodule.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  12/26/2009 03:26:10 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  BOYPT (PT), pentie@gmail.com
 *        Company:  http://apt-blog.net
 *
 * =====================================================================================
 */




#include	"cmodule.h"

    void
say_hello ( void )
{
    printf("%s,, %f\n", "hello", sin(30));
}		/* -----  end of function say_hello  ----- */


void show_args (int argc, char *argv[])
{
    printf("There is %d args\n", argc);
    
    int i;
    for (i = 0; i < argc; i++) {
        printf("%s,", argv[i]);
    }
    printf("\n");
}



