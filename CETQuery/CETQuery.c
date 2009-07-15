#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <iconv.h>   

void PANIC(char *msg);
#define PANIC(msg)  {perror(msg); abort();}
int tcp_connect(const char *host, const char *serv);
int code_convert(char *from_charset, char *to_charset,
            char *inbuf, int inlen, char *outbuf, int outlen);
void display_list(char *result, char type, char *id);

int 
main(int argc, char *argv[])
{
    int sockfd, bytes_read;
    char buffer[4096];
    char result[100];
    char *id;

    if(argc != 2 || strlen(argv[1]) != 15) {
        printf("Error: 参数错误，请输入15位准考证号，自动识别考试类型。"
            "\nExample:\n\nCETQuery 123456789012345\n\n"
            "CETQuery-C version 0.3  2009.3.2\n\n    An Exercise Program by PT, GZ University\n    "
            "Author Blog: http://apt-blog.co.cc , Welcome to Drop by.\n\n");
        exit(1);
    }

    id = argv[1];
    char type = (id[9] - 1) ? '6' : '4';

    /* 建立连接socket   */
    sockfd = tcp_connect("cet.99sushe.com", "http");

    /* 准备HTTP头数据 */
    sprintf(buffer, "GET /cetscore_99sushe0902.html?t=%c&id=%s HTTP/1.1\r\nReferer: http://cet.99sushe.com/\r\nHost: cet.99sushe.com\r\n\r\n", type, id);

    /* 发送数据 */
    send(sockfd, buffer, strlen(buffer), 0);

    /* 接收缓存 */
    bzero(buffer, sizeof(buffer));

    /* 接收 */
    bytes_read = recv(sockfd, buffer, sizeof(buffer), 0);

    /* 关闭套接字 */
    close(sockfd);

    /* 错误处理 */
    if ( bytes_read <= 0 ){
        PANIC("MAIN");
        exit(1);
    }
    
    /* 信息头过滤 */
    char *metadata = strstr(buffer,"\r\n\r\n");
    metadata += 4;

    /* 转码缓存 */
    bzero(result, sizeof(result));
    code_convert("gb2312", "utf-8", metadata, strlen(metadata), result, 100);

    /* 输出结果 */
    display_list(result, type, id);

    return 0;
}/* ----------  end of function main  ---------- */

int
tcp_connect(const char *host, const char *serv)
{
    int     sockfd, n;
    struct addrinfo hints, *res, *ressave;
    
    bzero(&hints, sizeof(struct addrinfo));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if( (n = getaddrinfo(host, serv, &hints, &res)) != 0)
        PANIC("tcp_connect");
    ressave = res;

    do {
        sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

        if (sockfd < 0)
          continue;

        if (connect(sockfd, res->ai_addr, res->ai_addrlen) == 0)
          break;
        close(sockfd);
    }while( (res = res->ai_next) != NULL);
    freeaddrinfo(ressave);
    return (sockfd);
}


int code_convert(char *from_charset, char *to_charset,
            char *inbuf, int inlen, char *outbuf, int outlen)
{
    iconv_t cd;
    int rc;
    char **pin = &inbuf;
    char **pout = &outbuf;

    cd = iconv_open(to_charset,from_charset);

    if (cd==0) 
      return -1;
    memset(outbuf,0,outlen);

    if (iconv(cd, pin, &inlen, pout, &outlen)==-1) 
      return -1;
    iconv_close(cd);
    return 0;
}

void display_list(char *result, char type, char *id)
{
    int  count = 0;
    char* token;
    char record[10][20];
    char colum[][10] = {"听力", "阅读", "综合", "写作", "总分", 
        "学校", "姓名", "Prev 1", "Next 1", "Next 2"};

    /* 逗号分割 */
    token = strtok(result, ",");
    while( token != NULL )
    {
         sprintf(record[count++], "%s", token);
         token = strtok( NULL, ",");
    }

    /* 错误处理 */
    if(count > 10)
      PANIC("TOKEN Error!!");

    /* 输出 */
    printf("\n***** CET %c 成绩清单 *****\n"
            "-准考证号: %s\n", type, id);
    for(count = 0; count < 10; count++) {
        printf("-%s: %s\n", colum[count],record[count]);
    }
    printf("**************************\n\n");
}

