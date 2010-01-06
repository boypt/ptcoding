/*
 * =====================================================================================
 *
 *       Filename:  lock.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  12/28/2009 12:21:03 AM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  BOYPT (PT), pentie@gmail.com
 *        Company:  http://apt-blog.net
 *
 * =====================================================================================
 */


#include	<stdio.h>
#include	<stdlib.h>
//#include    <Python.h>

int end = 0;

void
_c_loop ( void )
{
    //Py_BEGIN_ALLOW_THREADS 
    while(!end) {
        printf("Print from C loop\n");
        sleep(1);
    }
    printf("C loop ENDED\n");
    //Py_END_ALLOW_THREADS
}
