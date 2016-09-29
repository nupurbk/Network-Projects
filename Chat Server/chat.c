#include <stdio.h> /* for printf() and fprintf() */
#include <sys/socket.h> /* for socket(), bind(), and connect() */
#include <arpa/inet.h> /* for sockaddr_in and inet_ntoa() */
#include <stdlib.h> /* for atoi() */
#include <string.h> /* for memset() */
#include <unistd.h> /* for close() */
#include <netdb.h>

#define RCVBUFSIZE 140 /* Size of receive buffer */
#define MAXPENDING 5 /* Maximum outstanding connection requests */
#define CLADDR_LEN 100

void DieWithError(char *errorMessage); /* Error handling function */


void HandleTCPClient(int clntSocket)
 {
 	
	char Buffer[140]; /* Buffer for echo string */
 	int recvMsgSize; /* Size of received message */
	int maxlen=140;
	
	while(1)
	{
	/* Receive message from client */
		
 		if ((recvMsgSize = recv(clntSocket, Buffer, 140, 0)) < 0)
 			DieWithError("recv() failed") ;

		if(recvMsgSize>=140)
			DieWithError("Error : Input too long") ;
		else
		{
				Buffer[recvMsgSize]='\0';
				printf("Friend: %s\n",Buffer);
		}
	
	/* Send received string and receive again until end of transmission */
		printf("\nYou:");
		fgets(Buffer,maxlen-1,stdin);
		if(recvMsgSize>=140)
			DieWithError("Error : Input too long") ;
		else
		{
			recvMsgSize = strlen(Buffer) ;
 		// Echo message back to client 
 			if (send(clntSocket, Buffer, recvMsgSize, 0) != recvMsgSize)
			{
 				DieWithError("send() failed"); 
			
			}
		}
		
	}
	
}

//main function
int main(int argc , char *argv[])
{
	if(argc==1)
	{
		int servSock; /* Socket descriptor for server */
		int clntSock; /* Socket descriptor for client */
		struct sockaddr_in ServAddr;/* Local address */
		struct sockaddr_in *h;
		struct sockaddr_in ClntAddr; /* Client address */
		struct in_addr ia;
		unsigned short ServPort; /* Server port */
		unsigned int clntLen; /* Length of client address data structure */
		char serveraddr[CLADDR_LEN];
		char ip[100];

		//for getting ip of server
		struct addrinfo hints;
		struct addrinfo	*res,*p;
		int status;

		char hostname[1024];
		hostname[1023] = '\0';
		

		
		//assign port to 0
		ServPort = 0; /* First arg: local port */

		/* Create socket for incoming connections */
		if ((servSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
			DieWithError( "socket () failed") ;/* TCP client handling function */

 

		/* Construct local address structure */
		memset(&ServAddr, 0, sizeof(ServAddr)); /* Zero out structure */
		ServAddr.sin_family = AF_INET; /* Internet address family */
		ServAddr.sin_addr.s_addr = htonl(INADDR_ANY); /* Any incoming interface */ 
		ServAddr.sin_port = htons(ServPort); /* Local port */ 

		/* Bind to the local address */
		if (bind(servSock, (struct sockaddr *)&ServAddr, sizeof(ServAddr)) < 0)
			DieWithError( "bind () failed");

		

		
		printf("\nWelcome to chat!\n");
		printf("\nWaiting for connection on");

		//Ip address of server
		gethostname(hostname, 1023);
		
		memset(&hints,0,sizeof hints);
		hints.ai_family=AF_UNSPEC;
		hints.ai_socktype=SOCK_STREAM;



		if((status=getaddrinfo(hostname,NULL,&hints,&res))!=0)
		{
			fprintf(stderr,"getaddrinfo :%s\n",gai_strerror(status));
			return 2;
		}

		for(p = res; p != NULL; p = p->ai_next) 
		{
			h = (struct sockaddr_in *) p->ai_addr;
			strcpy(ip , inet_ntoa( h->sin_addr ) );
        }

		printf("\n %s" , ip);
     
		//port no
		socklen_t len = sizeof(ServAddr);
		if(getsockname(servSock, (struct sockaddr *)&ServAddr,&len)==-1)
			DieWithError( "getsockname");
		else
			printf("\t Port number= %d\n",ntohs(ServAddr.sin_port));



		/* Mark the socket so it will listen for incoming connections */
		if (listen(servSock, MAXPENDING) < 0)
			DieWithError("listen() failed") ;

 
		for (;;) /* Run forever */ //Why forever?
		{
			//printf("\nentering in for loop...");
			/* Set the size of the in-out parameter */
			clntLen = sizeof(ClntAddr);

			/* Wait for a client to connect */
			if ((clntSock = accept(servSock, (struct sockaddr *) &ClntAddr, &clntLen)) < 0) 
					DieWithError("accept() failed");
			/* clntSock is connected to a client! */

			printf("\nFound a friend  ! You recieve First !!!!");	
			printf("Handling client %s\n\n", inet_ntoa(ClntAddr.sin_addr)); //convert to string
			HandleTCPClient (clntSock) ;
	//
		}
		close(clntSock);
			
	}
	else
	{
		int sock; /* Socket descriptor */
		struct sockaddr_in ServAddr; /* Echo server address */
		unsigned short ServPort; /* Echo server port */
		char *servIP;
		char *ch;
		char message[140] ; /* String to send to echo server */
		
		unsigned int StringLen; /* Length of string to echo */
		int bytesRcvd, totalBytesRcvd; 

		if ((argc< 5) && (argc> 5)) /* Test for correct number of arguments */
		{
			fprintf(stderr, "Usage: %s SERVER IP [<Echo Port>]\n",argv[0]);
			exit(1);
		}
		
		 
	

		 if(strcmp(argv[1],"p")==0 && strcmp(argv[3],"s")==0)
		 {
					printf("Port and Server");
					servIP = argv[4];
					ServPort=atoi(argv[2]);
		 }
		 else if(strcmp(argv[1],"s")==0 && strcmp(argv[3],"p")==0)
		 {
					printf("Server and Port");
					servIP = argv[2];
					ServPort=atoi(argv[4]);	
		 }
		 else if(strcmp(argv[1],"h")==0)
		 {
			 printf("Help :  s is server ip and p denotes port............so while running client argument are \n");
			 printf("file name,port no and server ip or server name and port no...take port no given by server");
		 }
					
		 


					
		/* Create a reliable, stream socket using TCP */
		if ((sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
			DieWithError(" socket () failed") ;

		/* Construct the server address structure */
		memset(&ServAddr, 0, sizeof(ServAddr)); /* Zero out structure */

		ServAddr.sin_family = AF_INET; /* Internet address family */
		ServAddr.sin_addr.s_addr = inet_addr(servIP); /* Server IP address */ 
		ServAddr.sin_port = htons(ServPort); 
	
		printf("\nConnecting to Server   \n ");

	
		/* Establish the connection to the echo server */
		if (connect(sock, (struct sockaddr *) &ServAddr, sizeof(ServAddr)) < 0)
 			DieWithError(" connect () failed") ;
		
		printf("\n Connected !");

		printf("\n\nConnected to a friend!You send First\n");
	
		memset(message,0,140);
	
		while(1)
		{
		
			printf("\nYou :"); 
			fgets(message,RCVBUFSIZE-1,stdin);
			StringLen = strlen(message) ; /* Determine input length */
		
			if(StringLen>=140)
				DieWithError("\nError : Input too long") ;
			else
			{
				if(send(sock, message, StringLen, 0) ==-1) //Why not sending \0
				{
 					DieWithError("send() sent a different number of bytes than expected");
					exit(1);
			
				}
			}


		
			//printf("\nchecking for recieved message\n");
			if((bytesRcvd = recv(sock, message, RCVBUFSIZE - 1, 0)) <= 0)
			{
		 		DieWithError("recv() failed or connection closed prematurely");
				exit(1);
			}
			else
			{
				if(bytesRcvd>=140)
				{
					DieWithError("Er ror : Input too long") ;
				}
				else
				{
					printf("\nFriend:%s",message); /* Print the echo buffer */
					fflush(stdout);
				}
			}
		
		
			printf("\n"); /* Print a final linefeed */
	
		//close(sock);
	}
}
}

void DieWithError(char *errorMessage)
{
	perror(errorMessage);
	exit(1);
}

