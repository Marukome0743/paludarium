#define _GNU_SOURCE
#include <sched.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <signal.h>
#include <string.h>
static int child(void *arg) { (void)arg; return 42; }
int main(int argc, char **argv) {
 if (argc == 2 && !strcmp(argv[1], "ptrace")) {
  errno=0; long r=ptrace(PTRACE_TRACEME,0,0,0); int e=errno;
  printf("ptrace_result=%ld errno=%d message=%s\n",r,e,strerror(e)); return 0;
 }
 if(argc != 3) return 2;
 int mask=atoi(argv[1]), sig=atoi(argv[2]);
 int flags=sig;
 if(mask&1) flags|=CLONE_VM;
 if(mask&2) flags|=CLONE_FS;
 if(mask&4) flags|=CLONE_FILES;
 if(mask&8) flags|=CLONE_UNTRACED;
 void *stack=malloc(1024*1024); if(!stack) return 3;
 errno=0; int pid=clone(child,(char*)stack+1024*1024,flags,0); int e=errno;
 printf("mask=%d signal=%d flags=0x%x clone=%d errno=%d message=%s\n",mask,sig,flags,pid,e,strerror(e)); fflush(stdout);
 if(pid<0) { free(stack); return 0; }
 int status=0; errno=0; int waited=waitpid(pid,&status,sig?0:__WCLONE); e=errno;
 printf("waitpid=%d errno=%d child_exited=%d child_exit=%d child_signal=%d\n",waited,e,WIFEXITED(status),WIFEXITED(status)?WEXITSTATUS(status):-1,WIFSIGNALED(status)?WTERMSIG(status):0);
 free(stack); return waited==pid && WIFEXITED(status) && WEXITSTATUS(status)==42 ? 0:4;
}
