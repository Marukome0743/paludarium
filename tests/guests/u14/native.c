#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

/* Native x86-64 observations precede U14 translation. Arithmetic flag masks
 * exclude undefined/reserved bits; MOV/SSE/RET do not define arithmetic flags. */
struct instruction_case {
    const char *name;
    const unsigned char *code;
    size_t size;
    uint64_t input;
    uint64_t flag_mask;
    int mode;
};
static const unsigned char move[] = {0x48,0xb8,0xef,0xcd,0xab,0x89,0x67,0x45,0x23,0x01,0xc3};
static const unsigned char add[] = {0x48,0x83,0xc0,0x01,0xc3};
static const unsigned char sub[] = {0x48,0x83,0xe8,0x01,0xc3};
static const unsigned char jne[] = {0x48,0x83,0xf8,0x07,0x75,0x06,0xb8,0x2a,0x00,0x00,0x00,0xc3,0xb8,0x09,0x00,0x00,0x00,0xc3};
static const unsigned char je[] = {0x48,0x83,0xf8,0x07,0x74,0x06,0xb8,0x2a,0x00,0x00,0x00,0xc3,0xb8,0x09,0x00,0x00,0x00,0xc3};
static const unsigned char memory[] = {0x48,0x89,0x07,0x48,0x83,0x07,0x05,0x48,0x8b,0x07,0xc3};
static const unsigned char fallback[] = {0x66,0x0f,0xef,0xc0,0x66,0x48,0x0f,0x7e,0xc0,0xc3};
static const unsigned char fault[] = {0x48,0x8b,0x07,0xc3};
static const unsigned char divide[] = {0x31,0xd2,0x31,0xc9,0x48,0xf7,0xf1,0xc3};
static const struct instruction_case cases[] = {
    {"move64",move,sizeof(move),0,0,0},
    {"add64-carry",add,sizeof(add),UINT64_MAX,0x8d5,0},
    {"sub64-overflow",sub,sizeof(sub),UINT64_C(0x8000000000000000),0x8d5,0},
    {"jne-zf1-not-taken",jne,sizeof(jne),7,0x8d5,0},
    {"jne-zf0-taken",jne,sizeof(jne),8,0x8d5,0},
    {"je-zf1-taken",je,sizeof(je),7,0x8d5,0},
    {"je-zf0-not-taken",je,sizeof(je),8,0x8d5,0},
    {"memory-read-write",memory,sizeof(memory),11,0x8d5,0},
    {"unsupported-sse-fallback",fallback,sizeof(fallback),17,0,0},
    {"unmapped-data-fault",fault,sizeof(fault),0,0,1},
    {"division-fault",divide,sizeof(divide),1,0,0},
    {"self-modifying-code",move,sizeof(move),0,0,2},
    {"cross-page-instruction",move,sizeof(move),0,0,3},
};

static void observe(const struct instruction_case *item) {
    unsigned char *mapping = mmap(NULL,8192,PROT_READ|PROT_WRITE|PROT_EXEC,
                                  MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    uint64_t *data = mmap(NULL,4096,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if (mapping == MAP_FAILED || data == MAP_FAILED) _exit(110);
    unsigned char *entry = mapping + (item->mode == 3 ? 4093 : 0);
    memcpy(entry,item->code,item->size);
    if (item->mode == 1 && mprotect(data,4096,PROT_NONE)) _exit(111);
    uint64_t value = item->input, flags;
    __asm__ volatile("call *%[entry]; pushfq; pop %[flags]"
        : "+a"(value), [flags]"=r"(flags)
        : [entry]"r"(entry), "D"(data)
        : "rcx","rdx","rsi","r8","r9","r10","r11","xmm0","cc","memory");
    uint64_t first = value;
    if (item->mode == 2) {
        entry[2] = 0x2a;
        memset(entry+3,0,7);
        __asm__ volatile("call *%[entry]" : "+a"(value)
            : [entry]"r"(entry), "D"(data)
            : "rcx","rdx","rsi","r8","r9","r10","r11","xmm0","cc","memory");
    }
    printf("{\"name\":\"%s\",\"rax\":\"%016" PRIx64 "\",\"first_rax\":\"%016" PRIx64
           "\",\"flags\":\"%016" PRIx64 "\",\"flag_mask\":\"%016" PRIx64
           "\",\"memory\":\"%016" PRIx64 "\",\"signal\":0,\"child_exit\":0}\n",
           item->name,value,first,flags & item->flag_mask,item->flag_mask,*data);
    fflush(stdout);
    _exit(0);
}

int main(void) {
    struct rlimit limit = {0,0};
    if (setrlimit(RLIMIT_CORE,&limit)) return 112;
    for (size_t index=0; index<sizeof(cases)/sizeof(cases[0]); index++) {
        pid_t child = fork();
        if (child < 0) return 113;
        if (child == 0) observe(&cases[index]);
        int status;
        if (waitpid(child,&status,0) != child) return 114;
        if (WIFSIGNALED(status)) {
            printf("{\"name\":\"%s\",\"signal\":%d,\"child_exit\":null}\n",cases[index].name,WTERMSIG(status));
            fflush(stdout);
        } else if (!WIFEXITED(status) || WEXITSTATUS(status)) return 115;
    }
    return 0;
}
