/* mds_server.c 
 * MDS Sample Server for unix by Preson M.(BOYPT)<pentie@gmail.com> 
 * Compile with:
 *      gcc -Wall -o mds_server mds_server.c 
 */

#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h> /* memset() */
#include <time.h>

#define LOCAL_SERVER_PORT 19781

#define MAX_MSG 100

void
print_hex(uint8_t *array, int count)
{
    int i;
    for(i = 0; i < count; i++){
        if ( !(i % 16))
            printf ("\n");
        printf("%02x ", array[i]);
    }
    printf("\n");
}


int main(int argc, char *argv[]) {
  
  int sd, rc;
  size_t n;
  socklen_t cliLen;
  struct sockaddr_in cliAddr, servAddr;
  char msg[MAX_MSG];


  char pinbuf[9];
  char response[] = {0x10, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  unsigned long PIN;
  unsigned long *responsePIN = (unsigned long*)(response + 6);
  time_t timep;
  char *time_stamp;

  time (&timep);
  time_stamp = ctime(&timep);
  time_stamp[24] = 0;

  /* socket creation */
  sd=socket(AF_INET, SOCK_DGRAM, 0);
  if(sd<0) {
    printf("[%s] %s: cannot open socket \n",time_stamp, argv[0]);
    exit(1);
  }

  /* bind local server port */
  servAddr.sin_family = AF_INET;
  servAddr.sin_addr.s_addr = htonl(INADDR_ANY);
  servAddr.sin_port = htons(LOCAL_SERVER_PORT);
  rc = bind (sd, (struct sockaddr *) &servAddr,sizeof(servAddr));
  if(rc<0) {
    printf("[%s] %s: cannot bind port number %d \n", 
       time_stamp, argv[0], LOCAL_SERVER_PORT);
    exit(1);
  }

  printf("[%s] %s: waiting for data on port UDP %u\n", 
       time_stamp, argv[0], LOCAL_SERVER_PORT);
  fflush(stdout);


  /* server infinite loop */
  while(1) {
    
    /* init buffer */
    memset(msg,0x0,MAX_MSG);

    /* receive message */
    cliLen = sizeof(cliAddr);
    n = recvfrom(sd, msg, MAX_MSG, 0,
         (struct sockaddr *) &cliAddr, &cliLen);

    time (&timep);
    time_stamp = ctime(&timep);
    time_stamp[24] = 0;

    if(n<0) {
      printf("[%s] %s: cannot receive data \n", time_stamp, argv[0]);
      continue;
    }

    if (n != 18 || msg[0] != 0x10 || msg[1] != 0x08 || (*(int*)(&msg[6])) != 0) {
        printf("[%s] bad data received from %s, len=%zu\n", time_stamp,  inet_ntoa(cliAddr.sin_addr), n);
        print_hex((uint8_t *)msg, n);
        fflush(stdout);
        continue;
    }
    PIN = *(u_long*)(&msg[2]);
    *responsePIN = PIN;
    response[10] = msg[10] - 0x80;
    sendto(sd, (const char *)response, sizeof(response), 0, (struct sockaddr*)&cliAddr, n);

    sprintf(pinbuf, "%x", ntohl(PIN));
    printf("[%s] Request received from %s, PIN=%s ...response sent.\n", time_stamp, inet_ntoa(cliAddr.sin_addr), pinbuf); 
    fflush(stdout);
    
  }/* end of server infinite loop */

return 0;

}


